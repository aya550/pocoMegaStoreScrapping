## Membres du groupe

- Aya SGHAIER SLIM
- Danielle Jamila KOAGNE NGANKAM

## Cible et périmètre

- URL de départ : https://ecommerce-playground.lambdatest.io/
- Type : catalogue e-commerce (démo publique OpenCart), rendu HTML côté serveur
- Périmètre : menu catégories → pagination → fiches produit, jusqu'à **60 produits** (plafond configurable, jamais dépassé)
- Détails complets du diagnostic : voir [`TRAME_COMPTE_RENDU.html`](TRAME_COMPTE_RENDU.html)

## Prérequis

- Python 3.10+
- Accès réseau sortant vers `ecommerce-playground.lambdatest.io`

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example .env
```

## Lancement (collecte limitée)

```bash
source .venv/bin/activate
python src/scraper.py --max-items 60 --delay 1
```

Options : `--max-items` (défaut 60), `--delay` (secondes entre requêtes, défaut 1),
`--output` (chemin du JSONL, défaut `data/staging/products.jsonl`).

## Vérification (sans réseau)

```bash
source .venv/bin/activate
python tests/verif.py
```

Rejoue l'extraction sur des pages HTML déjà enregistrées (`tests/fixtures/`) et
affiche `OK`/`ECHEC` pour trois contrôles : nombre d'objets extraits d'une page
de listing, normalisation d'un prix, déduplication + rejet d'un objet incomplet.

## Architecture

Six responsabilités séparées : configuration (`src/config.py`), acquisition
(`src/http_client.py`), extraction (`src/extraction.py`), normalisation/validation
(`src/normalize.py`), export (`src/export.py`), orchestration + journalisation/erreurs
(`src/scraper.py`). Détails et décisions justifiées : [`docs/architecture.md`](docs/architecture.md).

## Format de sortie

Un fichier JSONL (`data/staging/products.jsonl`), une ligne = un objet JSON avec
les champs : `id, name, price, currency, category, url, image_url, availability,
collected_at`. Échantillon de 8 objets réels : [`samples/sample_output.json`](samples/sample_output.json).

## Limites connues

- Le champ `category` reflète le fil d'Ariane de la première catégorie par
  laquelle un produit est rencontré, pas une taxonomie canonique unique par
  produit (voir `docs/architecture.md`) : ce site OpenCart peut afficher une
  catégorie différente pour un même produit selon le chemin de navigation.
- La déduplication et l'identifiant stable reposent sur le paramètre `product_id`
  de l'URL : une réorganisation des URLs par le site casserait cette règle.
- Aucun mécanisme de reprise sur incident (checkpoint) : une interruption oblige
  à relancer la collecte depuis le début.

## Règles d'usage responsable appliquées

- `robots.txt` vérifié programmatiquement (`urllib.robotparser`) avant chaque
  requête, pas seulement lu — voir constat détaillé dans `TRAME_COMPTE_RENDU.html`.
- Une requête à la fois, délai configurable entre requêtes (1 s par défaut, aucun
  `Crawl-delay` déclaré par le site).
- Volume plafonné à 60 produits (fiche de cible S17), jamais dépassé.
- Aucune requête `POST` : le panier de démonstration n'est jamais validé.
- Aucun secret ni donnée personnelle commis (`.env` ignoré par git, voir `.gitignore`).

## Usage de l'IA

Voir [`docs/AI_USAGE.md`](docs/AI_USAGE.md).

