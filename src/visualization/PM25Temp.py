import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("data/processed/data_clean.csv")
print(df.head())


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
    plt.title(f"Évolution de PM1 et PM2.5 dans le temps")
    plt.legend()
    fig1 = plt.gcf()
    fig1.autofmt_xdate()
    fig1.tight_layout()

    return fig1



