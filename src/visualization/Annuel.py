import matplotlib.pyplot as plt

SEASON_ORDER = ["Hiver", "Printemps", "Été", "Automne"]
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


def _month_label(month: int) -> str:
    return ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"][month - 1]


def _category_line(ax, plot_df):
    if "pm25_category" not in plot_df.columns or plot_df["pm25_category"].dropna().empty:
        return

    category = plot_df["pm25_category"].mode().iloc[0]
    color_map = {
        "Mauvais": "red",
        "Modéré": "yellow",
        "Bon": "green",
    }
    color = color_map.get(category, "red")
    label = category
    y_value = plot_df["pm25"].mean()
    ax.axhline(y=y_value, color=color, alpha=1, linestyle="--", label=label)


def plot_annual_evolution(df, year, season=None):
    """Renvoie une figure matplotlib de l'évolution annuelle de PM1 et PM2.5.

    Args:
        df: DataFrame contenant la colonne `time` et les colonnes `pm1` et `pm25`.
        year: Année à analyser.
        season: Saison facultative à filtrer (Hiver, Printemps, Été, Automne).

    Retourne:
        matplotlib.figure.Figure ou None si aucune donnée.
    """
    if df is None or df.empty:
        return None

    plot_df = df.copy()
    plot_df = plot_df[plot_df["time"].dt.year == year].copy()
    if plot_df.empty:
        return None

    plot_df["season"] = plot_df["time"].dt.month.map(SEASON_MAP)

    if season:
        plot_df = plot_df[plot_df["season"] == season].copy()
        if plot_df.empty:
            return None

        monthly_mean = (
            plot_df
            .groupby(plot_df["time"].dt.month)[["pm1", "pm25"]]
            .mean()
            .sort_index()
        )
        if monthly_mean.empty:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot([_month_label(m) for m in monthly_mean.index], monthly_mean["pm1"], marker="o", label="PM1")
        ax.plot([_month_label(m) for m in monthly_mean.index], monthly_mean["pm25"], marker="o", label="PM2.5")
        _category_line(ax, plot_df)
        ax.set_title(f"Évolution mensuelle de {season} {year}")
        ax.set_xlabel("Mois")
        ax.set_ylabel("Concentration moyenne (µg/m³)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        return fig

    season_mean = (
        plot_df
        .groupby("season")[["pm1", "pm25"]]
        .mean()
        .reindex(SEASON_ORDER)
    )
    season_mean = season_mean.dropna(how="all")
    if season_mean.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(season_mean.index, season_mean["pm1"], marker="o", label="PM1")
    ax.plot(season_mean.index, season_mean["pm25"], marker="o", label="PM2.5")
    _category_line(ax, plot_df)
    ax.set_title(f"Évolution saisonnière de {year}")
    ax.set_xlabel("Saison")
    ax.set_ylabel("Concentration moyenne (µg/m³)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig