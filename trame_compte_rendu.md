# Fiche descriptive — Site cible

## Identité du site

- **Nom** : LambdaTest E-commerce Playground
- **URL** : https://ecommerce-playground.lambdatest.io/
- **Type de site** : catalogue e-commerce (démo publique basée sur OpenCart)
- **Objectif du site** : bac à sable public destiné aux tests d'automatisation et de scraping

## Analyse technique

- **Rendu** : HTML/SSR — par comparaison directe entre `curl` (réponse HTTP brute) et l'inspecteur du navigateur sur `index.php?route=product/category&path=57` : les 15 fiches produit (nom, prix, image, lien) de la page 1 sont identiques dans les deux, avant toute exécution de JavaScript. Aucun rendu client requis pour les données ciblées.
- **Pagination** : liens `<a>` dans `ul.pagination`, URL de la forme `...&path=<id>&page=<n>`. Suivie via le lien "suivant" trouvé dans le HTML (pas par construction manuelle des numéros de page), voir `extraction.extract_pagination_next`.
- **Authentification requise** : non (catalogue public).
- **robots.txt réel (constaté le 30/07/2026)** :
  ```
  Disallow: /*?page=$   /*&page=$
  Disallow: /*?sort=    /*&sort=
  Disallow: /*?order=   /*&order=
  Disallow: /*?limit=   /*&limit=
  Disallow: /*?filter_name=          /*&filter_name=
  Disallow: /*?filter_sub_category=  /*&filter_sub_category=
  Disallow: /*?filter_description=   /*&filter_description=
  ```
  Le `$` ancre la fin d'URL juste après le paramètre : ces règles interdisent une valeur de paramètre **vide** (ex. `?page=` sans numéro), pas la pagination normale. Vérifié programmatiquement avec `urllib.robotparser` : `can_fetch()` retourne `True` pour `...&path=57`, `...&path=57&page=2` et pour une fiche produit `...&product_id=28`. Aucun `Crawl-delay` déclaré (`crawl_delay()` renvoie `None`) — le scraper applique quand même un délai par défaut de 1 s entre requêtes (`REQUEST_DELAY_SECONDS`, configurable).
- **Structure des pages produit / listing** : voir le détail des sélecteurs et leur justification dans `docs/architecture.md` et les commentaires de `src/extraction.py` (`div.product-thumb`, `h4.title a`, `div.price span.price-new`, `li` contenant le libellé "Availability:").
- **Panier de démonstration** : jamais soumis par ce scraper — aucune requête `POST` n'est envoyée, seules des requêtes `GET` sur des pages publiques (catégorie, pagination, fiche produit).

## Données ciblées

| Champ             | Description                                                                                                                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nom produit       | `h4.title a` sur le listing (texte du lien)                                                                                                                                                               |
| Prix              | `div.price span.price-new` (ou `span.price` à défaut) sur le listing, ou `#product .price-new` sur la fiche détail ; normalisé en `price` (float) + `currency` (ISO à partir du symbole, ex. `$` → `USD`) |
| Catégorie         | dernier maillon non actif du fil d'Ariane (`.breadcrumb`) sur la fiche produit — dépend du chemin de navigation, voir limite documentée dans `docs/architecture.md`                                       |
| Disponibilité     | `<li>` contenant le libellé "Availability:" puis son `.badge`, sur la fiche produit ; normalisée en `in_stock` / `out_of_stock` / `preorder` / texte brut                                                 |
| Image             | attribut `data-src` (lazy-load) de `div.image img`, à défaut `src`                                                                                                                                        |
| URL fiche produit | attribut `href` du lien nom produit, résolu en URL absolue                                                                                                                                                |

## Contraintes et bonnes pratiques

- Respecter les directives du `robots.txt`
- Limiter la fréquence des requêtes (délai entre requêtes, éviter la surcharge du serveur)
- User-Agent identifiable
- Site de démonstration public conçu pour la pratique du scraping — aucune restriction contractuelle connue
