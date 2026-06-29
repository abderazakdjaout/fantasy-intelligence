import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os
from itertools import combinations

sys.path.append(os.path.dirname(__file__))
from analysis import top_joueur_par_position, joueurs_budget, comparer_joueurs, joueurs_sous_evalues

def colorier_fdr(val):
    if val == 1:
        return "background-color: #00d2ff; color: black"
    elif val == 2:
        return "background-color: #00ff85; color: black"
    elif val == 3:
        return "background-color: #f5c400; color: black"
    elif val == 4:
        return "background-color: #ff8c00; color: black"
    elif val == 5:
        return "background-color: #ff0000; color: white"
    return ""

st.title("⚽ Fantasy Football Intelligence")
st.subheader("Coupe du Monde 2026")

df = pd.read_csv("data/raw/players_sofascore.csv")
df_groups = pd.read_csv("data/raw/groups.csv")
df = df.merge(df_groups, on="team", how="left")
df_strength = pd.read_csv("data/raw/group_strength.csv")
df = df.merge(df_strength, on="group", how="left")
df_penalties = pd.read_csv("data/raw/penalty_takers.csv")
df = df.merge(df_penalties[["name", "is_penalty_taker", "penalty_order"]], on="name", how="left")
df["is_penalty_taker"] = df["is_penalty_taker"].fillna(False)
df["penalty_order"] = df["penalty_order"].fillna(0).astype(int)

df_dates = pd.read_csv("data/raw/match_dates_r1.csv")
df = df.merge(df_dates[["team", "match_date_r1", "match_time_et", "opponent_r1"]], on="team", how="left")

df_fdr = pd.read_csv("data/raw/fdr.csv")
df = df.merge(df_fdr, on="team", how="left")

df_knockout = pd.read_csv("data/raw/parcours_knockout.csv")
df_knockout["score_parcours"] = (
    df_knockout["prob_last16"] +
    df_knockout["prob_quarts"] +
    df_knockout["prob_semis"] +
    df_knockout["prob_finale"] +
    df_knockout["prob_winner"]
).round(2)
df = df.merge(df_knockout, on="team", how="left")

def charger_stats(fichier, suffixe):
    df_s = pd.read_csv(fichier)
    df_agg = df_s.groupby("name").agg({
        "goals": "sum", "assists": "sum", "yellowCard": "sum", "redCard": "sum",
        "cleanSheet": "sum", "rating": "mean", "minutesPlayed": "sum", "keyPass": "sum",
        "interceptions": "sum", "wonTackles": "sum", "duelsWon": "sum", "duelsTotal": "sum",
        "passesCompleted": "sum", "passesTotal": "sum", "wasFouled": "sum", "dispossessed": "sum",
        "offsides": "sum", "dribblesWon": "sum", "dribblesTotal": "sum", "longBalls": "sum",
        "totalClearances": "sum", "blockedShots": "sum", "penaltyWon": "sum", "penaltyScored": "sum",
        "penaltyMissed": "sum", "penaltyCommitted": "sum", "penaltySaved": "sum",
        "savedShotsInside": "sum", "savedShotsOutside": "sum", "runsOut": "sum", "punches": "sum"
    }).reset_index()
    s = suffixe
    df_agg.columns = ["name", f"goals_{s}", f"assists_{s}", f"yellow_{s}", f"red_{s}",
                      f"cleansheet_{s}", f"rating_{s}", f"minutes_{s}", f"keypasses_{s}",
                      f"interceptions_{s}", f"tackles_{s}", f"duels_won_{s}", f"duels_total_{s}",
                      f"passes_completed_{s}", f"passes_total_{s}", f"was_fouled_{s}",
                      f"dispossessed_{s}", f"offsides_{s}", f"dribbles_won_{s}", f"dribbles_total_{s}",
                      f"long_balls_{s}", f"clearances_{s}", f"blocked_shots_{s}", f"penalty_won_{s}",
                      f"penalty_scored_{s}", f"penalty_missed_{s}", f"penalty_committed_{s}",
                      f"penalty_saved_{s}", f"saves_inside_{s}", f"saves_outside_{s}",
                      f"runs_out_{s}", f"punches_{s}"]
    return df_agg

df = df.merge(charger_stats("data/raw/player_stats_r1.csv", "r1"), on="name", how="left")
df = df.merge(charger_stats("data/raw/player_stats_r2.csv", "r2"), on="name", how="left")
df = df.merge(charger_stats("data/raw/player_stats_r3.csv", "r3"), on="name", how="left")
df = df.loc[:, ~df.columns.duplicated()].copy().reset_index(drop=True)

for s in ["r1", "r2", "r3"]:
    df[f"pass_ratio_{s}"] = (df[f"passes_completed_{s}"] / df[f"passes_total_{s}"]).fillna(0).round(2)
    df[f"dribble_ratio_{s}"] = (df[f"dribbles_won_{s}"] / df[f"dribbles_total_{s}"]).fillna(0).round(2)
    df[f"duel_ratio_{s}"] = (df[f"duels_won_{s}"] / df[f"duels_total_{s}"]).fillna(0).round(2)
    df[f"minutes_{s}"] = df[f"minutes_{s}"].fillna(0)

df["points_par_but"] = df["position"].map({"D": 6, "M": 5, "F": 4, "G": 6})

df["score_plancher_r1"] = (
    (df["minutes_r1"].fillna(0) / 90) * 2 +
    df["pass_ratio_r1"].fillna(0) * 3 +
    df["keypasses_r1"].fillna(0) * 1 +
    df["tackles_r1"].fillna(0) * 1 +
    df["interceptions_r1"].fillna(0) * 1 +
    df["long_balls_r1"].fillna(0) * 1 +
    df["clearances_r1"].fillna(0) * 1
).round(1)

df["bonus_cleansheet"] = np.where(df["position"].isin(["D", "G"]), df["cleansheet_r1"].fillna(0) * 4, 0)

df["score_explosif_r1"] = (
    df["goals_r1"].fillna(0) * df["points_par_but"] +
    df["assists_r1"].fillna(0) * 3 +
    df["dribbles_won_r1"].fillna(0) * 1 +
    df["bonus_cleansheet"]
).round(1)

df["score_plafond_r1"] = (df["score_plancher_r1"] + df["score_explosif_r1"]).round(1)

def pts_plancher_round(df, s):
    valide = (df[f"minutes_{s}"].fillna(0) >= 60).astype(float)
    pts_min = np.where(df[f"minutes_{s}"].fillna(0) >= 60, 2,
              np.where(df[f"minutes_{s}"].fillna(0) > 0, 1, 0))
    pts_passes = np.where(
        (df[f"passes_total_{s}"].fillna(0) >= 40) & (df[f"pass_ratio_{s}"].fillna(0) >= 0.90), 1, 0)
    pts_duels = np.where(
        (df[f"duels_total_{s}"].fillna(0) >= 3) & (df[f"duel_ratio_{s}"].fillna(0) >= 0.50), 1, 0)
    pts_dribbles = np.where(
        (df[f"dribbles_total_{s}"].fillna(0) >= 3) & (df[f"dribble_ratio_{s}"].fillna(0) >= 0.60), 1, 0)
    pts_tackles = (df[f"tackles_{s}"].fillna(0) // 3)
    pts_interceptions = (df[f"interceptions_{s}"].fillna(0) // 3)
    pts_keypasses = (df[f"keypasses_{s}"].fillna(0) // 2)
    pts_clearances = (df[f"clearances_{s}"].fillna(0) // 5)
    pts_long_balls = np.where(df[f"long_balls_{s}"].fillna(0) >= 3, 1, 0)
    return (pts_min + pts_passes + pts_duels + pts_dribbles +
            pts_tackles + pts_interceptions + pts_keypasses +
            pts_clearances + pts_long_balls) * valide

def pts_explosif_round(df, s):
    valide = (df[f"minutes_{s}"].fillna(0) >= 60).astype(float)
    bonus_cs = np.where(df["position"].isin(["D", "G"]),
                        df[f"cleansheet_{s}"].fillna(0) * 4, 0)
    return (
        df[f"goals_{s}"].fillna(0) * df["points_par_but"] +
        df[f"assists_{s}"].fillna(0) * 3 +
        df[f"dribbles_won_{s}"].fillna(0) * 1 +
        bonus_cs
    ) * valide

df["rounds_valides"] = (
    (df["minutes_r1"].fillna(0) >= 60).astype(int) +
    (df["minutes_r2"].fillna(0) >= 60).astype(int) +
    (df["minutes_r3"].fillna(0) >= 60).astype(int)
)

df["score_plancher"] = np.where(
    df["rounds_valides"] > 0,
    ((pts_plancher_round(df, "r1") + pts_plancher_round(df, "r2") + pts_plancher_round(df, "r3")) / df["rounds_valides"]).round(1),
    0
)

df["score_explosif"] = np.where(
    df["rounds_valides"] > 0,
    ((pts_explosif_round(df, "r1") + pts_explosif_round(df, "r2") + pts_explosif_round(df, "r3")) / df["rounds_valides"]).round(1),
    0
)

df["score_plafond"] = (df["score_plancher"] + df["score_explosif"]).round(1)
df["valeur_totale"] = (df["score_plafond"] * df["score_parcours"]).round(1)

df["score_valeur"] = df["total_score"] / df["price"]
df_joue = df[df["minutes_r1"] > 0]
moyennes = df_joue.groupby("position")["score_valeur"].mean()
df["moyenne_position"] = df["position"].map(moyennes)
df["statut"] = np.where(
    df["minutes_r1"] > 0,
    np.where(df["score_valeur"] > df["moyenne_position"], "SOUS-EVALUE", "SUR-EVALUE"),
    "PAS JOUÉ"
)

# SIDEBAR
st.sidebar.header("Filtres")
date_choisie = st.sidebar.selectbox("Date du match R1", ["Toutes"] + sorted(df["match_date_r1"].dropna().unique().tolist()))
recherche = st.sidebar.text_input("Rechercher un joueur")
position_choisie = st.sidebar.selectbox("Position", ["Toutes", "F", "M", "D", "G"])
budget = st.sidebar.slider("Budget maximum (M)", min_value=5.0, max_value=12.0, value=12.0, step=0.5)
seuil = st.sidebar.slider("Choisi par combien de managers", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
pays_choisie = st.sidebar.multiselect("Pays", options=sorted(df["team"].unique().tolist()), default=[])
groupe_choisi = st.sidebar.selectbox("Groupe", ["Tous"] + sorted(df["group"].dropna().unique().tolist()))
difficulty_choisi = st.sidebar.selectbox("Difficulté", ["Toutes"] + sorted(df["difficulty"].dropna().unique().tolist()))
favori_filtre = st.sidebar.selectbox("Statut favori", ["Tous", "strong", "likely", "unclear", "none"])
penalty_filtre = st.sidebar.selectbox("Tireur de penalty", ["Tous", "Tireur principal (1)", "Backup (2)", "Tous les tireurs"])
joueurs_compares = st.sidebar.multiselect("Comparer des joueurs", options=df["name"].tolist(), default=[])
fdr_max = st.sidebar.slider("FDR R1 maximum", min_value=1, max_value=5, value=5, step=1)
fdr_r2_max = st.sidebar.slider("FDR R2 maximum", min_value=1, max_value=5, value=5, step=1)
fdr_r3_max = st.sidebar.slider("FDR R3 maximum", min_value=1, max_value=5, value=5, step=1)

# Sélection des colonnes
toutes_colonnes = ["name", "team", "position", "price", "total_score", "score_parcours",
                   "owned_percentage", "penalty_order", "statut",
                   "score_plancher", "score_explosif", "score_plafond", "valeur_totale", "rounds_valides",
                   "score_plancher_r1", "score_plafond_r1",
                   "fdr_r1", "fdr_r2", "fdr_r3",
                   "goals_r1", "assists_r1", "rating_r1", "minutes_r1",
                   "goals_r2", "assists_r2", "rating_r2", "minutes_r2",
                   "goals_r3", "assists_r3", "rating_r3", "minutes_r3",
                   "yellow_r1", "red_r1", "cleansheet_r1", "keypasses_r1",
                   "interceptions_r1", "tackles_r1", "pass_ratio_r1",
                   "duels_won_r1", "duels_total_r1", "duel_ratio_r1",
                   "dribbles_won_r1", "dribbles_total_r1", "dribble_ratio_r1",
                   "passes_completed_r1", "passes_total_r1",
                   "long_balls_r1", "clearances_r1",
                   "yellow_r2", "red_r2", "cleansheet_r2", "keypasses_r2",
                   "interceptions_r2", "tackles_r2", "pass_ratio_r2",
                   "duels_won_r2", "duels_total_r2", "duel_ratio_r2",
                   "dribbles_won_r2", "dribbles_total_r2", "dribble_ratio_r2",
                   "passes_completed_r2", "passes_total_r2",
                   "long_balls_r2", "clearances_r2",
                   "yellow_r3", "red_r3", "cleansheet_r3", "keypasses_r3",
                   "interceptions_r3", "tackles_r3", "pass_ratio_r3",
                   "duels_won_r3", "duels_total_r3", "duel_ratio_r3",
                   "dribbles_won_r3", "dribbles_total_r3", "dribble_ratio_r3",
                   "passes_completed_r3", "passes_total_r3",
                   "long_balls_r3", "clearances_r3"]

colonnes_choisies = st.sidebar.multiselect(
    "Colonnes à afficher",
    options=toutes_colonnes,
    default=["name", "team", "position", "price", "total_score", "score_parcours",
             "score_plancher", "score_explosif", "score_plafond", "valeur_totale",
             "goals_r1", "assists_r1", "rating_r1",
             "goals_r2", "assists_r2", "rating_r2",
             "goals_r3", "assists_r3", "rating_r3"]
)

# FILTRES
df_filtre = df.copy()
if date_choisie != "Toutes":
    df_filtre = df_filtre[df_filtre["match_date_r1"] == date_choisie]
if recherche:
    df_filtre = df_filtre[df_filtre["name"].str.contains(recherche, case=False, na=False)]
if position_choisie != "Toutes":
    df_filtre = df_filtre[df_filtre["position"] == position_choisie]
df_filtre = df_filtre[df_filtre["price"] <= budget]
df_filtre = df_filtre[df_filtre["owned_percentage"] <= seuil]
if len(pays_choisie) > 0:
    df_filtre = df_filtre[df_filtre["team"].isin(pays_choisie)]
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
    st.dataframe(
        comparer_joueurs(df, joueurs_compares)[["name", "team", "position", "price",
               "total_score", "statut", "fdr_r1", "fdr_r2", "fdr_r3",
               "score_plancher", "score_explosif", "score_plafond", "valeur_totale",
               "goals_r1", "assists_r1", "rating_r1", "minutes_r1",
               "goals_r2", "assists_r2", "rating_r2", "minutes_r2",
               "goals_r3", "assists_r3", "rating_r3", "minutes_r3",
               "yellow_r1", "red_r1", "cleansheet_r1", "keypasses_r1",
               "interceptions_r1", "tackles_r1", "pass_ratio_r1",
               "yellow_r2", "red_r2", "cleansheet_r2", "keypasses_r2",
               "interceptions_r2", "tackles_r2", "pass_ratio_r2",
               "yellow_r3", "red_r3", "cleansheet_r3", "keypasses_r3",
               "interceptions_r3", "tackles_r3", "pass_ratio_r3"]].style.map(
            colorier_fdr, subset=["fdr_r1", "fdr_r2", "fdr_r3"]
        )
    )
    csv_export = comparer_joueurs(df, joueurs_compares).to_csv(index=False)
    st.download_button(label="Télécharger cette comparaison en CSV", data=csv_export, file_name="comparaison_joueurs.csv", mime="text/csv")

df_filtre = df_filtre[df_filtre["fdr_r1"] <= fdr_max]
df_filtre = df_filtre[df_filtre["fdr_r2"] <= fdr_r2_max]
df_filtre = df_filtre[df_filtre["fdr_r3"] <= fdr_r3_max]

# MON ÉQUIPE
st.sidebar.header("Mon équipe")
equipe_sauvegardee = []
if os.path.exists("data/raw/mon_equipe.csv"):
    equipe_sauvegardee = pd.read_csv("data/raw/mon_equipe.csv")["name"].tolist()
mon_equipe = st.sidebar.multiselect("Sélectionne tes 15 joueurs", options=df["name"].tolist(), default=equipe_sauvegardee)
if st.sidebar.button("Sauvegarder mon équipe"):
    pd.DataFrame({"name": mon_equipe}).to_csv("data/raw/mon_equipe.csv", index=False)
    st.sidebar.success("Équipe sauvegardée !")

if len(mon_equipe) > 0:
    st.header("📋 Mon équipe")
    df_mon_equipe = df[df["name"].isin(mon_equipe)].copy()
    budget_utilise = df_mon_equipe["price"].sum()
    st.write(f"Budget utilisé : {budget_utilise}M sur 15 joueurs sélectionnés ({len(mon_equipe)}/15)")

    alertes_fdr = df_mon_equipe[df_mon_equipe["fdr_r2"] >= 4]
    if len(alertes_fdr) > 0:
        st.warning(f"⚠️ {len(alertes_fdr)} joueur(s) avec un FDR R2 difficile : " + ", ".join(alertes_fdr["name"].tolist()))
    alertes_perf = df_mon_equipe[(df_mon_equipe["minutes_r1"] > 0) & (df_mon_equipe["rating_r1"] < 6.5)]
    if len(alertes_perf) > 0:
        st.warning(f"⚠️ {len(alertes_perf)} joueur(s) avec un rating R1 faible : " + ", ".join(alertes_perf["name"].tolist()))
    pas_joue = df_mon_equipe[df_mon_equipe["statut"] == "PAS JOUÉ"]
    if len(pas_joue) > 0:
        st.info(f"ℹ️ {len(pas_joue)} joueur(s) n'ont pas encore joué : " + ", ".join(pas_joue["name"].tolist()))

    st.dataframe(
        df_mon_equipe[["name", "team", "position", "price", "total_score", "score_parcours",
                       "score_plancher", "score_explosif", "score_plafond", "valeur_totale",
                       "rounds_valides", "fdr_r1", "fdr_r2", "fdr_r3",
                       "goals_r1", "assists_r1", "rating_r1", "minutes_r1",
                       "goals_r2", "assists_r2", "rating_r2", "minutes_r2",
                       "goals_r3", "assists_r3", "rating_r3", "minutes_r3",
                       "statut"]].style.map(
            colorier_fdr, subset=["fdr_r1", "fdr_r2", "fdr_r3"]
        )
    )

# SIMULATEUR
st.sidebar.header("Simulateur de budget")
joueurs_a_vendre = st.sidebar.multiselect("Joueurs à vendre", options=df["name"].tolist(), key="vendre")
banque_actuelle = st.sidebar.number_input("Banque actuelle (M)", value=2.5, step=0.5)
candidats_premium = st.sidebar.multiselect("Tes joueurs favoris à comparer 2 par 2", options=df["name"].tolist(), key="premium")
prix_3e_joueur_cible = st.sidebar.number_input("Prix visé pour le 3e joueur (M)", value=5.0, step=0.5)

if len(joueurs_a_vendre) > 0 and len(candidats_premium) >= 2:
    st.header("🧮 Simulateur de budget — paires favorites")
    budget_total = df[df["name"].isin(joueurs_a_vendre)]["price"].sum() + banque_actuelle
    st.write(f"Budget total disponible : {budget_total}M")
    candidats_df = df[df["name"].isin(candidats_premium)][["name", "price"]]
    resultats_paires = []
    for paire in combinations(candidats_df.itertuples(), 2):
        prix_paire = sum(p.price for p in paire)
        noms_paire = " + ".join([p.name for p in paire])
        budget_3e = budget_total - prix_paire
        resultats_paires.append({
            "paire": noms_paire,
            "prix_paire": round(prix_paire, 1),
            "budget_3e_joueur": round(budget_3e, 1),
            "vente_necessaire": round(prix_3e_joueur_cible - budget_3e, 1)
        })
    df_paires = pd.DataFrame(resultats_paires).sort_values("budget_3e_joueur", ascending=False)
    st.dataframe(df_paires)

# CONTENU PRINCIPAL
st.header("Joueurs")
st.write(f"{df_filtre.shape[0]} joueurs trouvés")
st.dataframe(
    df_filtre[colonnes_choisies].style.map(
        colorier_fdr, subset=[c for c in ["fdr_r1", "fdr_r2", "fdr_r3"] if c in colonnes_choisies]
    )
)

st.header("Score valeur")
df_tri = df_filtre.sort_values("score_valeur", ascending=False)
fig = px.bar(df_tri, x="name", y="score_valeur", color="position")
st.plotly_chart(fig)

st.header("Joueurs sous-évalués")
st.write(f"{joueurs_sous_evalues(df_filtre).shape[0]} joueurs trouvés")
st.dataframe(joueurs_sous_evalues(df_filtre)[["name", "team", "group", "difficulty", "position", "price", "total_score", "score_valeur"]])