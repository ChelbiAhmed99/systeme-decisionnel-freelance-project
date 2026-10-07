# TravelBI — application desktop du système décisionnel

| Section | Contenu |
|---|---|
| **Tableau de bord** | 6 indicateurs (CA, réservations, panier moyen, taux d'annulation, satisfaction, clients actifs) avec variation vs année précédente, CA mensuel, top destinations, canaux de vente, types de voyage ; filtre par année |
| **Rapports Power BI** | Plusieurs rapports Power BI Service affichés dans l'application, lien ou code `<iframe>`, connexion Microsoft mémorisée, mode présentation |
| **Recommandations** | Client existant (recherche, fiche profil, résultats instantanés) ou nouveau client (cold-start), explication et décomposition du score, export CSV |
| **Performance des modèles** | Meilleur modèle, taux de réussite, NDCG, pondération hybride, tableau et graphiques (classement et RMSE) |
| **À propos** | Fiche du modèle, état des fichiers, contrôle de cohérence avec le notebook, rechargement |

## Mise en place

1. Dans le notebook, exécutez tout jusqu'à la **section 15** : elle télécharge `TravelBI_App.zip`
   (dossiers `models/`, `data/` et `config.json`).
2. Dézippez-le au même endroit que ce dossier-ci : les deux archives contiennent `TravelBI_App/` et se complètent.
3. Lancez `run_windows.bat` (Windows) ou `./run_mac_linux.sh`, ou `pip install -r requirements.txt` puis `python app.py`.

## Vérifier que l'application reproduit le notebook

```
python app.py --selfcheck
```
Le moteur recalcule les recommandations de 40 clients et les compare à celles calculées dans le notebook
(`data/reference_recos.csv`). Le même contrôle est disponible dans la section **À propos**.

## Ajouter un rapport Power BI

Power BI Service › ouvrir le rapport › **Fichier › Intégrer le rapport** :
- **Site web ou portail** : lien sécurisé, connexion Microsoft une fois (session mémorisée) ;
- **Publier sur le web (public)** : sans connexion, mais le rapport devient public.

Puis **Rapports Power BI › Ajouter un rapport** et collez le lien ou le code `<iframe>`. Les rapports sont
enregistrés dans `config.json` ; l'ancienne clé `powerbi_url` est reprise automatiquement.

## Structure

```
TravelBI_App/
├── app.py            interface (PyQt6)
├── moteur_reco.py    moteur de recommandation hybride (sans interface)
├── indicateurs.py    calcul des indicateurs du tableau de bord (sans interface)
├── config.json       rapports Power BI
├── models/  data/    produits par la section 15 du notebook
└── assets/           logo.png facultatif
```

Raccourcis : `Ctrl+1` à `Ctrl+5` pour les sections, `F5` actualiser le rapport, `F11` plein écran,
`Échap` quitter le mode présentation.
