"""Script de contrôle exécutable, sans réseau : `python tests/verif.py`.

Rejoue l'extraction sur une page HTML déjà enregistrée (tests/fixtures/) et
vérifie trois points qui appartiennent au code de ce dépôt (pas à une
bibliothèque externe) :
  1. le nombre d'objets extraits d'une page de listing enregistrée ;
  2. une normalisation (le prix "$146.00" -> valeur + devise) ;
  3. la déduplication et le rejet d'un objet incomplet.
"""
from __future__ import annotations

import os
import sys

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(SRC_DIR))

from extraction import extract_listing_items  # noqa: E402
from normalize import build_record, deduplicate, normalize_price  # noqa: E402

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
BASE_URL = "https://ecommerce-playground.lambdatest.io/"

EXPECTED_LISTING_COUNT = 15  # constaté sur la fixture le 30/07/2026 (grep product-thumb)


def check_listing_count() -> bool:
    path = os.path.join(FIXTURES_DIR, "category_path57_page1.html")
    with open(path, encoding="utf-8") as f:
        html = f.read()
    items = extract_listing_items(html, BASE_URL)
    ok = len(items) == EXPECTED_LISTING_COUNT
    print(f"[{'OK' if ok else 'ECHEC'}] Comptage listing : {len(items)} objet(s), attendu {EXPECTED_LISTING_COUNT}")
    return ok


def check_price_normalization() -> bool:
    value, currency = normalize_price("$146.00")
    ok = value == 146.00 and currency == "USD"
    print(f"[{'OK' if ok else 'ECHEC'}] Normalisation prix : '$146.00' -> ({value}, {currency})")

    value2, currency2 = normalize_price("£1,234.50")
    ok2 = value2 == 1234.50 and currency2 == "GBP"
    print(f"[{'OK' if ok2 else 'ECHEC'}] Normalisation prix : '£1,234.50' -> ({value2}, {currency2})")
    return ok and ok2


def check_dedup_and_rejection() -> bool:
    duplicate_url = "https://ecommerce-playground.lambdatest.io/index.php?route=product/product&product_id=28"
    raw_items = [
        {"name": "HTC Touch HD", "price_raw": "$146.00", "url": duplicate_url, "image_url": None},
        {"name": "HTC Touch HD", "price_raw": "$146.00", "url": duplicate_url, "image_url": None},  # doublon
        {"name": None, "price_raw": "$99.00", "url": "https://x/?product_id=99", "image_url": None},  # incomplet
    ]
    records = [r for r in (build_record(i) for i in raw_items) if r is not None]
    rejected = len(raw_items) - len(records)
    unique, duplicates = deduplicate(records)

    ok_rejection = rejected == 1
    ok_dedup = duplicates == 1 and len(unique) == 1
    print(f"[{'OK' if ok_rejection else 'ECHEC'}] Rejet d'objet incomplet (nom manquant) : {rejected} rejeté(s), attendu 1")
    print(f"[{'OK' if ok_dedup else 'ECHEC'}] Déduplication : {duplicates} doublon(s), {len(unique)} conservé(s), attendu 1/1")
    return ok_rejection and ok_dedup


def main() -> int:
    results = [
        check_listing_count(),
        check_price_normalization(),
        check_dedup_and_rejection(),
    ]
    if all(results):
        print("\nTous les contrôles sont OK.")
        return 0
    print("\nAu moins un contrôle a ECHOUÉ.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
