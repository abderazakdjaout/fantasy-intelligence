import pandas as pd
import numpy as np
from analysis import top_joueur_par_position, joueurs_budget, comparer_joueurs, joueurs_sous_evalues

# Lire le fichier CSV
df = pd.read_csv("data/raw/players.csv")

# Afficher les 5 premiers joueurs
print("=== Les 5 premiers joueurs ===")
print(df.head())

# Afficher les dimensions du tableau
print("\n=== Dimensions ===")
print(f"{df.shape[0]} joueurs, {df.shape[1]} colonnes")

# Afficher les positions disponibles
print("\n=== Positions disponibles ===")
print(df["position"].unique())

# Afficher les joueurs par position
print("\n=== Nombre de joueurs par position ===")
print(df["position"].value_counts())

# Afficher le joueur le plus cher
print("\n=== Joueur le plus cher ===")
print(df[df["price"] == df["price"].max()][["name", "team", "position", "price"]])

# Afficher les joueurs à moins de 7.0
print("\n=== Joueurs à moins de 7.0M ===")
print(df[df["price"] < 7.0][["name", "team", "position", "price"]])

#Afficher le pays des joueur
print("\n=== Joueurs venant de la france ===")
print(df[df["team"] == 'France'][["name", "position", "price"]])

#Afficher les joueurs par categorie de leur pays
for team in df["team"].unique():
    print(f"\n=== {team} ===")
    print(df[df["team"] == team][["name", "position", "price"]])

#Afficher tout les joeur par prix du plus cher au moins cher
print("\n=== Joueurs du plus cher au moins cher ===")
print(df[df["position"] == 'ATT'].sort_values("price", ascending = False))

#Creer une nouvelle colonne point par prix
df["score_valeur"] = df["points"] / df["price"]
print(df["score_valeur"])

#On veut voir le classement des joueurs par score valeur — du meilleur rapport qualité/prix au moins bon.
print(df.sort_values("score_valeur", ascending = False))

#Afficher les joueurs par categorie de leur pays
for position in df["position"].unique():
    print(f"\n=== {position} ===")
    print(df[df["position"] == position].sort_values("score_valeur", ascending = False))

#Afficher les joueurs dont le score_valeur est au-dessus de la moyenne de leur position.
moyennes = df.groupby("position")["score_valeur"].mean()

df["moyenne_position"] = df["position"].map(moyennes)

df["statut"] = np.where(
    df["score_valeur"] > df["moyenne_position"],
    "SOUS-EVALUE",
    "SUR-EVALUE"
)

print(df)
print(df[["position","name", "price", "score_valeur", "statut"]])



print(top_joueur_par_position(df, "ATT"))
print(joueurs_budget(df, 8.0))
print(comparer_joueurs (df, ["Kylian Mbappé", "Erling Haaland", "Bukayo Saka"]))
print(joueurs_sous_evalues(df))


