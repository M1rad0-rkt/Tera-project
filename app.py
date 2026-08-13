from src.visualization.PM25Temp import plot_time
from src.visualization.MoyenneHoraire import plot_hourly_average
from src.visualization.MoyenneQuo import plot_daily_hourly_mean
from src.visualization.Annuel import plot_annual_evolution
from src.visualization.capteur import plot_sensor_data_count
import streamlit as st
import pandas as pd
import calendar
from src.visualization.PM1vsPM25 import plot_hourly_mean, plot_hourly_pm
from src.visualization.carte import plot_sensor_map
from src.visualization.camembert import plot_pm25_category_bar
from src.visualization.Category import plot_pm25_category_trends
import os
from src.visualization.carte import plot_sensor_map, MAP_IMAGE_PATH

AVATAR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asset", "Avtar.png")

st.set_page_config(page_title="Analyse de la qualité de l'aire", layout="wide")

if os.path.exists(AVATAR_PATH):
    st.sidebar.image(AVATAR_PATH, width=150)

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/data_clean.csv")
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    return df


df = load_data()

st.title("Analyse de la qualité de l'air")
st.sidebar.header("Filtres")

first_date = df["time"].dropna().dt.date.min()
last_date = df["time"].dropna().dt.date.max()
available_years = sorted(df["time"].dropna().dt.year.unique().astype(int))

use_date = st.sidebar.checkbox("Activer filtre par date", value=False, key="use_date_filter")
selected_period = "Global"
selected_year = available_years[-1] if available_years else first_date.year
selected_month = None
selected_season = None
selected_filter_type = None
date = None
filtered_df = df.copy()
season_checkbox = False

if use_date:
    selected_filter_type = st.sidebar.selectbox(
        "Sélectionner le niveau de date",
        ["Jour", "Mois", "Année"],
        key="date_filter_type",
    )

    if selected_filter_type == "Jour":
        date = st.sidebar.date_input(
            "Choisir une date",
            value=st.session_state.get("selected_date", first_date) if st.session_state.get("selected_date", None) is not None else first_date,
            min_value=first_date,
            max_value=last_date,
            key="selected_date",
        )
        selected_year = date.year
        selected_month = date.month
        filtered_df = df[df["time"].dt.date == date]
        selected_period = date.strftime("%Y-%m-%d")

    elif selected_filter_type == "Mois":
        months = list(calendar.month_name)[1:]
        session_month = st.session_state.get("selected_month", pd.Timestamp.now().month)
        if isinstance(session_month, str):
            if session_month.isdigit():
                session_month = int(session_month)
            elif session_month in months:
                session_month = months.index(session_month) + 1
            else:
                try:
                    session_month = int(session_month)
                except ValueError:
                    session_month = pd.Timestamp.now().month
        default_month_index = session_month - 1
        default_month_index = min(max(default_month_index, 0), len(months) - 1)
        selected_month = st.sidebar.selectbox(
            "Sélectionner un mois",
            months,
            index=default_month_index,
            key="selected_month",
        )
        session_year = st.session_state.get("selected_year", selected_year)
        if isinstance(session_year, str) and session_year.isdigit():
            session_year = int(session_year)
        selected_year = st.sidebar.selectbox(
            "Sélectionner une année",
            available_years,
            index=max(0, available_years.index(session_year)) if session_year in available_years else len(available_years) - 1,
            key="selected_year",
        )
        month_number = months.index(selected_month) + 1
        selected_season = (
            "Hiver" if month_number in [12, 1, 2]
            else "Printemps" if month_number in [3, 4, 5]
            else "Été" if month_number in [6, 7, 8]
            else "Automne"
        )
#        st.sidebar.subheader(f"**Saison automatique :** {selected_season}")
        filtered_df = df[(df["time"].dt.month == month_number) & (df["time"].dt.year == selected_year)]
        selected_period = f"{selected_month} {selected_year}"

    else:
        selected_year = st.sidebar.selectbox(
            "Sélectionner une année",
            available_years,
            index=max(0, available_years.index(st.session_state.get("selected_year", selected_year))) if selected_year in available_years else len(available_years) - 1,
            key="selected_year",
        )
        filtered_df = df[df["time"].dt.year == selected_year]
        selected_period = str(selected_year)

    if selected_filter_type != "Mois":
        season_checkbox = st.sidebar.checkbox("Filtrer par saison", value=False, key="season_checkbox")
        if season_checkbox:
            selected_season = st.sidebar.selectbox(
                "Sélectionner une saison",
                ["Hiver", "Printemps", "Été", "Automne"],
                key="selected_season",
            )

if selected_filter_type == "Année":
    main_df = filtered_df
else:
    main_df = df

if selected_filter_type == "Mois":
    daily_df = filtered_df
    start_daily = f"{selected_year}-{month_number:02}-01"
    end_daily = f"{selected_year}-{month_number:02}-{calendar.monthrange(selected_year, month_number)[1]}"
elif selected_filter_type == "Année":
    daily_df = filtered_df
    start_daily = f"{selected_year}-01-01"
    end_daily = f"{selected_year}-12-31"
elif selected_filter_type == "Jour" and date is not None:
    day_month = date.month
    day_year = date.year
    daily_df = df[(df["time"].dt.year == day_year) & (df["time"].dt.month == day_month)]
    start_daily = f"{day_year}-{day_month:02}-01"
    end_daily = f"{day_year}-{day_month:02}-{calendar.monthrange(day_year, day_month)[1]}"
else:
    daily_df = df
    start_daily = "2024-01-01"
    end_daily = "2026-12-31"

capteurs_disponibles = sorted(df["id_install"].astype(str).unique())
capteurs_checkbox = st.sidebar.checkbox("Filtrer par capteurs", value=False, key="capteurs_checkbox")
selected_capteurs = None
if capteurs_checkbox:
    capteurs_selectionnes = st.sidebar.multiselect(
        "Sélectionner un ou plusieurs capteurs",
        options=capteurs_disponibles,
        default=capteurs_disponibles,
    )
else:
    capteurs_selectionnes = None

# Filtre par catégorie PM
# pm_category_checkbox = st.sidebar.checkbox("Filtrer par catégorie PM2.5", value=False, key="pm_category_checkbox")
# selected_pm_category = "Toutes"
# if pm_category_checkbox:
#     pm_categories = ["Toutes", "Bon", "Modéré", "Mauvais", "Très mauvais"]
#     selected_pm_category = st.sidebar.selectbox(
#         "Sélectionner une catégorie PM2.5", pm_categories, index=0, key="pm_category"
#     )


def air_quality_category(pm25_value):
    if pd.isna(pm25_value):
        return "Aucune donnée", "#f3f4f6"
    if pm25_value <= 12:
        return "Bon", "#d1fae5"
    if pm25_value <= 35.4:
        return "Modéré", "#fef3c7"
    if pm25_value <= 55.4:
        return "Mauvais", "#fed7aa"
    return "Très mauvais", "#fecaca"


def kpi_card(title, value, icon="", bg_color="#ffffff"):
    icon_html = f" {icon}" if icon else ""
    return f"""
    <div class="kpi-card" style="background: {bg_color};">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}{icon_html}</div>
    </div>
    """

st.markdown("""
<style>

.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    text-align: center;
    margin-bottom: 15px;
}

.kpi-icon {
    font-size: 50px;
}

.kpi-title {
    color: #6b7280;
    font-size: 14px;
    margin-top: 5px;
}

.kpi-value {
    color: #111827;
    font-size: 26px;
    font-weight: bold;
    margin-top: 8px;
}

</style>
""", unsafe_allow_html=True)


global_pm1 = df["pm1"].mean()
global_pm25 = df["pm25"].mean()
global_pm1_label = f"{global_pm1:.2f} µg/m³" if pd.notna(global_pm1) else "N/A"
global_pm25_label = f"{global_pm25:.2f} µg/m³" if pd.notna(global_pm25) else "N/A"
global_sensors = int(df["id_sensor"].nunique())
filtered_sensors = int(filtered_df["id_sensor"].nunique())
quality_label, quality_bg = air_quality_category(global_pm25)

def kpi_trend_style(value, global_value):
    if pd.isna(value) or pd.isna(global_value):
        return "#ffffff", ""
    if value < global_value:
        return "#fdb7b7ff", "▼"
    if value > global_value:
        return "#93ff99ff", "▲"
    return "#fefeff", ""

col1, col2, col3, col4 = st.columns(4)
if not use_date:
    with col1:
        st.markdown(kpi_card("PM1 moyen (global)", global_pm1_label), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("PM2.5 moyen (global)", global_pm25_label), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Qualité de l'air (global)", quality_label, bg_color=quality_bg), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("Capteurs (global)", global_sensors), unsafe_allow_html=True)
else:
    if filtered_df.empty:
        pm1_val = "N/A"
        pm25_val = "N/A"
        quality_label, quality_bg = "Aucune donnée", "#f3f4f6"
        pm1_bg, pm1_icon = "#ffffff", ""
        pm25_bg, pm25_icon = "#ffffff", ""
    else:
        pm1_mean = filtered_df['pm1'].mean()
        pm25_mean = filtered_df['pm25'].mean()
        pm1_val = f"{pm1_mean:.2f} µg/m³" if pd.notna(pm1_mean) else "N/A"
        pm25_val = f"{pm25_mean:.2f} µg/m³" if pd.notna(pm25_mean) else "N/A"
        pm1_bg, pm1_icon = kpi_trend_style(pm1_mean, global_pm1)
        pm25_bg, pm25_icon = kpi_trend_style(pm25_mean, global_pm25)
        quality_label, quality_bg = air_quality_category(pm25_mean)
    with col1:
        st.markdown(kpi_card("PM1 moyen (sélection)", pm1_val, pm1_icon, bg_color=pm1_bg), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("PM2.5 moyen (sélection)", pm25_val, pm25_icon, bg_color=pm25_bg), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Qualité de l'air (sélection)", quality_label, bg_color=quality_bg), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("Capteurs (sélection)", filtered_sensors), unsafe_allow_html=True)
st.title("Visualisation des particules PM1 et PM2.5 dans le temps.")
col11, col12 = st.columns(2)

with col11:
    st.title("Évolution dans le temps.")
    st.subheader("Concentrations de PM1 et PM2.5 changent au fil du temps.")
    fig1 = plot_time(main_df)
    if fig1 is None:
        st.warning("Aucune donnée trouvée.")
    else:
        st.pyplot(fig1)

with col12:
    st.title("Moyenne horaire.")
    st.subheader("Identification de la moyenne des pollution entre 2024 et 2026.")
    fig2 = plot_hourly_average(main_df)
    if fig2 is None:
        st.warning("Aucune donnée trouvée pour la moyenne horaire.")
    else:
        st.pyplot(fig2)

st.title("Analyse annuelle.")
st.subheader("Voir l'analyse annuelle des concentrations de PM1 et PM2.5.")

analysis_year = selected_year if use_date else first_date.year
if selected_season:
    st.subheader(f"Affichage de la saison **{selected_season}** pour l'année **{analysis_year}**.")
else:
    st.subheader(f"Affichage global de l'année **{analysis_year}**.")

fig_annual = plot_annual_evolution(filtered_df, analysis_year, selected_season if selected_season else None)
if fig_annual is None:
    st.warning("Aucune donnée disponible pour ce filtre annuel.")
else:
    st.pyplot(fig_annual)

col21, col22 = st.columns(2)

with col21:
    st.title("Moyenne quotidienne.")
    st.subheader("Voir la moyenne quotidienne des concentrations de PM1 et PM2.5.")
    fig3 = plot_daily_hourly_mean(daily_df, start_date=start_daily, end_date=end_daily)
    if fig3 is None:
        st.warning("Aucune donnée disponible pour le calcul de la moyenne quotidienne sur la période.")
    else:
        st.pyplot(fig3)

with col22:
    st.title("Évolution quotidienne.")
    st.subheader("Voir les jours les plus pollués.")
    if selected_filter_type != "Jour" or date is None:
        st.info("Filtre de type Jour nécessaire — sélectionnez un jour pour voir l'évolution quotidienne.")
    else:
        fig = plot_hourly_pm(filtered_df, date)
        if fig is None:
            st.warning(f"Aucune donnée trouvée pour {date}")
        else:
            st.pyplot(fig)

col30, col31 = st.columns(2)

with col30:
    kwargs_date = {}
    if selected_filter_type == "Jour" and date is not None:
        kwargs_date = {"start_date": str(date), "end_date": str(date)}
    kwargs_sensors = {"sensors": capteurs_selectionnes if capteurs_selectionnes else None}
    kwargs_season = {"season": selected_season if selected_season else None}

    st.title("Répartition de la qualité de l'air")
    st.subheader("Voir la proportion du temps passé dans chaque catégorie de qualité de l'air.")
    fig_bar = plot_pm25_category_bar(filtered_df, **kwargs_date, **kwargs_sensors, **kwargs_season)
    if fig_bar is None:
        st.warning("Aucune donnée disponible pour la répartition de la qualité de l'air.")
    else:
        st.pyplot(fig_bar)

with col31:
    # --- Carte des capteurs ---
    st.title("Cartes des mesures")
    st.subheader("Voir où les concentrations de PM2.5 sont les plus élevées.")

    fig_map = plot_sensor_map(df, **kwargs_date, **kwargs_sensors, **kwargs_season)
    if fig_map is None:
        st.warning("Aucune donnée disponible pour ce filtre.")
    else:
        st.pyplot(fig_map)




col_left, col_right = st.columns(2)

with col_left:
    st.title("Tendances par catégorie")
    st.subheader("Proportions de chaque catégorie dans le temps.")
    # selected_category_filter = None if selected_pm_category == "Toutes" else selected_pm_category
    fig_trends = plot_pm25_category_trends(df, start_date=start_daily, end_date=end_daily,
                                          sensors=capteurs_selectionnes if capteurs_selectionnes else None,
                                          season=selected_season if selected_season else None)
                                        #   category=selected_category_filter
    if fig_trends is None:
        st.warning("Aucune donnée pour les tendances par catégorie.")
    else:
        st.pyplot(fig_trends)

with col_right:
    st.title("Analyse des capteurs de pollution")
    st.subheader("Nombre de données captées par capteur")

    filter_to_agg = {
        "Jour": "day",
        "Mois": "month",
        "Année": "year",
    }
    count_by = filter_to_agg.get(selected_filter_type, "month")

    fig_count = plot_sensor_data_count(
        df,
        by=count_by,
        sensor_ids=capteurs_selectionnes,
    )

    if fig_count is not None:
        st.pyplot(fig_count)
    else:
        st.warning("Aucune donnée pour ces filtres.")
    


st.subheader("Extremes par capteur (PM2.5)")
    # Utiliser filtered_df ou daily_df selon le contexte souhaité
src_df = filtered_df.copy() if not filtered_df.empty else df.copy()
src_df = src_df.dropna(subset=['time', 'pm25'])
if src_df.empty:
    st.info("Aucune donnée disponible pour ce filtre.")
else:
    src_df['date_only'] = src_df['time'].dt.date
    rows = []
    for sensor, g in src_df.groupby('id_install'):
        if g['pm25'].notna().any():
            g_sorted = g.sort_values('pm25')
            best = g_sorted.iloc[0]
            worst = g_sorted.iloc[-1]
            rows.append({
                'CAPTEUR': sensor,
                'MEILLEUR JOUR': best['date_only'],
                'PM2.5 MEILLEUR': round(best['pm25'], 2),
                'PIRE JOUR': worst['date_only'],
                'PM2.5 PIRE': round(worst['pm25'], 2)
            })
    summary = pd.DataFrame(rows)
    if summary.empty:
        st.info("Pas de valeurs PM2.5 disponibles pour ces capteurs.")
    else:
            # Trier par pire valeur décroissante pour mettre en évidence les capteurs les plus problématiques
        st.dataframe(summary.sort_values('PM2.5 PIRE', ascending=False).reset_index(drop=True))








