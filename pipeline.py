from src.extract.extract import extract_data
from src.transform.transform import transform_data
from src.load.load import load_data

def run_pipeline():

    # Extract
    df = extract_data(
        "data/raw/data.csv"
    )

    # Transform
    df = transform_data(df)

    # Load
    load_data(
        df,
        "data/processed/data_clean.csv"
    )

    print(df.head())
    print("✅ Pipeline ETL terminé")

run_pipeline()

