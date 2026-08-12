import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.visualization.camembert import COULEURS_CATEGORIE

sns.set_theme(style="whitegrid")

SEASONS_MAP = {
    1: "Hiver", 2: "Hiver",
    3: "Printemps", 4: "Printemps", 5: "Printemps",
    6: "Été", 7: "Été", 8: "Été",
    9: "Automne", 10: "Automne", 11: "Automne", 12: "Hiver",
}


def _filtrer(df, start_date=None, end_date=None, sensors=None, season=None, category=None):
    fa = df.copy()
    fa['time'] = pd.to_datetime(fa['time'], errors='coerce')
    fa = fa.dropna(subset=['time'])

    if start_date:
        fa = fa[fa['time'] >= pd.to_datetime(start_date)]
    if end_date:
        fa = fa[fa['time'] <= pd.to_datetime(end_date)]

    if season:
        fa = fa[fa['time'].dt.month.map(SEASONS_MAP) == season]

    if sensors:
        fa = fa[fa['id_install'].isin(sensors)]

    if category:
        fa = fa[fa['pm25_category'] == category]

    return fa


def plot_pm25_category_trends(df, start_date=None, end_date=None, sensors=None, season=None, category=None, freq='M'):
    """Return a stacked-area plot of monthly category proportions for PM2.5.

    Parameters
    ----------
    df : DataFrame with columns ['time','pm25_category','id_install',...]
    start_date, end_date : optional date strings
    sensors : optional list of id_install
    season : optional season name to filter
    category : optional single category to filter before aggregating (None = all)
    freq : frequency for resampling ('M' monthly by default)
    """
    fa = _filtrer(df, start_date, end_date, sensors, season, category)
    if fa.empty:
        return None

    # Ensure category column exists
    if 'pm25_category' not in fa.columns:
        # try to derive category from pm25 numeric if present
        if 'pm25' in fa.columns:
            def _cat(v):
                if pd.isna(v):
                    return 'Aucune donnée'
                if v <= 12:
                    return 'Bon'
                if v <= 35.4:
                    return 'Modéré'
                if v <= 55.4:
                    return 'Mauvais'
                return 'Très mauvais'
            fa['pm25_category'] = fa['pm25'].apply(_cat)
        else:
            return None

    # Group by period and category
    fa['period'] = fa['time'].dt.to_period(freq).dt.to_timestamp()
    grp = fa.groupby(['period', 'pm25_category']).size().reset_index(name='count')

    total = grp.groupby('period')['count'].sum().reset_index(name='total')
    merged = grp.merge(total, on='period')
    merged['pct'] = merged['count'] / merged['total'] * 100

    pivot = merged.pivot(index='period', columns='pm25_category', values='pct').fillna(0)
    pivot = pivot.sort_index()

    # Plot stacked area using same colors as the camembert
    couleurs = [COULEURS_CATEGORIE.get(cat, "#95a5a6") for cat in pivot.columns]
    fig, ax = plt.subplots(figsize=(10, 5))
    pivot.plot.area(ax=ax, color=couleurs)
    ax.set_ylabel('Proportion (%)')
    ax.set_xlabel('Période')
    ax.set_title('Répartition mensuelle des catégories PM2.5')
    ax.legend(title='Catégorie')
    fig.tight_layout()
    return fig
