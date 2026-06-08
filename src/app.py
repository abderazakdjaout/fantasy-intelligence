import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(__file__))
from analysis import top_joueur_par_position, joueurs_budget, comparer_joueurs, joueurs_sous_evalues

# Titre
st.title("⚽ Fantasy Football Intelligence")
st.subheader("Coupe du Monde 2026")

# Charger les données
df = pd.read_csv("data/raw/players.csv")

# Calculer les colonnes
df["score_valeur"] = df["points"] / df["price"]
moyennes = df.groupby("position")["score_valeur"].mean()
df["moyenne_position"] = df["position"].map(moyennes)
df["statut"] = np.where(
    df["score_valeur"] > df["moyenne_position"],
    "SOUS-EVALUE",
    "SUR-EVALUE"
)

# SIDEBAR — filtres à gauche
st.sidebar.header("Filtres")

position_choisie = st.sidebar.selectbox(
    "Position",
    ["Toutes", "ATT", "MID", "DEF", "GKP"]
)

budget = st.sidebar.slider(
    "Budget maximum (M)",
    min_value=5.0,
    max_value=12.0,
    value=12.0,
    step=0.5
)

# Appliquer les filtres
df_filtre = df.copy()

if position_choisie != "Toutes":
    df_filtre = df_filtre[df_filtre["position"] == position_choisie]

df_filtre = df_filtre[df_filtre["price"] <= budget]

# CONTENU PRINCIPAL
st.header("Joueurs")
st.dataframe(df_filtre[["name", "team", "position", "price", "points", "score_valeur", "statut"]])

# Graphique
st.header("Score valeur")
df_tri = df_filtre.sort_values("score_valeur", ascending=False)
fig = px.bar(df_tri, x="name", y="score_valeur", color="position")
st.plotly_chart(fig)

# Joueurs sous-évalués
st.header("Joueurs sous-évalués")
st.dataframe(joueurs_sous_evalues(df_filtre)[["name", "team", "position", "price", "points", "score_valeur"]])