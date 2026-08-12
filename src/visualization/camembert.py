import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Couleurs associées à chaque catégorie -> adapte les clés si tes libellés diffèrent
COULEURS_CATEGORIE = {
    "Bon": "#2ecc71",
    "Modéré": "#f1c40f",
    "Mauvais": "#e74c3c",
    "Très mauvais": "#8e44ad",
}

# Correspondance mois -> saison, identique à celle utilisée dans Annuel.py
SEASON_MAP = {
    1: "Hiver",
    2: "Hiver",
    3: "Printemps",
    4: "Printemps",
    5: "Printemps",
    6: "Été",
    7: "Été",
    8: "Été",
    9: "Automne",
    10: "Automne",
    11: "Automne",
    12: "Hiver",
}

sns.set_theme(style="whitegrid")


def _filtrer(df, start_date, end_date, sensors, season):
    """Filtrage commun aux deux fonctions ci-dessous (date, saison, capteurs)."""
    fa = df.copy()
    fa["time"] = pd.to_datetime(fa["time"], errors="coerce")
    fa = fa.dropna(subset=["time"])

    if start_date:
        fa = fa[fa["time"].dt.date >= pd.to_datetime(start_date).date()]
    if end_date:
        fa = fa[fa["time"].dt.date <= pd.to_datetime(end_date).date()]

    if season:
        fa = fa[fa["time"].dt.month.map(SEASON_MAP) == season]

    if sensors:
        fa = fa[fa["id_install"].isin(sensors)]

    return fa.dropna(subset=["pm25_category"])


def _titre(base, start_date, end_date, season):
    periode = ""
    if start_date or end_date:
        periode = f"\n{start_date or '...'} - {end_date or '...'}"
    if season:
        periode += f" ({season})"
    return f"{base}{periode}"


def plot_pm25_category_bar(df, start_date="2024-01-01", end_date="2026-12-31", sensors=None, season=None):
    """Barres Seaborn de la répartition du temps par catégorie de qualité
    de l'air (colonne 'pm25_category'), sur la période, les capteurs
    et/ou la saison choisis. Alternative recommandée au camembert :
    plus lisible pour comparer des proportions entre catégories.

    Parameters
    ----------
    df : DataFrame contenant au minimum les colonnes
         'pm25_category', 'time', et 'id_install' (si filtre par capteur)
    start_date, end_date : bornes de filtrage temporel ("YYYY-MM-DD")
    sensors : liste d'id_install à inclure (optionnel, tous par défaut)
    season : "Été", "Automne", "Hiver" ou "Printemps" (optionnel)

    Retourne une figure Matplotlib, ou None si aucune donnée disponible.
    """
    fa = _filtrer(df, start_date, end_date, sensors, season)
    if fa.empty:
        return None

    repartition = fa["pm25_category"].value_counts(normalize=True).mul(100)
    if repartition.empty:
        return None

    plot_df = repartition.reset_index()
    plot_df.columns = ["categorie", "pourcentage"]

    couleurs = [COULEURS_CATEGORIE.get(cat, "#95a5a6") for cat in plot_df["categorie"]]

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.barplot(data=plot_df, x="categorie", y="pourcentage", palette=couleurs, ax=ax, hue="categorie", legend=False)

    for i, valeur in enumerate(plot_df["pourcentage"]):
        ax.text(i, valeur + 1, f"{valeur:.1f}%", ha="center", fontsize=9)

    ax.set_ylim(0, max(plot_df["pourcentage"]) + 10)
    ax.set_xlabel("Catégorie de qualité de l'air")
    ax.set_ylabel("Proportion du temps (%)")
    ax.set_title(_titre("Répartition par catégorie de qualité de l'air", start_date, end_date, season))
    fig.tight_layout()
    return fig