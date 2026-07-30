"""Normalisation et validation des objets produit avant export.

Règle sur les valeurs manquantes : un champ non trouvé dans le HTML vaut `None`
(absent). Une chaîne vide `""` n'est jamais produite par ce module : soit le
champ a une valeur, soit il est `None`. Ça distingue "le site ne l'affiche pas"
de "le site affiche une valeur vide", qui ne se produit pas ici en pratique.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger("scraper.normalize")

CURRENCY_SYMBOLS = {
    "$": "USD",
    "£": "GBP",
    "€": "EUR",
}

REQUIRED_FIELDS = ("name", "price", "url")


def extract_product_id(url: str) -> str | None:
    """Identifiant stable : product_id de l'URL OpenCart (query string).

    Stable car réutilisé par le site lui-même d'une catégorie à l'autre pour un
    même produit (vérifié : un même produit peut apparaître dans plusieurs
    catégories avec la même valeur de product_id). Une réorganisation des URL
    casserait cette règle ; documenté comme limite connue.
    """
    query = parse_qs(urlparse(url).query)
    values = query.get("product_id")
    return values[0] if values else None


def normalize_price(price_raw: str | None) -> tuple[float | None, str | None]:
    """Sépare la valeur numérique et la devise à partir d'un prix affiché ("$146.00")."""
    if not price_raw:
        return None, None

    match = re.search(r"([^\d\s.,]+)?\s*([\d.,]+)", price_raw)
    if not match:
        logger.warning("Prix illisible, non normalisé : %r", price_raw)
        return None, None

    symbol, amount = match.groups()
    amount = amount.replace(",", "")
    try:
        value = round(float(amount), 2)
    except ValueError:
        logger.warning("Montant de prix non convertible : %r", price_raw)
        return None, None

    currency = CURRENCY_SYMBOLS.get(symbol, symbol)
    return value, currency


def normalize_availability(raw: str | None) -> str | None:
    """Normalise le texte de disponibilité vers un vocabulaire restreint."""
    if not raw:
        return None
    text = raw.strip().lower()
    if "out" in text and "stock" in text:
        return "out_of_stock"
    if "in" in text and "stock" in text:
        return "in_stock"
    if "pre-order" in text or "preorder" in text:
        return "preorder"
    return text.replace(" ", "_")


def normalize_text(raw: str | None) -> str | None:
    if raw is None:
        return None
    cleaned = re.sub(r"\s+", " ", raw).strip()
    return cleaned or None


def build_record(raw_item: dict, collected_at: datetime | None = None) -> dict | None:
    """Construit un enregistrement normalisé à partir d'un item brut fusionné
    (listing + détail). Retourne None si un champ obligatoire manque."""
    collected_at = collected_at or datetime.now(timezone.utc)

    product_id = extract_product_id(raw_item.get("url", ""))
    name = normalize_text(raw_item.get("name"))
    price, currency = normalize_price(raw_item.get("price_raw_detail") or raw_item.get("price_raw"))
    category = normalize_text(raw_item.get("category"))
    availability = normalize_availability(raw_item.get("availability_raw"))

    record = {
        "id": product_id,
        "name": name,
        "price": price,
        "currency": currency,
        "category": category,
        "url": raw_item.get("url"),
        "image_url": raw_item.get("image_url"),
        "availability": availability,
        "collected_at": collected_at.isoformat(),
    }

    missing_required = [f for f in REQUIRED_FIELDS if not record.get(f)]
    if missing_required:
        logger.warning(
            "Objet rejeté (champs obligatoires manquants: %s) : %s",
            ", ".join(missing_required), record.get("url"),
        )
        return None

    return record


def deduplicate(records: list[dict]) -> tuple[list[dict], int]:
    """Déduplique sur `id` (à défaut, sur `url`). Conserve la première occurrence.

    Un même produit apparaît souvent dans plusieurs catégories du site : la
    déduplication sur l'identifiant produit évite de l'exporter en double.
    """
    seen: set[str] = set()
    unique: list[dict] = []
    duplicates = 0
    for record in records:
        key = record.get("id") or record.get("url")
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        unique.append(record)
    return unique, duplicates
