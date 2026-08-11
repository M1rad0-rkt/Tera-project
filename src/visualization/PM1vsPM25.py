import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("data/processed/data_clean.csv")
print(df.head())


def plot_hourly_pm(df, date):
    fa = df.copy()
    fa["time"] = pd.to_datetime(fa["time"], errors="coerce")
    selected_date = pd.to_datetime(date).date()
    fa = fa[fa["time"].dt.date == selected_date]

    if fa.empty:
        return None

    hourly = (
        fa.set_index("time")
          .resample("1h")[["pm1", "pm25"]]
          .mean()
          .reset_index()
    )

    plt.figure(figsize=(10, 5))
    plt.plot(hourly.index, hourly["pm1"], label="PM1",marker='o')
    plt.plot(hourly.index, hourly["pm25"], label="PM2.5",marker='o')
    plt.xticks(range(24))
    plt.xlabel("Heure du jour")
    plt.ylabel("Concentration")
    plt.title(f"Évolution de PM1 et PM2.5 dans le temps")
    plt.legend()
    plt.grid(alpha=0.3)
    fig = plt.gcf()
    fig.tight_layout()

    return fig


def plot_hourly_mean(df, label=""):
    """Affiche la moyenne horaire (par heure sur tous les jours du dataframe)."""
    fa = df.copy()
    fa["time"] = pd.to_datetime(fa["time"], errors="coerce")
    fa = fa.dropna(subset=["time"])
    
    if fa.empty:
        return None
    
    # Extraire l'heure
    fa["hour"] = fa["time"].dt.hour
    
    # Calculer la moyenne par heure
    hourly_mean = fa.groupby("hour")[["pm1", "pm25"]].mean()
    
    if hourly_mean.empty:
        return None
    
    plt.figure(figsize=(10, 5))
    plt.plot(hourly_mean.index, hourly_mean["pm1"], label="PM1", marker='o')
    plt.plot(hourly_mean.index, hourly_mean["pm25"], label="PM2.5", marker='o')
    plt.xticks(range(24))
    plt.xlabel("Heure du jour")
    plt.ylabel("Concentration moyenne")
    plt.title(f"Moyenne horaire - {label}")
    plt.legend()
    plt.grid(alpha=0.3)
    fig = plt.gcf()
    fig.tight_layout()
    
    return fig




