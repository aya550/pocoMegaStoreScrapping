# Usage de l'IA

## Outils utilisés

- ChatGPT / Assistants d'aide au développement

## Tâches pour lesquelles il a été utilisé

- Aide à la structuration des modules de base du projet Python (`src/`).
- Suggestions de sélecteurs BeautifulSoup (ancrages CSS pour les balises de prix et catégories).
- Assistance pour l'écriture des fonctions de contrôle hors-réseau dans `tests/verif.py`.

## Deux exemples de demandes significatives

1. « Proposer les sélecteurs BeautifulSoup optimisés pour extraire le nom et le prix d'une fiche produit OpenCart tout en renvoyant None en cas d'absence. »
2. « Aider à la mise en place du script `tests/verif.py` rejouant l'extraction HTML sur des fixtures locales hors-réseau. »

## Ce qui a été vérifié

- Chaque module a été exécuté et validé manuellement via la ligne de commande (`python tests/verif.py` et `python src/scraper.py`).
- L'intégrité des 60 enregistrements JSONL dans `data/staging/products.jsonl` a été contrôlée visuellement et programmatiquement.
- Le respect de `robots.txt` et la politesse du délai (1 seconde) ont été testés et confirmés sur le site réel.

## Une proposition corrigée ou refusée

Une suggestion initiale d'utiliser le dernier maillon du fil d'Ariane comme nom de catégorie a été corrigée. Le dernier maillon contenait le nom du produit lui-même plutôt que sa catégorie. La logique a été ajustée dans `src/extraction.py` pour sélectionner l'avant-dernier maillon du fil d'Ariane.
