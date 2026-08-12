import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("data/processed/data_clean.csv")
print(df.head())


def plot_sensor_data_count(df, by="month", sensor_ids=None):
    """
    Compte le nombre de données captées par capteur (id_install),
    agrégées par 'month', 'day' ou 'year'.

    df         : DataFrame déjà filtré par la sidebar (filtered_df, daily_df, etc.)
    by         : "month", "day" ou "year"
    sensor_ids : liste optionnelle d'id_install à inclure (filtre)
    """
    fa = df.copy()
    fa["time"] = pd.to_datetime(fa["time"], errors="coerce")
    fa = fa.dropna(subset=["time"])

    if sensor_ids:
        fa = fa[fa["id_install"].astype(str).isin(sensor_ids)]

    if fa.empty:
        return None

    if by == "month":
        fa["month"] = fa["time"].dt.month
        group_col = "month"
        order = sorted(fa["month"].unique())

    elif by == "day":
        fa["day"] = fa["time"].dt.date
        group_col = "day"
        order = sorted(fa["day"].unique())

    elif by == "year":
        fa["year"] = fa["time"].dt.year
        group_col = "year"
        order = sorted(fa["year"].unique())

    else:
        raise ValueError("by doit être 'month', 'day' ou 'year'")

    counts = (
        fa.groupby(["id_install", group_col])
          .size()
          .unstack(fill_value=0)
          .reindex(columns=order, fill_value=0)
    )

    ax = counts.T.plot(kind="bar", figsize=(12, 6))
    ax.set_xlabel("Temps")
    ax.set_ylabel("Nombre de données captées")
    ax.set_title(f"Nombre de données par capteur")
    ax.legend(title="Capteur (id_install)", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.grid(alpha=0.3, axis="y")
    fig = plt.gcf()
    fig.tight_layout()

    return fig