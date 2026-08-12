import pandas as pd
import matplotlib.pyplot as plt


def plot_time(df):
    fa = df.copy()
    fa["time"] = pd.to_datetime(fa["time"], errors="coerce")
    fa = fa.dropna(subset=["time"]).sort_values("time")

    if fa.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 6))
    plotted = False

    if fa["pm1"].notna().any():
        ax.plot(fa["time"], fa["pm1"], label="PM1")
        plotted = True

    if fa["pm25"].notna().any():
        ax.plot(fa["time"], fa["pm25"], label="PM2.5")
        plotted = True

    if not plotted:
        return None

    ax.set_xlabel("Temps")
    ax.set_ylabel("Concentration")
    ax.set_title("Évolution de PM1 et PM2.5 dans le temps")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()

    return fig



