# ⚽ Fantasy Football Intelligence

Dashboard d'aide à la décision pour le fantasy football — Coupe du Monde 2026.

## Ce que ça fait

- Affiche tous les joueurs avec leurs statistiques
- Filtre par position et par budget
- Calcule le score valeur/prix de chaque joueur
- Identifie les joueurs sous-évalués
- Visualise les performances avec des graphiques interactifs

## Technologies utilisées

- Python
- pandas — manipulation de données
- Streamlit — dashboard interactif
- Plotly — visualisations

## Comment lancer le projet

```bash
streamlit run src/app.py
```

## Structure du projet

Fantasy-intelligence/
├── data/
│   └── raw/
│       └── players.csv
├── src/
│   ├── analysis.py    # fonctions d'analyse
│   ├── app.py         # dashboard Streamlit
│   └── explore_api.py # exploration des données
└── README.md

## Auteur

Zakyzak