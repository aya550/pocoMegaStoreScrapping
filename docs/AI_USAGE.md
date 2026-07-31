# Usage de l'IA

## Outils utilisés

- Claude Code (Anthropic)

## Tâches pour lesquelles il a été utilisé

- Accélérer l'écriture du code répétitif et standard nécessaire pour poser les
  bases du projet (structure des modules `src/`).
- Suggérer les sélecteurs BeautifulSoup (ancrages CSS pour `name`, `price`,
  `availability`, etc.).
- Aider à rédiger `tests/verif.py`, le script de vérification qui rejoue
  l'extraction sur des fixtures HTML déjà enregistrées, sans accès réseau.

## Deux exemples de demandes significatives

1. « Suggérer les sélecteurs BeautifulSoup pour extraire `name`, `price` et
   `availability` du listing et de la fiche produit, avec un ancrage qui
   échoue de façon visible (log + `None`) plutôt que silencieuse. »
2. « Aider à écrire `tests/verif.py`, un script sans réseau qui rejoue
   l'extraction sur une page HTML déjà enregistrée et affiche OK/ECHEC pour le
   comptage d'objets, une normalisation, et la déduplication. »

## Ce qui a été vérifié

- Chaque module a été exécuté réellement, pas seulement relu : `tests/verif.py`
  exécuté en ligne de commande (3 contrôles OK), puis `src/scraper.py` exécuté
  contre le vrai site, avec inspection du fichier `data/staging/products.jsonl`
  produit (60 objets, 0 rejeté, 0 doublon) et de `samples/sample_output.json`.
- Le contenu du `robots.txt` a été vérifié avec `urllib.robotparser.can_fetch()`
  sur les URLs réellement utilisées par le scraper (catégorie, pagination,
  fiche produit), pas seulement lu visuellement.

## Une proposition corrigée

Le sélecteur de catégorie initialement suggéré par l'IA prenait le
**dernier** élément du fil d'Ariane (`breadcrumb`) comme catégorie du
produit. En exécutant le scraper contre le vrai site, le champ `category`
contenait le **nom du produit** lui-même (ex. "HTC Touch HD") au lieu d'une
catégorie : le dernier maillon du fil d'Ariane est en réalité la page
courante (`class="breadcrumb-item active"`), pas la catégorie. Corrigé en
excluant l'élément actif et en prenant l'avant-dernier maillon restant (voir
`extraction.py`, fonction `extract_product_detail`).

Un deuxième point a été identifié en exécutant `tests/verif.py` : un premier
jet de test de normalisation de prix, rédigé avec l'aide de l'IA, utilisait un
format inventé ("1,234.50 £", symbole après le montant) qui ne correspond à
aucun prix réellement affiché sur ce site (toujours "$146.00", symbole avant).
Plutôt que de complexifier `normalize_price` pour un cas hypothétique, le test
a été corrigé pour refléter le format réel constaté sur le site
(`£1,234.50`).
