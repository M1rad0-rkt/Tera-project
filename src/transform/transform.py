import pandas as pd

def clean_columns(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

def convert_types(df):
    df["id_sensor"] = df["id_sensor"].astype(str)
    df["id_install"] = df["id_install"].astype(str)

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["pm1"] = pd.to_numeric(df["pm1"], errors="coerce")
    df["pm25"] = pd.to_numeric(df["pm25"], errors="coerce")

    return df

def handle_missing_values(df):
    df = df.dropna(
        subset=["id_sensor", "id_install", "time"]
    )

    df["pm1"] = df["pm1"].fillna(0)
    df["pm25"] = df["pm25"].fillna(0)

    return df

def remove_duplicates(df):
    return df.drop_duplicates()

def sort_data(df):
    return df.sort_values(by="time")

def validate_coordinates(df):
    df = df[
        (df["longitude"].between(-180, 180))
        & (df["latitude"].between(-90, 90))
    ]

    return df

def validate_pm_values(df):
    df = df[
        (df["pm1"] >= 0)
        & (df["pm25"] >= 0)
    ]

    return df

def create_time_features(df):
    df["date"] = df["time"].dt.date
    df["hour"] = df["time"].dt.hour
    df["day"] = df["time"].dt.day
    df["month"] = df["time"].dt.month
    df["year"] = df["time"].dt.year
    df["day_of_week"] = df["time"].dt.day_name()

    return df

def create_pollution_category(df):
    def categorize(pm25):
        if pm25 < 12:
            return "Bon"
        elif pm25 < 35.5:
            return "Modéré"
        elif pm25 < 55.5:
            return "Mauvais"
        else:
            return "Très mauvais"

    df["pm25_category"] = df["pm25"].apply(categorize)

    return df

def calculate_pm_ratio(df):
    df["pm25_pm1_ratio"] = df["pm25"] / df["pm1"].replace(0, pd.NA)

    return df

def create_season(df):
    def get_season(month):
        if month in [12, 1, 2]:
            return "Hiver"
        elif month in [3, 4, 5]:
            return "Printemps"
        elif month in [6, 7, 8]:
            return "Été"
        else:  # 9, 10, 11
            return "Automne"

    df["season"] = df["month"].apply(get_season)
    return df

def transform_data(df):

    df = df.copy()

    print("Affichage des 5 premières lignes du DataFrame : ")
    df = clean_columns(df)
    df = convert_types(df)
    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = validate_coordinates(df)
    df = validate_pm_values(df)
    df = sort_data(df)
    df = create_time_features(df)
    df = create_pollution_category(df)
    df = calculate_pm_ratio(df)
    df = create_season(df)
    print(df.head())

    return df