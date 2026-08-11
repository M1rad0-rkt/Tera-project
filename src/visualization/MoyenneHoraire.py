import pandas as pd
import matplotlib.pyplot as plt

#===============================================================
#ANALYSE DE L EVOLUTION PAR SAISON
#===============================================================
 
def plot_time(df):
    fa = df.copy()
    fa["time"] = pd.to_datetime(fa["time"], errors="coerce")

    if fa.empty:
        return None

    plt.figure(figsize=(12, 6))
    plt.plot(fa["time"], fa["pm1"], label="PM1")
    plt.plot(fa["time"], fa["pm25"], label="PM2.5")
    plt.xlabel("Temps")
    plt.ylabel("Concentration")
    plt.title("Moyenne de l'évolution de PM1 et PM2.5 dans le temps")
    plt.legend()
    fig1 = plt.gcf()
    fig1.autofmt_xdate()
    fig1.tight_layout()

    return fig1


def plot_hourly_average(df, start_date="2024-01-01", end_date="2026-12-31"):
    fa = df.copy()
    fa["time"] = pd.to_datetime(fa["time"], errors="coerce")
    fa = fa.dropna(subset=["time"])

    if start_date:
        fa = fa[fa["time"] >= pd.to_datetime(start_date)]
    if end_date:
        fa = fa[fa["time"] <= pd.to_datetime(end_date)]

    if fa.empty:
        return None

    hourly = (
        fa.set_index("time")[['pm1', 'pm25']]
          .resample("1h")
          .mean()
          .reset_index()
    )

    plt.figure(figsize=(12, 6))
    plt.plot(hourly["time"], hourly["pm1"], label="PM1 (moyenne horaire)")
    plt.plot(hourly["time"], hourly["pm25"], label="PM2.5 (moyenne horaire)")
    plt.xlabel("Temps")
    plt.ylabel("Concentration moyenne")
    plt.title(f"Moyenne horaire de PM1 et PM2.5 ({start_date} - {end_date})")
    plt.legend()
    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.tight_layout()

    return fig



