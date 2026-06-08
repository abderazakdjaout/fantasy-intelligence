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
df = pd.read_csv("data/raw/players_sofascore.csv")

# Charger les groupes et joindre
df_groups = pd.read_csv("data/raw/groups.csv")
df = df.merge(df_groups, on="team", how="left")

# Charger la force des groupes et joindre
df_strength = pd.read_csv("data/raw/group_strength.csv")
df = df.merge(df_strength, on="group", how="left")

# Charger les tireurs de penalties et joindre
df_penalties = pd.read_csv("data/raw/penalty_takers.csv")
df = df.merge(df_penalties[["name", "is_penalty_taker"]], on="name", how="left")
df["is_penalty_taker"] = df["is_penalty_taker"].fillna(False)

# Calculer les colonnes
df["score_valeur"] = df["total_score"] / df["price"]
moyennes = df.groupby("position")["score_valeur"].mean()
df["moyenne_position"] = df["position"].map(moyennes)
df["statut"] = np.where(
    df["score_valeur"] > df["moyenne_position"],
    "SOUS-EVALUE",
    "SUR-EVALUE"
)

# SIDEBAR — filtres à gauche
st.sidebar.header("Filtres")

penalty_seulement = st.sidebar.checkbox("Tireurs de penalties seulement")

position_choisie = st.sidebar.selectbox(
    "Position",
    ["Toutes", "F", "M", "D", "G"]
)

budget = st.sidebar.slider(
    "Budget maximum (M)",
    min_value=5.0,
    max_value=12.0,
    value=12.0,
    step=0.5
)

seuil = st.sidebar.slider(
    "Choisi par combien de managers",
    min_value=0.0,
    max_value=100.0,
    value=50.0,
    step=1.0
)

pays_choisie = st.sidebar.selectbox(
    "Pays",
    ["Tous"] + sorted(df["team"].unique().tolist())
)

groupe_choisi = st.sidebar.selectbox(
    "Groupe",
    ["Tous"] + sorted(df["group"].dropna().unique().tolist())
)

difficulty_choisi = st.sidebar.selectbox(
    "Difficulty",
    ["Toutes"] + sorted(df["difficulty"].dropna().unique().tolist())
)

favori_filtre = st.sidebar.selectbox(
    "Statut favori",
    ["Tous", "strong", "likely", "unclear", "none"]
)

# Appliquer les filtres
df_filtre = df.copy()

if penalty_seulement:
    df_filtre = df_filtre[df_filtre["is_penalty_taker"] == True]

if position_choisie != "Toutes":
    df_filtre = df_filtre[df_filtre["position"] == position_choisie]

df_filtre = df_filtre[df_filtre["price"] <= budget]

df_filtre = df_filtre[df_filtre["owned_percentage"] <= seuil]

if pays_choisie != "Tous":
    df_filtre = df_filtre[df_filtre["team"] == pays_choisie]

if groupe_choisi != "Tous":
    df_filtre = df_filtre[df_filtre["group"] == groupe_choisi]

if difficulty_choisi != "Toutes":
    df_filtre = df_filtre[df_filtre["difficulty"] == difficulty_choisi]

if favori_filtre != "Tous":
    df_filtre = df_filtre[df_filtre["is_favorite"] == favori_filtre]

# CONTENU PRINCIPAL
st.header("Joueurs")
st.dataframe(df_filtre[["name", "team", "group", "difficulty", "position", "price", "total_score", "score_valeur", "statut", "owned_percentage"]])

# Graphique
st.header("Score valeur")
df_tri = df_filtre.sort_values("score_valeur", ascending=False)
fig = px.bar(df_tri, x="name", y="score_valeur", color="position")
st.plotly_chart(fig)

# Joueurs sous-évalués
st.header("Joueurs sous-évalués")
st.dataframe(joueurs_sous_evalues(df_filtre)[["name", "team", "group", "difficulty", "position", "price", "total_score", "score_valeur"]])