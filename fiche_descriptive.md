# Fiche descriptive — Site cible

## Identité du site
- **Nom** : LambdaTest E-commerce Playground
- **URL** : https://ecommerce-playground.lambdatest.io/
- **Type de site** : catalogue e-commerce (démo publique basée sur OpenCart)
- **Objectif du site** : bac à sable public destiné aux tests d'automatisation et de scraping

## Analyse technique
- **Rendu** : _à compléter (HTML côté serveur, SPA/JS, mix ?)_
- **Pagination** : via paramètre `page=` dans l'URL (exclu du crawl par `robots.txt` sur certaines combinaisons de query string)
- **Authentification requise** : non (catalogue public)
- **robots.txt** : autorise le crawl général ; interdit certaines combinaisons de paramètres (`?page=`, `&page=`, `?sort=`, `&sort=`, `?order=`, `&order=`, `?limit=`, `&limit=`, `?filter_*`)
- **Structure des pages produit** : _à compléter (sélecteurs CSS/XPath une fois analysés)_

## Données ciblées
| Champ | Description |
| --- | --- |
| Nom produit | _à compléter_ |
| Prix | _à compléter_ |
| Catégorie | _à compléter_ |
| Disponibilité | _à compléter_ |
| Image | _à compléter_ |
| URL fiche produit | _à compléter_ |

## Contraintes et bonnes pratiques
- Respecter les directives du `robots.txt`
- Limiter la fréquence des requêtes (délai entre requêtes, éviter la surcharge du serveur)
- User-Agent identifiable
- Site de démonstration public conçu pour la pratique du scraping — aucune restriction contractuelle connue
