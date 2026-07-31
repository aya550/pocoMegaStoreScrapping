from __future__ import annotations

import argparse
import logging
import sys

import requests

from config import load_config
from export import write_jsonl
from extraction import (
    extract_category_paths,
    extract_listing_items,
    extract_pagination_next,
    extract_product_detail,
)
from http_client import HttpClient, RobotsDisallowedError
from normalize import build_record, deduplicate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("scraper")


def collect(client: HttpClient, base_url: str, max_items: int) -> list[dict]:
    home_response = client.get(base_url)
    category_urls = extract_category_paths(home_response.text, base_url)
    logger.info("%d catégorie(s) trouvée(s) dans le menu", len(category_urls))

    seen_urls: set[str] = set()
    raw_items: list[dict] = []

    for category_url in category_urls:
        if len(raw_items) >= max_items:
            break

        page_url: str | None = category_url
        while page_url and len(raw_items) < max_items:
            try:
                listing_response = client.get(page_url)
            except RobotsDisallowedError as exc:
                logger.warning("Page ignorée (robots.txt) : %s", exc)
                break
            except requests.RequestException as exc:
                logger.error("Échec de récupération de %s : %s — page suivante", page_url, exc)
                break

            page_items = extract_listing_items(listing_response.text, base_url)
            for item in page_items:
                if item["url"] in seen_urls:
                    continue
                seen_urls.add(item["url"])
                raw_items.append(item)
                if len(raw_items) >= max_items:
                    break

            page_url = extract_pagination_next(listing_response.text, base_url)

    logger.info("%d produit(s) vu(s) au total (listing), avant visite des fiches détail", len(raw_items))

    enriched_items = []
    for item in raw_items:
        try:
            detail_response = client.get(item["url"])
        except RobotsDisallowedError as exc:
            logger.warning("Fiche produit ignorée (robots.txt) : %s", exc)
            enriched_items.append(item)
            continue
        except requests.RequestException as exc:
            logger.error("Échec de récupération de la fiche %s : %s — champs détail absents", item["url"], exc)
            enriched_items.append(item)
            continue

        detail_fields = extract_product_detail(detail_response.text)
        enriched_items.append({**item, **detail_fields})

    return enriched_items


def run(max_items: int, delay_seconds: float, output_path: str) -> None:
    config = load_config()
    client = HttpClient(config.base_url, config.user_agent, delay_seconds)

    raw_items = collect(client, config.base_url, max_items)

    records = []
    rejected = 0
    for raw_item in raw_items:
        record = build_record(raw_item)
        if record is None:
            rejected += 1
            continue
        records.append(record)

    unique_records, duplicates = deduplicate(records)
    write_jsonl(unique_records, output_path)

    logger.info(
        "Terminé — vus: %d, acceptés: %d, doublons: %d, rejetés: %d, exportés: %d -> %s",
        len(raw_items), len(records), duplicates, rejected, len(unique_records), output_path,
    )


def parse_args() -> argparse.Namespace:
    config = load_config()
    parser = argparse.ArgumentParser(description="Scraper LambdaTest E-commerce Playground")
    parser.add_argument("--max-items", type=int, default=config.max_items)
    parser.add_argument("--delay", type=float, default=config.request_delay_seconds)
    parser.add_argument("--output", type=str, default=config.output_jsonl_path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        run(max_items=args.max_items, delay_seconds=args.delay, output_path=args.output)
    except RobotsDisallowedError as exc:
        logger.error("Collecte interrompue : %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
