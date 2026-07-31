# Architecture

## Flux de données

```
[config.py]           lit .env : URL cible, MAX_ITEMS, délai, chemin de sortie
     |
     v
[http_client.py]      acquisition : GET + robots.txt (can_fetch) + throttle + retries HTTP
     |
     v
[extraction.py]       parsing HTML -> dicts bruts (nom, prix brut, url, image, dispo brute...)
     |
     v
[normalize.py]         normalisation (prix/devise, id, dispo) + validation + dédup
     |
     v
[export.py]            écriture JSONL
     |
     v
[scraper.py]            orchestrateur : enchaîne les 5 étapes ci-dessus, journalise les
                          compteurs (vus/acceptés/rejetés/doublons/exportés)
```

Les six responsabilités demandées par l'énoncé (configuration, acquisition, extraction,
normalisation/validation, export, journalisation/erreurs) correspondent chacune à un
fichier de `src/` : `config.py`, `http_client.py`, `extraction.py`, `normalize.py`,
`export.py`, et la journalisation/gestion d'erreurs est intégrée dans `scraper.py`
(logging du module `logging` + blocs `try/except` par page).

## Décisions structurantes

### 1. `requests` + BeautifulSoup plutôt qu'un navigateur piloté (Selenium/Playwright)

La comparaison entre la réponse HTTP brute et l'affichage navigateur est claire : le
HTML renvoyé par le serveur contient déjà tout ce qu'il faut — noms, prix, images,
liens produit. La vérification via un `curl` classique confronté à l'inspecteur du
navigateur sur `index.php?route=product/category&path=57` le confirme : on retrouve
bien les mêmes 15 fiches produit des deux côtés.

Du coup, passer par un navigateur piloté n'apporterait rien de plus, pour un coût
largement supérieur (dépendance à un navigateur, lenteur, fragilité des scripts).
L'option Playwright a été écartée pour cette raison : elle n'aurait eu de sens que si
le listing était chargé en JavaScript après coup, ce qui n'est pas le cas ici.

### 2. Extraction pure séparée de l'acquisition réseau

`extraction.py` ne fait aucun appel réseau : chaque fonction prend du HTML en paramètre et retourne des dicts. C'est justement cette séparation qui permet à `tests/verif.py` de rejouer l'extraction sur des pages enregistrées (tests/fixtures/\*.html) sans réseau, comme l'exige la vérification.

### 3. Fusion listing + détail avant normalisation

Le listing donne nom/prix/url/image ; la fiche produit donne disponibilité et
catégorie (fil d'Ariane). Le choix s'est porté sur une visite systématique de la
fiche détail de chaque produit retenu, plutôt que de se contenter du listing, car
`availability` n'existe nulle part dans ce dernier.
Seul compromis : cela double le nombre de requêtes (une par produit, en plus de la
pagination), d'où l'importance du plafond `MAX_ITEMS` et du délai configurable.

## Limite constatée : la catégorie dépend du chemin de navigation

Un même produit n'a pas de catégorie fixe sur ce site. Par exemple:
`product_id=28` ("HTC Touch HD") affiche "Software" comme catégorie quand on y arrive par `path=17`, mais affiche "Tablets" quand on y arrive par `path=57`. Le
site affiche donc la catégorie du chemin par lequel on est arrivé, pas une catégorie unique et définitive du produit.

Par conséquent pour mon programme : quand il rencontre ce produit, il note la première catégorie qu'il a vue, sans savoir si c'est "la bonne".
