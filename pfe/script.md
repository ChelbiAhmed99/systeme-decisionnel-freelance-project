# Soutenance PFE TravelBI — Script oral et dossier de conception

Oct 9, 2026 · @ons elloumi

## Cadre, charte et minutage

La présentation compte 25 diapositives pour environ 21 minutes, démonstration de 4 minutes comprise. Le rapport ne fixe aucune durée : l'hypothèse retenue est une soutenance de 20 à 25 minutes, à ajuster selon la consigne d'ESPRIT.

**Informations absentes du rapport, à compléter :** date et salle de soutenance, composition du jury, durée officielle. Les captures d'écran existent dans le rapport (figures 4.8 à 4.12 et 5.1 à 5.5) et sont à réexporter en haute résolution.

**Deux points dérivés, non repris tels quels du rapport :** l'architecture logique en couches est une synthèse des sections 3.2, 3.4 et 3.7 (le rapport ne contient qu'un diagramme de déploiement) ; le diagramme de classes reprend la figure 3.5 sans ajout.

### Charte graphique tirée du logo Sunny Tunisia Trip

| Rôle | Couleur | Code approché | Usage |
| --- | --- | --- | --- |
| Principale | Bleu marine du mot « Tunisia Trip » | #0B4F9E | Titres, bandeaux, formes des diagrammes |
| Accent | Orange soleil du mot « Sunny » | #F39A1E | Chiffres clés, élément mis en avant, numéros de section |
| Secondaire | Bleu vague | #2A9FD8 | Flèches, composants secondaires, graphiques |
| Fond doux | Sable de la médina | #FBF3E2 | Cartes et encadrés |
| Texte | Gris ardoise | #1F2A37 | Corps de texte sur fond blanc |

Les codes sont estimés à l'œil sur l'image : à vérifier avec la pipette de PowerPoint sur le logo. Typographie : un serif pour les titres (Georgia ou Cambria, en écho au logo), Calibri ou Segoe UI pour le corps, 24 pt minimum pour le texte, 14 pt minimum dans les diagrammes. Fond blanc, fine vague bleue en pied de page, logo en haut à droite, pagination « n / 25 » en bas à droite.

### Plan minuté

| N° | Diapositive | Section du plan | Durée |
| --- | --- | --- | --- |
| 1 | Titre | — | 0:20 |
| 2 | Plan | — | 0:20 |
| 3 | Introduction | Introduction | 0:50 |
| 4 | 2 Go Sunny Tunisia Trip | Organisme d'accueil | 0:40 |
| 5 | Le système actuel | Étude de l'existant | 0:45 |
| 6 | Cinq limites | Critique de l'existant | 0:45 |
| 7 | Problématique | Problématique | 0:30 |
| 8 | TravelBI, trois volets | Solution proposée | 1:00 |
| 9 | Besoins fonctionnels | Besoins fonctionnels | 0:45 |
| 10 | Besoins non fonctionnels | Besoins non fonctionnels | 0:35 |
| 11 | Cas d'utilisation | Diagramme de cas d'utilisation | 0:55 |
| 12 | Classes de TravelBI | Diagramme de classes | 0:55 |
| 13 | Scrum et CRISP-DM | Méthodologie de travail | 0:55 |
| 14 | Technologies | Technologies utilisées | 0:45 |
| 15 | Architecture logique | Architecture logique | 1:00 |
| 16 | Architecture physique | Architecture physique | 0:55 |
| 17 | Des données aux variables | Modèles d'IA | 0:50 |
| 18 | Moteur hybride | Modèles d'IA | 1:15 |
| 19 | Sept approches comparées | Modèles d'IA | 1:00 |
| 20 | Lecture critique | Modèles d'IA | 0:45 |
| 21 | Démonstration | Démonstration live | 4:00 |
| 22 | Secours démonstration | Démonstration live | masquée |
| 23 | Bilan | Conclusion | 0:45 |
| 24 | Perspectives | Perspectives | 0:35 |
| 25 | Questions | — | — |

## Script — Contexte (diapositives 1 à 8)

### 1 — Titre (0:20)

**Affiché :** « Conception et réalisation d'un système décisionnel intégrant un moteur de recommandation de destinations pour une agence de voyages » ; Ranim Nabi ; spécialité Data Science ; ESPRIT ; 2 Go Sunny Tunisia Trip ; encadrant académique M. Sirajeddine Miladi ; encadrant professionnel M. Kamel Kharrat ; 2025-2026. Logos ESPRIT et agence.

**Discours :** « Madame la présidente, Monsieur le président, mesdames et messieurs les membres du jury, bonjour. Je m'appelle Ranim Nabi, élève ingénieure en Data Science à ESPRIT. J'ai l'honneur de vous présenter mon projet de fin d'études, réalisé au sein de l'agence 2 Go Sunny Tunisia Trip, sous l'encadrement de M. Miladi et de M. Kharrat. »

**Transition :** « Voici le fil conducteur de cette présentation. »

**Conseil :** adapter la formule d'adresse au jury réel. Regarder le jury, pas l'écran.

### 2 — Plan (0:20)

**Affiché :** frise horizontale en cinq temps : Contexte · Analyse et conception · Réalisation · Démonstration · Bilan.

**Discours :** « Je commencerai par le contexte et la problématique. Je présenterai ensuite l'analyse des besoins et la conception, puis les choix techniques et le moteur de recommandation. Une démonstration de l'application précédera le bilan et les perspectives. »

**Transition :** « Commençons par le contexte. »

**Conseil :** ne pas lire les dix-sept sections ; cinq temps suffisent.

### 3 — Introduction (0:50)

**Affiché :** deux cartes face à face : « Piloter l'activité » (chiffre d'affaires, canaux, annulations, saisonnalité) et « Personnaliser le conseil » (une proposition adaptée à chaque client). En pied : « La donnée, actif stratégique, désormais accessible aux petites structures ».

**Discours :** « Aujourd'hui, un client compare les offres de voyage en ligne et attend des propositions adaptées à ses goûts. Une agence doit donc réussir deux choses à la fois : piloter son activité avec des indicateurs fiables, et personnaliser son conseil. L'informatique décisionnelle et l'apprentissage automatique, longtemps réservés aux grands groupes, sont maintenant à la portée d'une petite structure. C'est exactement le pari de ce projet : apporter ces deux capacités à une agence de taille modeste. »

**Transition :** « Cette agence, c'est 2 Go Sunny Tunisia Trip. »

**Conseil :** poser le double enjeu dès maintenant ; il structure toute la suite.

### 4 — Organisme d'accueil (0:40)

**Affiché :** logo ; fiche courte (agence de voyages, Monastir, avenue Habib Bourguiba, directeur M. Adel Nabi) ; activités (vols, hôtels, forfaits, conseil) ; quatre canaux de vente en icônes : agence physique, site web, application mobile, centre d'appels. Organigramme simplifié : direction, service commercial, clients et réservation, marketing et produit.

**Discours :** « 2 Go Sunny Tunisia Trip est une agence de voyages installée à Monastir et dirigée par M. Adel Nabi. Elle réserve des vols et des hôtels, vend des forfaits et conseille ses clients sur le choix de leur destination. Ses ventes passent par quatre canaux. Deux profils m'intéressent particulièrement : la direction, destinataire des indicateurs, et les conseillers commerciaux, qui utiliseront les recommandations face au client. »

**Transition :** « Comment l'agence travaille-t-elle aujourd'hui avec ses données ? »

**Conseil :** montrer du doigt la direction et le service commercial sur l'organigramme.

### 5 — Étude de l'existant (0:45)

**Affiché :** îlots de tables non reliés : customers, hotels, flights, flight\_price\_list, packages, bookings, cities, countries, continents. Deux étiquettes : « Suivi : consultation manuelle des fichiers » et « Conseil : expérience du conseiller ».

**Discours :** « L'agence possède des données sur ses clients, ses hôtels, ses vols, ses forfaits et ses réservations. Mais ces tables sont indépendantes : elles sont alimentées au fil de l'activité, sans être reliées ni exploitées de manière systématique. Le suivi de l'activité repose sur la consultation manuelle des fichiers, et le conseil sur la mémoire et l'expérience de chaque conseiller. »

**Transition :** « Cette organisation a des conséquences directes. »

**Conseil :** faire apparaître les tables une à une, volontairement dispersées.

### 6 — Critique de l'existant (0:45)

**Affiché :** cinq cartes numérotées : aucun indicateur consolidé · saisonnalité et rentabilité difficiles à repérer · pas de segmentation formalisée · recommandations sans exploitation de l'historique · volume réel réduit.

**Discours :** « J'ai relevé cinq limites. Le chiffre d'affaires, le panier moyen ou le taux d'annulation ne sont suivis ni dans le temps ni par canal. La saisonnalité et les destinations rentables sont difficiles à identifier. La connaissance client n'est pas formalisée. Les propositions ne s'appuient pas sur l'historique. Enfin, et c'est un point que j'assume tout au long de ce travail, l'historique réel est très réduit, ce qui limite toute analyse statistique directe. »

**Transition :** « Tout cela se résume en une question. »

**Conseil :** insister sur la cinquième limite : elle prépare la diapositive sur l'augmentation des données.

### 7 — Problématique (0:30)

**Affiché :** une seule phrase, centrée : « Comment permettre à l'agence de piloter son activité par des indicateurs fiables et de conseiller chaque client à partir de ses données ? »

**Discours :** « L'agence dispose de données précieuses, mais elle ne peut ni piloter son activité à partir d'indicateurs fiables, ni s'en servir pour conseiller chaque client. Le pilotage comme le conseil dépendent des personnes, et non des données. »

**Transition :** « Ma réponse tient en un nom : TravelBI. »

**Conseil :** marquer un silence d'une seconde après la phrase.

### 8 — Solution proposée (1:00)

**Affiché :** trois colonnes convergeant vers une application : volet données (pipeline Python, modèle en étoile), volet décisionnel (rapport Power BI de cinq pages), volet intelligent (moteur hybride). Dessous, comparaison avant/après en trois lignes : tables dispersées → modèle en étoile ; aucun indicateur → KPI et tableaux de bord ; expérience du conseiller → Top-N avec score et explication.

**Discours :** « J'ai conçu et réalisé un système décisionnel en trois volets. Un volet données : un pipeline Python qui charge, nettoie, enrichit et structure les données en modèle en étoile. Un volet décisionnel : un rapport Power BI de cinq pages. Un volet intelligent : un moteur de recommandation hybride. Ces trois volets sont réunis dans une application de bureau, TravelBI, qui affiche les indicateurs, intègre les rapports Power BI et calcule les recommandations localement, pour un client existant comme pour un nouveau client. »

**Transition :** « Pour arriver à cette solution, je suis partie des besoins. »

**Conseil :** c'est la diapositive que le jury retiendra ; ralentir.

## Script — Analyse et conception (diapositives 9 à 14)

### 9 — Besoins fonctionnels (0:45)

**Affiché :** quatre blocs alignés sur les sprints. Données : charger et qualifier, nettoyer, calculer les indicateurs, segmenter (BF1 à BF4). Décisionnel : modèle en étoile, tableaux de bord filtrables (BF5, BF6). Recommandation : Top-N expliqué pour un client existant, nouveau client, comparaison des modèles (BF7 à BF9). Application : tout réunir (BF10).

**Discours :** « J'ai identifié dix besoins fonctionnels, regroupés en quatre familles qui correspondent à mes quatre sprints. Préparer les données : les charger, en décrire la qualité, les nettoyer, calculer les indicateurs par client et par destination, puis segmenter la clientèle. Restituer : exporter un modèle en étoile et proposer des tableaux de bord filtrables. Recommander : pour un client existant, les destinations les plus pertinentes qu'il n'a pas encore réservées, avec un score et une explication, et aussi pour un nouveau client à partir de son seul profil. Enfin, réunir le tout dans une application de bureau. »

**Transition :** « À ces fonctions s'ajoutent des exigences de qualité. »

**Conseil :** ne pas énumérer BF1 à BF10 ; parler par famille.

### 10 — Besoins non fonctionnels (0:35)

**Affiché :** huit pictogrammes sur deux lignes : fiabilité, reproductibilité, cohérence, explicabilité, performance (moins d'une seconde), autonomie (hors ligne, sans Python), ergonomie (français), confidentialité.

**Discours :** « Huit exigences encadrent la solution. J'en souligne trois, qui ont guidé l'architecture. La cohérence : l'application doit reproduire exactement les recommandations du notebook. L'explicabilité : chaque recommandation doit être justifiée dans des termes compréhensibles par le client. L'autonomie : l'application doit fonctionner hors ligne, sans installation de Python sur les postes de l'agence. »

**Transition :** « Voyons qui utilise le système, et pour quoi faire. »

**Conseil :** mettre les trois exigences citées en orange, les cinq autres en bleu. Si le jury interroge sur la performance : le temps de réponse n'a pas été mesuré (limite L12).

### 11 — Diagramme de cas d'utilisation (0:55)

**Affiché :** diagramme UML, système « TravelBI », quatre acteurs, neuf cas d'utilisation (voir la spécification plus bas).

**Discours :** « Le système compte trois acteurs humains et un acteur système. Le directeur consulte le tableau de bord, les rapports Power BI et la performance des modèles. Le conseiller commercial obtient des recommandations pour un client existant ou pour un nouveau client, et peut les exporter. L'analyste de données prépare les données, entraîne les modèles, publie le rapport et vérifie la cohérence de l'application. Enfin, Power BI Service intervient comme acteur secondaire : il héberge le rapport publié, que l'application affiche. »

**Transition :** « Ces cas d'utilisation se traduisent dans la structure de l'application. »

**Conseil :** faire apparaître acteur par acteur avec ses cas ; suivre du pointeur.

### 12 — Diagramme de classes (0:55)

**Affiché :** diagramme UML de l'application : FenetrePrincipale, cinq pages, module indicateurs, RecommenderEngine.

**Discours :** « L'application repose sur un principe simple : séparer le calcul de l'interface. La fenêtre principale est composée de cinq pages : tableau de bord, rapports, recommandations, modèles et à propos. Le tableau de bord s'appuie sur le module indicateurs. Les pages de recommandation et à propos utilisent la classe RecommenderEngine, qui charge les artefacts, recommande pour un client existant ou nouveau, construit l'explication et expose une méthode selfcheck. Ni le moteur ni les indicateurs ne dépendent d'une bibliothèque graphique : ils peuvent être testés seuls, ce qui a rendu possible le contrôle automatique de cohérence. »

**Transition :** « Pour construire tout cela, il fallait une méthode adaptée à un projet à la fois logiciel et data. »

**Conseil :** montrer d'abord la composition, puis les deux dépendances « use ». Nommer selfcheck : il revient dans la démonstration.

### 13 — Méthodologie de travail (0:55)

**Affiché :** frise de 26 semaines : cadrage (S1 à S4), sprint 1 données (S5 à S9), sprint 2 décisionnel (S10 à S14), sprint 3 recommandation (S15 à S20), sprint 4 application (S21 à S24). Sous la frise, les phases CRISP-DM correspondantes. À droite, rôles : Product Owner (direction et encadrant professionnel), Scrum Master (encadrant académique), équipe (l'étudiante).

**Discours :** « Mon projet mêle de l'ingénierie logicielle, qui se livre par incréments, et de la science des données, dont le résultat n'est connu qu'après expérimentation. Aucune méthode ne couvrait seule les deux. J'ai donc retenu une approche hybride : Scrum pilote le projet en quatre sprints, et CRISP-DM structure le travail sur les données, de la compréhension du métier au déploiement. Chaque sprint avait un critère de validation explicite. Par exemple, pour le sprint 3 : un HitRate au rang 7 d'au moins 0,70. »

**Transition :** « Côté outils, j'ai cherché la continuité plutôt que l'accumulation. »

**Conseil :** montrer que le sprint 3 est le plus long (six semaines) et dire pourquoi : sept approches comparées.

### 14 — Technologies utilisées (0:45)

**Affiché :** quatre rangées avec logos. Données et modèles : Python, Jupyter sur Google Colab, pandas, NumPy, scikit-learn, LightGBM, XGBoost, CatBoost, Matplotlib, Seaborn. Stockage : fichiers CSV en modèle en étoile. Restitution : Power BI Desktop, Power BI Service, DAX. Application : PyQt6, Qt WebEngine, PyInstaller.

**Discours :** « Un seul langage, Python, couvre toute la chaîne : préparation, modèles, interface et distribution. Cela évite toute rupture entre la préparation des données et la modélisation. Le modèle en étoile est exporté en fichiers CSV : avec quelques milliers de réservations et aucun serveur à l'agence, c'est le choix proportionné, et le passage à un SGBD reste possible sans changer le modèle. Power BI a été retenu pour sa version Desktop gratuite, son import direct des CSV et la possibilité d'intégrer le rapport publié dans une application tierce. »

**Transition :** « Voyons comment ces briques s'assemblent. »

**Conseil :** anticiper la question « pourquoi pas une base de données ? » : la réponse est dans le discours.

## Script — Architectures et intelligence artificielle (diapositives 15 à 20)

### 15 — Architecture logique (1:00)

**Affiché :** cinq couches de gauche à droite : sources (tables de l'agence) → préparation (notebook : nettoyage, RFM, profils, interactions, segmentation) → stockage (modèle en étoile et KPI en CSV ; artefacts des modèles) → modèles (contenu, LightGBM, popularité ; factorisation en grisé, poids nul) → restitution (rapport Power BI ; application TravelBI avec indicateurs.py, moteur\_reco.py, app.py). Bandeau : « Le notebook, source unique ».

**Discours :** « L'architecture logique s'organise en cinq couches. Les tables de l'agence alimentent un pipeline de préparation, écrit dans un notebook. Ce pipeline produit deux ensembles : le modèle en étoile et les tables d'indicateurs destinés à Power BI, et les artefacts des modèles destinés à l'application. Le principe directeur est celui de la source unique : Power BI et l'application consomment les fichiers issus de la même exécution du notebook. La table de faits est la même pour les deux outils, et les recommandations de l'application sont calculées avec les modèles exportés. C'est ce qui garantit la fiabilité des indicateurs et la cohérence des recommandations. »

**Transition :** « Physiquement, cette architecture se déploie sur trois nœuds. »

**Conseil :** faire apparaître les couches dans l'ordre du flux ; terminer par le bandeau « source unique ».

### 16 — Architecture physique (0:55)

**Affiché :** diagramme de déploiement à trois nœuds : poste d'analyse (notebook Jupyter/Colab, powerbi\_exports, Power BI Desktop, dossier TravelBI\_App) ; Power BI Service (rapport publié) ; poste de l'agence (TravelBI.exe ; models, data, config.json). Liens : publication, copie, HTTPS.

**Discours :** « Sur le poste d'analyse, le notebook exporte les fichiers CSV, importés dans Power BI Desktop, ainsi que le dossier de l'application. Le rapport est publié sur Power BI Service. Sur le poste de l'agence, l'exécutable TravelBI lit localement ses modèles, ses données et son fichier de configuration : les indicateurs et les recommandations sont donc calculés hors ligne, et les données clients restent sur le poste. Seul l'affichage du rapport publié passe par le réseau, en HTTPS et après authentification. Il n'y a ni serveur applicatif ni base de données : c'est un choix assumé pour une agence sans infrastructure. »

**Transition :** « Entrons maintenant dans le cœur intelligent du système, en commençant par les données. »

**Conseil :** l'alimentation est manuelle (limite L11) : le dire si la question vient.

### 17 — Des données aux variables (0:50)

**Affiché :** entonnoir chiffré : 11 clients et 16 réservations réels → augmentation (bootstrap, perturbation, génération par segment) → 500 clients, 45 destinations, 9 944 réservations → nettoyage → 9 916 réservations (28 doublons retirés, 444 montants écrêtés par IQR) → 4 802 interactions client–destination. Encadré : segmentation KMeans, k = 5, sur six variables.

**Discours :** « L'historique réel de l'agence se limite à 11 clients et 16 réservations. C'est insuffisant pour apprendre un modèle. J'ai donc augmenté les données par un script dédié qui combine rééchantillonnage, perturbation contrôlée et génération conditionnée par segment, en restant ancrée dans la réalité de l'agence : mêmes villes, mêmes hôtels, mêmes tarifs. Une colonne source garde l'origine de chaque ligne. Après nettoyage, j'obtiens 9 916 réservations. Comme il n'existe pas de note explicite d'une destination par un client, j'ai construit un score d'interaction implicite de 0 à 5, qui pondère la satisfaction, la récence et le montant. Il donne 4 802 interactions. En parallèle, KMeans segmente la clientèle en cinq groupes. »

**Transition :** « C'est sur ces interactions que le moteur apprend. »

**Conseil :** dire « données générées » sans détour. La transparence ici protège tout le reste de la présentation.

### 18 — Le moteur hybride (1:15)

**Affiché :** flux de gauche à droite : profil client et destination → quatre signaux en parallèle → combinaison pondérée → exclusion des destinations déjà réservées → Top-N avec explication. Poids affichés : contenu 0,2 · factorisation matricielle 0 · LightGBM 0,5 · popularité 0,3.

**Discours :** « Le moteur combine quatre signaux, chacun ramené sur une échelle de 0 à 5. Le filtrage par contenu mesure la similarité cosinus entre le profil du client et celui de la destination, décrits dans un même espace de vingt dimensions : type de voyage, activités et budget. La factorisation matricielle, que j'ai implémentée avec NumPy, capture le comportement collectif. Un modèle supervisé de gradient boosting prédit la pertinence d'un couple client–destination à partir de quinze variables. Enfin, la popularité sert d'a priori. Les poids ont été cherchés sur une grille de 286 combinaisons. Résultat : 0,2 pour le contenu, 0,5 pour LightGBM, 0,3 pour la popularité, et zéro pour la factorisation, dont le signal est redondant sur ces données. Pour un nouveau client, le profil déclaré remplace l'historique. Et chaque recommandation est accompagnée d'une explication en langage naturel, construite par règles : type de voyage, activités communes, budget, popularité, satisfaction. »

**Transition :** « Reste à savoir si ce modèle hybride fait réellement mieux que ses composantes. »

**Conseil :** animer signal par signal. Le poids nul est un résultat, pas un échec : le présenter ainsi.

### 19 — Sept approches comparées (1:00)

**Affiché :** histogramme groupé HitRate@7 et NDCG@7 pour les sept approches, barre « Hybride » en orange. Chiffre clé : HitRate@7 = 85 %, seuil visé 70 %. Petit encadré : « RMSE le plus bas (0,354) : factorisation, pourtant dernière au classement ».

| Approche | NDCG@7 | HitRate@7 |
| --- | --- | --- |
| Contenu | 0,234 | 0,585 |
| Factorisation matricielle | 0,077 | 0,224 |
| LightGBM | 0,443 | 0,820 |
| XGBoost | 0,410 | 0,812 |
| CatBoost | 0,433 | 0,826 |
| Ensemble GBM | 0,425 | 0,810 |
| Hybride | 0,461 | 0,850 |

**Discours :** « J'ai comparé sept approches sur un jeu de test, au rang 7, c'est-à-dire la longueur d'une liste qu'un conseiller peut présenter en entretien. Le modèle hybride arrive en tête sur les cinq métriques de classement. Son HitRate atteint 85 % : pour 85 clients sur 100, la liste contient au moins une destination pertinente. Le seuil de 70 % fixé au départ est dépassé. Un enseignement intéressant : la factorisation matricielle a la meilleure erreur quadratique, et le plus mauvais classement. Cela confirme ce que montre la littérature : le RMSE ne mesure pas la qualité d'un Top-N. C'est pourquoi j'ai décidé sur le NDCG et le HitRate. »

**Transition :** « Ce chiffre de 85 %, je tiens à le lire avec vous de façon critique. »

**Conseil :** sur la diapositive, ne garder que le graphique et le chiffre clé ; le tableau reste dans les notes.

### 20 — Lecture critique des résultats (0:45)

**Affiché :** trois cartes : biais de sélection (poids et booster choisis sur le jeu de test) · fuite d'information (variables calculées avant le découpage) · pertinence peu sélective (97,6 % des interactions au-dessus du seuil). Conclusion en pied : « 85 % = borne haute ; la démarche et la chaîne technique sont validées ».

**Discours :** « En examinant mon propre protocole, j'ai identifié trois biais. Les poids du modèle hybride et le choix du booster ont été réglés sur le jeu de test. Certaines variables ont été calculées avant le découpage entre entraînement et test, ce qui constitue une fuite d'information. Et le seuil de pertinence est peu sélectif. S'y ajoute le caractère majoritairement généré des données. Je présente donc ces 85 % comme une borne haute, et non comme une performance garantie en production. Ce que ce travail valide, c'est la démarche et la chaîne technique, qui peut être rejouée sur des données réelles sans modifier le code de l'application. »

**Transition :** « Je vous propose maintenant de voir cette chaîne fonctionner. »

**Conseil :** ton posé, sans s'excuser. Un jury apprécie qu'une candidate nomme elle-même ses limites.

## Script — Démonstration et conclusion (diapositives 21 à 25)

### 21 — Démonstration live (4:00)

**Affiché :** titre « Démonstration » et le parcours en cinq étapes numérotées. La diapositive reste à l'écran dix secondes, puis bascule vers l'application.

**Annonce :** « Je vais suivre le parcours de deux utilisateurs : le directeur, puis un conseiller face à un client. »

| Étape | Action en direct | Ce que le jury doit observer | Durée |
| --- | --- | --- | --- |
| 1 | Lancer TravelBI ; page Tableau de bord, année 2026 | Six indicateurs avec variation annuelle : CA 5,61 M TND, 1 791 réservations, panier 3 645 TND, annulation 14,1 %, 485 clients actifs ; barre d'état « 500 clients, 45 destinations, booster LightGBM » | 0:45 |
| 2 | Page Rapports Power BI ; ouvrir le rapport, passer de l'accueil à « Vue d'ensemble » ; changer le filtre de statut familial | Le rapport publié s'affiche dans l'application ; les visuels réagissent au filtre | 0:45 |
| 3 | Page Recommandations, mode client existant ; choisir CLI00001 ; N = 5 | Top-5 : Venise 2,18 · Antalya 1,81 · Amsterdam 1,77 · Milan 1,69 · Sydney 1,64 ; explication par ligne ; graphique de décomposition du score | 1:00 |
| 4 | Mode nouveau client : 35 ans, 1 500 TND, type Aventure, budget 4 000 TND, deux activités ; recommander ; exporter en CSV | Une liste s'affiche sans aucun historique ; le fichier CSV est créé | 0:50 |
| 5 | Page À propos ; cliquer « Vérifier la cohérence avec le notebook » | Message « Top-7 identique au notebook pour 40/40 clients, écart de score maximal 0,000 » | 0:40 |

**Discours par étape :**

1. « Voici ce que voit le directeur à l'ouverture. Pour l'année choisie, six indicateurs et leur variation par rapport à l'année précédente, calculés localement à partir de la table de faits. »
2. « Sans quitter l'application, il accède au rapport Power BI publié. Je filtre sur le statut familial : toutes les analyses se mettent à jour. »
3. « Je passe du côté du conseiller. Il reçoit un client connu, ici CLI00001. Le moteur écarte les destinations déjà réservées et propose cinq destinations. Chaque ligne est justifiée : activités appréciées, budget habituel, satisfaction. Le graphique montre la contribution de chaque signal au score. Les scores absolus sont modestes, autour de 2 sur 5 : seul l'ordre relatif sert à recommander. »
4. « Un nouveau client se présente, sans aucun historique. Je saisis son profil. Le moteur s'appuie alors sur le profil déclaré et la popularité. Le conseiller peut exporter la proposition. »
5. « Dernier point : comment savoir que l'application calcule la même chose que le notebook ? Ce contrôle compare automatiquement les recommandations à quarante clients de référence. »

**Transition de sortie :** « Cette démonstration illustre la chaîne complète, des données à la décision. Je termine par le bilan. »

**Conseils :** lancer l'application avant la soutenance et la laisser ouverte. Vérifier la connexion et la session Power BI ; la capture du rapport mentionne un essai Power BI à durée limitée, à contrôler la veille. Le scénario 4 (test T5) est marqué « à documenter » dans le rapport : le répéter plusieurs fois et noter le résultat obtenu avant de l'annoncer. Ne pas montrer la page « Saisonnalité et canaux » sans prévenir : ses visuels par canal affichent la même valeur pour les quatre canaux (limite L8).

### 22 — Secours démonstration (diapositive masquée)

**Affiché :** quatre captures réelles du rapport : tableau de bord (figure 4.8), recommandations pour CLI00001 (figure 4.9), rapport Power BI intégré (figure 4.11), contrôle de cohérence (figure 4.12).

**Discours si la démonstration échoue :** « Pour ne pas perdre de temps, je vous présente les mêmes écrans sous forme de captures. » Puis reprendre le discours des étapes 1, 3, 2 et 5 sur chaque capture.

**Conseil :** si seul Power BI ne charge pas, ne basculer que pour l'étape 2 ; le reste fonctionne hors ligne.

### 23 — Conclusion (0:45)

**Affiché :** quatre jalons cochés, un par sprint : données nettoyées, RFM, cinq segments · modèle en étoile et rapport Power BI de cinq pages · sept approches comparées, modèle hybride retenu (HitRate@7 85 %, NDCG@7 0,461) · application TravelBI, cohérence 40/40.

**Discours :** « Ce projet répondait à un besoin concret : transformer des données dispersées en un outil d'aide à la décision. Les quatre sprints ont livré quatre résultats : des données fiabilisées et une clientèle segmentée ; un modèle en étoile restitué dans Power BI ; un moteur hybride retenu après comparaison de sept approches ; et une application qui réunit l'ensemble, et dont la cohérence avec le notebook est vérifiée automatiquement. Sur le plan personnel, j'ai mené un projet de science des données de bout en bout, et j'en retiens surtout une exigence : vérifier ses résultats et savoir en exposer les limites. »

**Transition :** « Ces limites dessinent naturellement la suite. »

**Conseil :** faire apparaître les quatre jalons un à un.

### 24 — Perspectives (0:35)

**Affiché :** deux colonnes. Court terme : découpage entraînement, validation, test ; variables calculées sur l'entraînement seul ; définitions d'indicateurs harmonisées entre Power BI et l'application ; mesure de la diversité des recommandations. Long terme : collecte de l'historique réel et réentraînement ; mise en production sur un serveur multi-postes ; expérimentation contrôlée auprès des clients.

**Discours :** « À court terme, il s'agit de corriger le protocole d'évaluation, d'harmoniser les définitions d'indicateurs entre Power BI et l'application, et de mesurer la diversité des listes. À plus long terme, la collecte de l'historique réel permettra de réentraîner les modèles, et une expérimentation contrôlée auprès des clients mesurera l'apport commercial réel du moteur, ce qu'aucune métrique hors ligne ne peut garantir. »

**Transition :** « Je vous remercie de votre attention. »

**Conseil :** finir en regardant le jury, sans relire la diapositive.

### 25 — Questions

**Affiché :** « Merci de votre attention », logo de l'agence, nom et encadrants.

**Discours :** « Je remercie mes encadrants, M. Miladi et M. Kharrat, ainsi que M. Adel Nabi et l'équipe de l'agence. Je suis à votre disposition pour vos questions. »

## Diagrammes à dessiner et animations

Chaque diagramme se construit avec des formes et des connecteurs natifs de PowerPoint, pour rester net et modifiable. Tous les éléments ci-dessous viennent du rapport.

### Cas d'utilisation (diapositive 11, d'après la figure 3.1)

Rectangle « Système TravelBI » au centre. Acteurs humains à gauche et à droite, acteur système marqué « système ».

| Acteur | Cas d'utilisation reliés (association simple) |
| --- | --- |
| Directeur | Consulter le tableau de bord · Consulter les rapports Power BI · Consulter la performance des modèles |
| Conseiller commercial | Recommander pour un client existant · Recommander pour un nouveau client · Exporter les recommandations |
| Analyste de données | Préparer les données et entraîner les modèles · Publier le rapport Power BI · Vérifier la cohérence |
| Power BI Service (système) | Consulter les rapports Power BI · Publier le rapport Power BI |

Le rapport ne définit aucune relation « include » ou « extend » : ne pas en ajouter.

### Classes (diapositive 12, d'après la figure 3.5)

| Classe | Attributs | Méthodes |
| --- | --- | --- |
| FenetrePrincipale | moteur : RecommenderEngine ; config : dict | naviguer(page) ; recharger() |
| PageTableauBord | annee : int | actualiser() |
| PageRapports | liens : list | afficher(lien) ; modePresentation() |
| PageRecommandations | mode : str ; n : int | recommander() ; exporterCSV() |
| PageModeles | comparaison : DataFrame | afficher() |
| PageAPropos | etatFichiers : dict | verifierCoherence() ; recharger() |
| indicateurs (module) | faits : DataFrame | calculerKPI(annee) ; caMensuel(annee) ; topDestinations(annee) |
| RecommenderEngine | meta : dict ; booster : Booster ; vecteurs, P, Q, biais ; poids : dict | charger(dossier) ; recommanderClient(client\_id, n) ; recommanderNouveau(profil, n) ; expliquer(client, destination) ; selfcheck() |

Relations : composition (losange plein côté FenetrePrincipale) vers les cinq pages. Dépendances « use » en pointillé : PageTableauBord → indicateurs ; PageRecommandations → RecommenderEngine ; PageAPropos → RecommenderEngine. Le rapport n'indique ni héritage, ni agrégation, ni multiplicités. Disposition : fenêtre en haut, pages sur une ligne, modules de calcul en bas.

### Architecture logique (diapositive 15, synthèse)

1. Sources : clients, destinations, hôtels, vols, préférences, réservations.
2. Préparation (notebook) : qualité, nettoyage, variables RFM, vecteurs de profil, score d'interaction, segmentation KMeans. Flèche « charge ».
3. Stockage : powerbi\_exports (fact\_reservations, quatre dimensions, sept tables KPI) et TravelBI\_App (booster LightGBM natif, embeddings, vecteurs de contenu, fichiers de données). Flèches « exporte ».
4. Modèles : contenu, factorisation matricielle, LightGBM, popularité, combinaison pondérée.
5. Restitution : Power BI Desktop puis Service (« importe », « publie ») ; TravelBI avec indicateurs.py, moteur\_reco.py, app.py (« lit »). Flèche « affiche via HTTPS » du rapport publié vers app.py.

Code couleur : bleu marine pour les données, bleu vague pour le décisionnel, orange pour l'IA.

### Architecture physique (diapositive 16, d'après la figure 3.2)

Trois nœuds en boîtes 3D. Poste d'analyse : notebook (Jupyter/Colab), powerbi\_exports (CSV), Power BI Desktop, TravelBI\_App (models, data). Power BI Service : rapport publié. Poste de l'agence : TravelBI.exe ; models, data, config.json. Connecteurs légendés : exporte (notebook → exports et dossier d'application), importe (exports → Desktop), publication (Desktop → Service), copie (dossier d'application → poste de l'agence), lit (exécutable → fichiers locaux), HTTPS (exécutable ↔ rapport publié). Ne pas ajouter de serveur, de base de données ni de conteneur : le rapport n'en contient pas. Le rapport présente le notebook dans le nœud poste d'analyse tout en l'exécutant sur Google Colab : garder la mention « Jupyter / Colab ».

### Compléments utiles

Modèle en étoile (figure 3.3) en diapositive d'annexe : fact\_reservations au centre, reliée en 1 à plusieurs à dim\_clients, dim\_destinations, dim\_hotels, dim\_flights et Dim\_Dates. Diagramme de séquence (figure 3.6) en annexe pour les questions.

### Animations et transitions

Transition unique sur tout le diaporama : Fondu, 0,5 s. Aucune autre.

| Diapositive | Éléments | Effet | Déclenchement |
| --- | --- | --- | --- |
| 5 | Tables dispersées | Apparaître, une par une | Après la précédente, 0,2 s |
| 6, 20 | Cartes | Fondu, une par clic | Au clic |
| 8 | Trois volets, puis l'application, puis le tableau avant/après | Fondu | Au clic, trois temps |
| 11 | Chaque acteur groupé avec ses cas et liens | Fondu | Au clic, quatre temps |
| 12 | Fenêtre et pages ; puis modules ; puis dépendances | Fondu, puis Balayage pour les flèches | Au clic, trois temps |
| 13 | Segments de la frise | Balayage depuis la gauche | Au clic |
| 15 | Couches dans l'ordre du flux, bandeau en dernier | Balayage depuis la gauche | Au clic, six temps |
| 16 | Nœuds, puis connecteurs dans l'ordre exporte, importe, publication, copie, HTTPS | Fondu, puis Balayage | Au clic |
| 17 | Étapes de l'entonnoir | Fondu | Au clic |
| 18 | Quatre signaux un à un, combinaison, Top-N | Fondu | Au clic, six temps |
| 19 | Barres, puis mise en avant de la barre Hybride | Balayage depuis le bas ; Emphase couleur | Au clic, deux temps |
| 23 | Quatre jalons | Fondu | Au clic |

Grouper les formes avant d'animer (Ctrl+G). Chaque diapositive reste complète et lisible si les animations sont désactivées.

## Guide de finalisation

- [ ] Confirmer la durée officielle de la soutenance et ajuster le minutage (hypothèse : 20 à 25 minutes).
- [ ] Compléter la diapositive de titre : date, composition du jury si l'usage d'ESPRIT le demande.
- [ ] Relever les codes exacts des couleurs du logo avec la pipette de PowerPoint.
- [ ] Réexporter en haute résolution les captures réelles : figures 4.8 à 4.12 (application) et 5.1 à 5.5 (Power BI).
- [ ] Exécuter et capturer les scénarios T5, T6 et T7, marqués « à documenter » dans le rapport.
- [ ] Vérifier la veille l'accès à Power BI Service et la validité de la licence d'essai.
- [ ] Répéter la démonstration chronomètre en main ; viser 4 minutes.
- [ ] Préparer la diapositive de secours et la masquer.
- [ ] Appliquer les animations du tableau ci-dessus et tester le diaporama sur le poste de la salle.
- [ ] Relire deux points du rapport avant le dépôt : sur la figure 5.1, deux boutons de la page d'accueil portent le même libellé « Saisonnalité et canaux » ; les captures Power BI sont filtrées sur un statut familial, leurs valeurs ne sont donc pas les totaux.

### Questions probables du jury

| Question | Élément de réponse tiré du rapport |
| --- | --- |
| Vos résultats valent-ils sur des données générées ? | Ils valident la démarche et la chaîne technique, pas le comportement réel de la clientèle (limite L1). La chaîne se rejoue sur des données réelles sans modifier l'application. |
| Pourquoi le poids de la factorisation est-il nul ? | Matrice remplie à 21 %, moins de dix destinations par client ; signal redondant avec le booster et la popularité (limite L6). |
| Pourquoi un RMSE excellent et un classement médiocre ? | La factorisation n'apprend que sur des interactions positives, concentrées autour de 3,8 : elle prédit la moyenne partout. |
| Pourquoi K = 7 et un seuil de 0,70 ? | Sept suggestions correspondent à ce qu'un conseiller présente en entretien ; le seuil a été fixé avec l'agence comme critère du sprint 3. |
| Pourquoi des CSV plutôt qu'un SGBD ? | Volume modeste, aucun serveur à l'agence, import direct dans Power BI ; migration possible sans changer le modèle. |
| La popularité à 30 % ne nuit-elle pas à la diversité ? | Risque reconnu ; la diversité et la couverture n'ont pas été mesurées (limite L5). |
| Pourquoi 8 597 réservations dans Power BI et 9 916 ailleurs ? | Power BI compte les confirmées, l'application toutes les réservations ; définition à unifier (limite L7). |
| Comment corrigeriez-vous le protocole ? | Trois jeux (entraînement, validation, test) et variables calculées sur l'entraînement seul (limites L3 et L13). |
