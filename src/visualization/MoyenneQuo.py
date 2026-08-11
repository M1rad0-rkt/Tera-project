import pandas as pd
import matplotlib.pyplot as plt


def plot_daily_hourly_mean(df, start_date="2024-01-01", end_date="2026-12-31"):
    """Calcule la moyenne par heure sur tous les jours entre start_date et end_date.

    Pour chaque heure (0-23) on calcule la moyenne des valeurs horaires
    (moyenne des jours) pour `pm1` et `pm25`.
    Retourne une figure Matplotlib ou None si aucune donnée.
    """
    fa = df.copy()
    fa["time"] = pd.to_datetime(fa["time"], errors="coerce")
    fa = fa.dropna(subset=["time"])

    # Filtrer la période
    if start_date:
        fa = fa[fa["time"] >= pd.to_datetime(start_date)]
    if end_date:
        fa = fa[fa["time"] <= pd.to_datetime(end_date)]

    if fa.empty:
        return None

    # Extraire date et hour
    fa["date_only"] = fa["time"].dt.date
    fa["hour"] = fa["time"].dt.hour

    # Calculer la moyenne par jour et par heure (pour normaliser si plusieurs mesures par heure)
    per_day_hour = (
        fa.groupby(["date_only", "hour"])[["pm1", "pm25"]]
          .mean()
          .reset_index()
    )

    # Maintenant calculer la moyenne par heure sur tous les jours
    hourly_mean = (
        per_day_hour.groupby("hour")[['pm1', 'pm25']]
            .mean()
            .reindex(range(24))
    )

    # Si toutes les heures sont NaN -> aucun résultat
    if hourly_mean[['pm1', 'pm25']].dropna(how='all').empty:
        return None

    # Tracer
    plt.figure(figsize=(10, 5))
    plt.plot(hourly_mean.index, hourly_mean['pm1'], marker='o', label='PM1 (moyenne horaire)')
    plt.plot(hourly_mean.index, hourly_mean['pm25'], marker='o', label='PM2.5 (moyenne horaire)')
    plt.xticks(range(24))
    plt.xlabel('Heure du jour')
    plt.ylabel('Concentration moyenne')
    plt.title(f'Moyenne horaire quotidienne (par heure)\n{start_date} - {end_date}')
    plt.grid(alpha=0.3)
    plt.legend()
    fig3 = plt.gcf()
    fig3.tight_layout()

    return fig3
