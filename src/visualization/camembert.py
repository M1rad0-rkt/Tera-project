import pandas as pd
import matplotlib.pyplot as plt


# Couleurs associées à chaque catégorie -> adapte les clés si tes libellés diffèrent
COULEURS_CATEGORIE = {
    "Bon": "#2ecc71",
    "Modéré": "#f1c40f",
    "Mauvais": "#e74c3c",
    "Très mauvais": "#8e44ad",
}


def plot_pm25_category_pie(df, start_date=None, end_date=None, sensors=None):
    """Affiche un camembert de la répartition du temps par catégorie de
    qualité de l'air (colonne 'pm25_category'), sur la période et/ou les
    capteurs choisis.

    Parameters
    ----------
    df : DataFrame contenant au minimum les colonnes
         'pm25_category', 'time', et 'id_install' (si filtre par capteur)
    start_date, end_date : bornes de filtrage temporel (optionnel, "YYYY-MM-DD")
    sensors : liste d'id_install à inclure (optionnel, tous par défaut)

    Retourne une figure Matplotlib, ou None si aucune donnée disponible.
    """
    fa = df.copy()
    fa["time"] = pd.to_datetime(fa["time"], errors="coerce")
    fa = fa.dropna(subset=["time"])

    if start_date:
        fa = fa[fa["time"] >= pd.to_datetime(start_date)]
    if end_date:
        fa = fa[fa["time"] <= pd.to_datetime(end_date)]

    if sensors:
        fa = fa[fa["id_install"].isin(sensors)]

    fa = fa.dropna(subset=["pm25_category"])

    if fa.empty:
        return None

    repartition = fa["pm25_category"].value_counts()

    if repartition.empty:
        return None

    # Couleurs dans le même ordre que les catégories présentes ;
    # catégorie inconnue -> gris par défaut, pour ne jamais planter
    couleurs = [COULEURS_CATEGORIE.get(cat, "#95a5a6") for cat in repartition.index]

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        repartition,
        labels=repartition.index,
        autopct="%1.1f%%",
        colors=couleurs,
        startangle=90,
    )

    periode = ""
    if start_date or end_date:
        periode = f"\n{start_date or '...'} - {end_date or '...'}"
    ax.set_title(f"Répartition par catégorie de qualité de l'air{periode}")
    ax.axis("equal")

    fig.tight_layout()
    return fig