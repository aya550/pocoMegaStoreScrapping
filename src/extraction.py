from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

logger = logging.getLogger("scraper.extraction")

CATEGORY_LINK_SELECTOR = 'a[href*="route=product/category"]'


def extract_category_paths(home_html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(home_html, "lxml")
    urls: set[str] = set()
    for a in soup.select(CATEGORY_LINK_SELECTOR):
        href = a.get("href")
        if href:
            urls.add(urljoin(base_url, href))
    return sorted(urls)


def extract_listing_items(listing_html: str, base_url: str) -> list[dict]:
    soup = BeautifulSoup(listing_html, "lxml")
    items = []
    cards = soup.select("div.product-thumb")
    logger.info("Listing : %d carte(s) produit détectée(s)", len(cards))

    for card in cards:
        name_link = card.select_one("h4.title a")
        if name_link is None:
            logger.warning("Carte produit sans lien nom/URL : ignorée (voir HTML brut)")
            continue

        name = name_link.get_text(strip=True) or None
        product_url = urljoin(base_url, name_link.get("href", ""))

        price_el = card.select_one("div.price span.price-new") or card.select_one("div.price span.price")
        price_raw = price_el.get_text(strip=True) if price_el else None

        img = card.select_one("div.image img")
        image_url = None
        if img is not None:
            image_url = img.get("data-src") or img.get("src")
            if image_url:
                image_url = urljoin(base_url, image_url)

        items.append(
            {
                "name": name,
                "price_raw": price_raw,
                "url": product_url,
                "image_url": image_url,
            }
        )

    return items


def extract_pagination_next(listing_html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(listing_html, "lxml")
    pagination = soup.select_one("ul.pagination")
    if pagination is None:
        return None
    for a in pagination.select("a"):
        if a.get_text(strip=True).lower() in (">", "next", "»"):
            href = a.get("href")
            return urljoin(base_url, href) if href else None
    return None


def extract_product_detail(detail_html: str) -> dict:
    soup = BeautifulSoup(detail_html, "lxml")

    availability = None
    for li in soup.select("li"):
        label = li.select_one(".ls-label")
        if label and "availability" in label.get_text(strip=True).lower():
            badge = li.select_one(".badge")
            availability = badge.get_text(strip=True) if badge else li.get_text(strip=True)
            break
    if availability is None:
        logger.warning("Disponibilité introuvable sur la fiche produit (sélecteur peut-être rompu)")

    category = None
    breadcrumb = soup.select_one(".breadcrumb")
    if breadcrumb is not None:
        crumbs = [
            li.get_text(strip=True)
            for li in breadcrumb.select("li")
            if "active" not in li.get("class", [])
        ]
        crumbs = [c for c in crumbs if c]
        if crumbs:
            category = crumbs[-1]

    price_el = soup.select_one("#product .price-new") or soup.select_one("#product .price")
    price_raw = price_el.get_text(strip=True) if price_el else None

    return {
        "availability_raw": availability,
        "category": category,
        "price_raw_detail": price_raw,
    }
