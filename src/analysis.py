import pandas as pd
import numpy as np

# Fonction pour savoir quel joueur a le meilleur score_valeur par position
def top_joueur_par_position(df, position):
    """
    Retourne les meilleurs joueurs dune position voulu.
    
    Paramètres:
        df : DataFrame pandas avec les joueurs
    
    Retourne:
        DataFrame filtré et trié
    """
    resultat = df[df["position"] == position].sort_values("score_valeur", ascending=False)
    
    return resultat

#Fonction budget par rapport au prix des joueur
def joueurs_budget (df, budget_max):
    """
    Retourne les joueurs dont le prix est inferieur
    au budget.
    
    Paramètres:
        df : DataFrame pandas avec les joueurs
    
    Retourne:
        DataFrame filtré et trié
    """
    resultat = df[df["price"] <= budget_max].sort_values("score_valeur", ascending=False)

    return resultat

#Fonction qui prend une liste de noms de joueurs et affiche leurs stats côte à côte.
def comparer_joueurs (df, liste_de_noms):
    """
    Retourne les joueurs quon veut comparer
    entre eux.
    
    Paramètres:
        df : DataFrame pandas avec les joueurs
    
    Retourne:
        DataFrame filtré et trié
    """
    resultat = df[df["name"].isin(liste_de_noms)]

    return resultat

#Fonction pour vior les meilleurs joueurs sous-evalue
def joueurs_sous_evalues(df):
    """
    Retourne les joueurs dont le statut est SOUS-EVALUE
    triés par score_valeur décroissant.
    
    Paramètres:
        df : DataFrame pandas avec les joueurs
    
    Retourne:
        DataFrame filtré et trié
    """
    resultat = df[df["statut"] == "SOUS-EVALUE"].sort_values("score_valeur", ascending=False)

    return resultat