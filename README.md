# Scraper — ecommerce-playground.lambdatest.io

## Membres du groupe

- Aya SGHAIER SLIM
- Danielle Jamila KOAGNE NGANKAM

## Site cible

- URL : https://ecommerce-playground.lambdatest.io/
- Type : catalogue e-commerce (démo OpenCart)

## Stack technique

- Python 3
- `requests` pour les requêtes HTTP
- `beautifulsoup4` + `lxml` pour le parsing HTML

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
source .venv/bin/activate
python src/scraper.py
```

## Structure du projet

```
.
├── src/
│   └── scraper.py       # script principal de collecte
├── data/
│   ├── raw/              # réponses brutes (HTML)
│   └── staging/          # données extraites/validées
├── requirements.txt
└── fiche_descriptive.md  # fiche descriptive du site cible
```

## Stratégie de scraping

## Données collectées
