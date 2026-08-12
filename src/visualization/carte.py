import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# Bornes géographiques de l'image de fond -> À AJUSTER selon ton image réelle
LON_MIN, LON_MAX = 47.05, 47.12
LAT_MIN, LAT_MAX = -21.48, -21.42

# Chemin vers l'image de fond de Fianarantsoa.
# Construit par rapport à l'emplacement de CE fichier (pas du dossier de lancement),
# donc ça fonctionne peu importe d'où tu lances "streamlit run app.py".
MAP_IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/raw/fianarantsoa.png")

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


def plot_sensor_map(df, start_date="2024-01-01", end_date="2026-12-31", sensors=None, season=None):
    """Affiche la position des capteurs sur la carte de Fianarantsoa,
    colorés selon la moyenne de PM2.5 sur la période/le jour/la saison choisis.

    Même logique de filtrage que plot_daily_hourly_mean : bornes de dates
    avec valeurs par défaut couvrant toute la plage du dataset. Pour
    afficher la qualité de l'air d'un jour précis, passe la même date
    en start_date et end_date.

    Les coordonnées de chaque capteur sont calculées directement depuis
    `df` (moyenne des lat/lon par id_install), pas depuis une table
    codée en dur -> reste à jour automatiquement si de nouveaux
    capteurs sont ajoutés au dataset.

    Parameters
    ----------
    df : DataFrame contenant au minimum les colonnes
         'id_install', 'latitude', 'longitude', 'pm25', 'time'
    start_date, end_date : bornes de filtrage temporel ("YYYY-MM-DD")
    sensors : liste d'id_install à afficher (optionnel, tous par défaut)
    season : "Été", "Automne", "Hiver" ou "Printemps" (optionnel, aucun filtre par défaut)

    Retourne une figure Matplotlib, ou None si aucune donnée disponible.
    """
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

    if fa.empty:
        return None

    # Position moyenne de chaque capteur (au cas où plusieurs lignes légèrement différentes)
    latitude_mean = fa.groupby(fa["id_install"])["latitude"].mean().sort_index()
    longitude_mean = fa.groupby(fa["id_install"])["longitude"].mean().sort_index()

    # Moyenne de PM2.5 par capteur sur la période filtrée
    pm25_mean = fa.groupby(fa["id_install"])["pm25"].mean().sort_index()

    geo_df = pd.DataFrame({
        "latitude": latitude_mean,
        "longitude": longitude_mean,
        "pm25": pm25_mean,
    }).dropna(subset=["latitude", "longitude"])

    if geo_df.empty:
        return None

    # Charge l'image de fond (si absente, la carte s'affiche quand même, sans fond)
    try:
        img = mpimg.imread(MAP_IMAGE_PATH)
    except FileNotFoundError:
        img = None

    fig, ax = plt.subplots(figsize=(10, 8))

    if img is not None:
        ax.imshow(img, extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX])

    sc = ax.scatter(
        geo_df["longitude"], geo_df["latitude"],
        c=geo_df["pm25"], cmap="RdYlGn_r",
        s=220, edgecolors="black", linewidths=1, zorder=5,
    )

    for id_install, row in geo_df.iterrows():
        ax.annotate(
            id_install,
            (row["longitude"], row["latitude"]),
            textcoords="offset points", xytext=(6, 6),
            fontsize=8, fontweight="bold", zorder=6,
        )

    plt.colorbar(sc, ax=ax, label="PM2.5 moyen (µg/m³)")

    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    periode = ""
    if start_date or end_date:
        periode = f"\n{start_date or '...'} - {end_date or '...'}"
    if season:
        periode += f" ({season})"
    ax.set_title(f"Qualité de l'air par capteur - Fianarantsoa{periode}")
    ax.set_aspect("equal")

    fig.tight_layout()
    return fig


def plot_sensor_locations(df):
    """Affiche l'emplacement de tous les capteurs existants sur la carte
    de Fianarantsoa, à partir de la moyenne de latitude/longitude par
    id_install. Pas de filtre temporel ni de couleur par pollution :
    c'est juste la carte des installations.

    Parameters
    ----------
    df : DataFrame contenant au minimum les colonnes
         'id_install', 'latitude', 'longitude'

    Retourne une figure Matplotlib, ou None si aucune donnée disponible.
    """
    if df.empty:
        return None

    latitude_mean = df.groupby(df["id_install"])["latitude"].mean().sort_index()
    longitude_mean = df.groupby(df["id_install"])["longitude"].mean().sort_index()

    geo_df = pd.DataFrame({
        "latitude": latitude_mean,
        "longitude": longitude_mean,
    }).dropna(subset=["latitude", "longitude"])

    if geo_df.empty:
        return None

    # Charge l'image de fond (si absente, la carte s'affiche quand même, sans fond)
    try:
        img = mpimg.imread(MAP_IMAGE_PATH)
    except FileNotFoundError:
        img = None

    fig, ax = plt.subplots(figsize=(10, 8))

    if img is not None:
        ax.imshow(img, extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX])

    ax.scatter(
        geo_df["longitude"], geo_df["latitude"],
        s=150, c="red", edgecolors="black", zorder=5,
    )

    for id_install, row in geo_df.iterrows():
        ax.annotate(
            id_install,
            (row["longitude"], row["latitude"]),
            textcoords="offset points", xytext=(5, 5),
            fontsize=8, fontweight="bold",
        )

    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Installations - Fianarantsoa")
    ax.set_aspect("equal")

    fig.tight_layout()
    return fig