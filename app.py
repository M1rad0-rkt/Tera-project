from src.visualization.PM25Temp import plot_time
from src.visualization.MoyenneHoraire import plot_hourly_average
from src.visualization.MoyenneQuo import plot_daily_hourly_mean
from src.visualization.Annuel import plot_annual_evolution
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.visualization.PM1vsPM25 import plot_hourly_pm
import os
from src.visualization.carte import plot_sensor_map, MAP_IMAGE_PATH
from src.visualization.camembert import plot_pm25_category_pie

print(MAP_IMAGE_PATH)
print(os.path.exists(MAP_IMAGE_PATH))

st.set_page_config(page_title="Analyse de la qualité de l'aire", layout="wide")

@st.cache_data
def load_data():

    df = pd.read_csv(
        "data/processed/data_clean.csv"
    )

    df["time"] = pd.to_datetime(
        df["time"],
        errors="coerce"
    )

    return df
df = load_data()

st.title("Analyse de la qualité de l'air")
st.sidebar.header("Filtres")

first_date = df["time"].dropna().dt.date.min()
last_date = df["time"].dropna().dt.date.max()

# default: no date selected at startup
use_date = st.sidebar.checkbox("Activer filtre par date", value=False, key="use_date_filter")

date = None
if use_date:
    date = st.sidebar.date_input(
        "Choisir une date",
        value=st.session_state.get("selected_date", first_date) if st.session_state.get("selected_date", None) is not None else first_date,
        min_value=first_date,
        max_value=last_date,
        key="selected_date",
    )

# If the session state has use_date_filter True, ensure date is set from session
if st.session_state.get("use_date_filter", False):
    # if no explicit date variable (checkbox just toggled), read from session
    if date is None:
        date = st.session_state.get("selected_date", first_date)

season_checkbox = st.sidebar.checkbox("Filtrer par saison", value=False, key="season_checkbox")
selected_season = None
if season_checkbox:
    selected_season = st.sidebar.selectbox(
        "Sélectionner une saison",
        ["Hiver", "Printemps", "Été", "Automne"],
        key="selected_season",
    )

st.sidebar.header("Filtre capteurs")
capteurs_disponibles = sorted(df["id_install"].astype(str).unique())
capteurs_selectionnes = st.sidebar.multiselect(
    "Sélectionner un ou plusieurs capteurs",
    options=capteurs_disponibles,
    default=capteurs_disponibles,
)

def kpi_card(title, value, icon):
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
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

col1, col2, col3 = st.columns(3)
if date is None:
    # no date filter: show global KPIs
    kpi_pm1 = f"{df['pm1'].mean():.2f} µg/m³"
    kpi_pm25 = f"{df['pm25'].mean():.2f} µg/m³"
    kpi_sensors = int(df['id_sensor'].nunique())
    sensors_list = ", ".join(sorted(df['id_sensor'].astype(str).unique())[:50])

    with col1:
        st.markdown(kpi_card("PM1 moyen (global)", kpi_pm1, "🌫️"), unsafe_allow_html=True)

    with col2:
        st.markdown(kpi_card("PM2.5 moyen (global)", kpi_pm25, "🌁"), unsafe_allow_html=True)

    with col3:
        st.markdown(kpi_card("Capteurs (global)", kpi_sensors, "📡"), unsafe_allow_html=True)

else:
    date_df = df[df["time"].dt.date == date]

    if date_df.empty:
        pm1_val = "N/A"
        pm25_val = "N/A"
        sensors_count = 0
        sensors_list = "Aucune donnée pour la date sélectionnée"
    else:
        pm1_val = f"{date_df['pm1'].mean():.2f} µg/m³"
        pm25_val = f"{date_df['pm25'].mean():.2f} µg/m³"
        sensors_count = int(date_df['id_sensor'].nunique())
        unique_sensors = sorted(date_df['id_sensor'].astype(str).unique())
        sensors_list = ", ".join(unique_sensors[:50])

    with col1:
        st.markdown(kpi_card("PM1 moyen (sélection)", pm1_val, "🌫️"), unsafe_allow_html=True)

    with col2:
        st.markdown(kpi_card("PM2.5 moyen (sélection)", pm25_val, "🌁"), unsafe_allow_html=True)

    with col3:
        st.markdown(kpi_card("Capteurs (sélection)", sensors_count, "📡"), unsafe_allow_html=True)

st.subheader("Visualisation des particules PM1 et PM2.5 dans le temps.")
col11, col12 = st.columns(2)

with col11:
    st.subheader("Évolution dans le temps.")
    st.markdown("Voir les concentrations de PM1 et PM2.5 changent au fil du temps.")
    fig1 = plot_time(df)
    if fig1 is None:
        st.warning(f"Aucune donnée trouvée.")
    else:
        st.pyplot(fig1)

with col12:
    st.subheader("Moyenne horaire.")
    st.markdown("Identification de la moyenne des pollution entre 2024 et 2026.")
    fig2 = plot_hourly_average(df)
    if fig2 is None:
        st.warning("Aucune donnée trouvée pour la moyenne horaire.")
    else:
        st.pyplot(fig2)

st.subheader("Analyse annuelle.")
st.markdown("Voir l'analyse annuelle des concentrations de PM1 et PM2.5.")

analysis_year = date.year if date is not None else first_date.year
if season_checkbox and selected_season:
    st.markdown(f"Affichage de la saison **{selected_season}** pour l'année **{analysis_year}**.")
else:
    st.markdown(f"Affichage global de l'année **{analysis_year}**.")

fig_annual = plot_annual_evolution(df, analysis_year, selected_season if season_checkbox else None)
if fig_annual is None:
    st.warning("Aucune donnée disponible pour ce filtre annuel.")
else:
    st.pyplot(fig_annual)


col21, col22 = st.columns(2)

with col21:
    st.subheader("Moyenne quotidienne.")
    st.markdown("Voir la moyenne quotidienne des concentrations de PM1 et PM2.5.")

    fig3 = plot_daily_hourly_mean(df, start_date="2024-01-01", end_date="2026-12-31")
    if fig3 is None:
        st.warning("Aucune donnée disponible pour le calcul de la moyenne quotidienne sur la période.")   
    else:
        st.pyplot(fig3)

with col22:
    st.subheader("Évolution quotidienne.")
    st.markdown("Voir les jours les plus pollués.")
    if date is None:
        st.info("Filtre date désactivé — sélectionnez une date pour voir l'évolution quotidienne.")
    else:
        fig = plot_hourly_pm(df, date)

        if fig is None:
            st.warning(f"Aucune donnée trouvée pour {date}")
        else:
            st.pyplot(fig)

st.subheader("Répartition de la qualité de l'air")
st.markdown("Voir la proportion du temps passé dans chaque catégorie de qualité de l'air.")

col_pie, _ = st.columns([1, 2])
fig_pie = plot_pm25_category_pie(
    df,
    start_date=str(date) if date is not None else None,
    end_date=str(date) if date is not None else None,
    sensors=capteurs_selectionnes if capteurs_selectionnes else None,
)

if fig_pie is None:
    st.warning("Aucune donnée disponible pour ce filtre.")
else:
    st.pyplot(fig_pie)

st.subheader("Cartes des mesures")
st.markdown("Voir où les concentrations de PM2.5 sont les plus élevées.")

fig_map = plot_sensor_map(
    df,
    start_date=str(date) if date is not None else None,
    end_date=str(date) if date is not None else None,
    sensors=capteurs_selectionnes if capteurs_selectionnes else None,
)

if fig_map is None:
    st.warning("Aucune donnée disponible pour afficher la carte avec ce filtre.")
else:
    st.pyplot(fig_map)