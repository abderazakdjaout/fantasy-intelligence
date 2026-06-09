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
df_groups = pd.read_csv("data/raw/groups.csv")
df = df.merge(df_groups, on="team", how="left")
df_strength = pd.read_csv("data/raw/group_strength.csv")
df = df.merge(df_strength, on="group", how="left")
df_penalties = pd.read_csv("data/raw/penalty_takers.csv")
df = df.merge(df_penalties[["name", "is_penalty_taker", "penalty_order"]], on="name", how="left")
df["is_penalty_taker"] = df["is_penalty_taker"].fillna(False)
df["penalty_order"] = df["penalty_order"].fillna(0).astype(int)

# Charger les dates des matchs R1 et joindre
df_dates = pd.read_csv("data/raw/match_dates_r1.csv")
df = df.merge(df_dates[["team", "match_date_r1", "match_time_et", "opponent_r1"]], on="team", how="left")

# Charger le FDR et joindre
df_fdr = pd.read_csv("data/raw/fdr.csv")
df = df.merge(df_fdr, on="team", how="left")

# Calculer les colonnes
df["score_valeur"] = df["total_score"] / df["price"]
moyennes = df.groupby("position")["score_valeur"].mean()
df["moyenne_position"] = df["position"].map(moyennes)
df["statut"] = np.where(
    df["score_valeur"] > df["moyenne_position"],
    "SOUS-EVALUE",
    "SUR-EVALUE"
)

# SIDEBAR
st.sidebar.header("Filtres")

date_choisie = st.sidebar.selectbox(
    "Date du match R1",
    ["Toutes"] + sorted(df["match_date_r1"].dropna().unique().tolist())
)

recherche = st.sidebar.text_input("Rechercher un joueur")

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
    "Difficulté",
    ["Toutes"] + sorted(df["difficulty"].dropna().unique().tolist())
)

favori_filtre = st.sidebar.selectbox(
    "Statut favori",
    ["Tous", "strong", "likely", "unclear", "none"]
)

penalty_filtre = st.sidebar.selectbox(
    "Tireur de penalty",
    ["Tous", "Tireur principal (1)", "Backup (2)", "Tous les tireurs"]
)

joueurs_compares = st.sidebar.multiselect(
    "Comparer des joueurs",
    options=df["name"].tolist(),
    default=[]
)

fdr_max = st.sidebar.slider(
    "FDR R1 maximum",
    min_value=1,
    max_value=5,
    value=5,
    step=1
)

# APPLIQUER LES FILTRES
df_filtre = df.copy()

if date_choisie != "Toutes":
    df_filtre = df_filtre[df_filtre["match_date_r1"] == date_choisie]

if recherche:
    df_filtre = df_filtre[df_filtre["name"].str.contains(recherche, case=False, na=False)]

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

if penalty_filtre == "Tireur principal (1)":
    df_filtre = df_filtre[df_filtre["penalty_order"] == 1]
elif penalty_filtre == "Backup (2)":
    df_filtre = df_filtre[df_filtre["penalty_order"] == 2]
elif penalty_filtre == "Tous les tireurs":
    df_filtre = df_filtre[df_filtre["is_penalty_taker"] == True]

if len(joueurs_compares) >= 2:
    st.header("Comparaison de joueurs")
    st.dataframe(comparer_joueurs(df, joueurs_compares))

df_filtre = df_filtre[df_filtre["fdr_r1"] <= fdr_max]

# CONTENU PRINCIPAL
st.header("Joueurs")
st.write(f"{df_filtre.shape[0]} joueurs trouvés")
st.dataframe(df_filtre[["name", "team", "group", "difficulty", "is_favorite", "position", "price", "total_score", "score_valeur", "statut", "owned_percentage", "penalty_order", "match_date_r1", "match_time_et", "opponent_r1", "fdr_r1"]])
# Graphique
st.header("Score valeur")
df_tri = df_filtre.sort_values("score_valeur", ascending=False)
fig = px.bar(df_tri, x="name", y="score_valeur", color="position")
st.plotly_chart(fig)

# Joueurs sous-évalués
st.header("Joueurs sous-évalués")
st.write(f"{joueurs_sous_evalues(df_filtre).shape[0]} joueurs trouvés")
st.dataframe(joueurs_sous_evalues(df_filtre)[["name", "team", "group", "difficulty", "position", "price", "total_score", "score_valeur"]])