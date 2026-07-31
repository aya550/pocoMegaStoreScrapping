FICHE DE CIBLE - DataHarvest
=============================

Cible ................. LambdaTest E-commerce Playground (Poco MegaStore / OpenCart)
URL de depart ......... https://ecommerce-playground.lambdatest.io/
Date d analyse ........ 2026-07-30
Analyste .............. Aya SGHAIER SLIM & Danielle Jamila KOAGNE NGANKAM

1. SOURCE
   Famille de site ......... SSR
   Preuve .................. curl -s "https://ecommerce-playground.lambdatest.io/index.php?route=product/category&path=17" | grep -c "product-thumb" -> 15
   Fichiers publies ........ robots.txt : oui | sitemap.xml : oui
   Nombre d URLs connues ... 65 (1 accueil + 4 pages listing + 60 fiches produit)

2. SURFACE PORTEUSE DE LA DONNEE
   HTML initial ............ oui   (marqueur : <div class="product-thumb">, occurrences : 15)
   DOM apres JS ............ non   (identique au HTML initial, aucun composant dynamique JS)
   Appel reseau ............ GET https://ecommerce-playground.lambdatest.io/index.php?route=product/category&path=17
   Format de reponse ....... HTML
   Champs disponibles ...... nom, prix, url, image (listing) ; disponibilite, categorie (detail)
   Couverture du contrat ... champs Product manquants : aucun

3. TECHNIQUE D ACQUISITION RETENUE
   Niveau .................. 2
   Valeur de source ........ http
   Commande de reference ... curl -s -A "Mozilla/5.0" "https://ecommerce-playground.lambdatest.io/index.php?route=product/category&path=17"
   En-tetes necessaires .... User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
   Pagination .............. liens href
   Condition d arret ....... Plafond MAX_ITEMS (60 produits) atteint ou absence de lien 'suivant'
   Niveaux ecartes ......... Niveau 3/4 (Playwright/Selenium) : ecarte car aucun rendu client JS n est necessaire ; Niveau 1 (API) : ecarte car aucune API JSON publique n est exposee

4. COMPLEXITE
   Estimation .............. S
   Justification ........... HTML statique serveur regulier avec selecteurs CSS stables et pagination HTML classique sans authentification ni CAPTCHA

5. RISQUES ET CONTRAINTES
   Techniques .............. Categorie dependante de la route d acces ; disponibilite presente uniquement sur la fiche detail produit
   Juridiques .............. Site demo public ; robots.txt autorise (can_fetch = True) ; aucune donnee personnelle collectee
   Charge .................. concurrence max 1 | delai min 1000 ms | conduite sur 429 : retry avec backoff et pause 5s
   Point de rupture ........ Modification des classes CSS du theme OpenCart (product-thumb, price-new, ls-label)
   Repli prevu ............. Niveau 3 (Playwright) si activation d un rendu dynamique JS cote client (cout : vitesse d execution reduite)
