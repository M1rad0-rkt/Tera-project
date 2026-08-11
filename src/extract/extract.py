import pandas as pd


def extract_data(file_path):
    """
    Extrait les données depuis un fichier CSV.
    """
    return pd.read_csv(file_path, sep=",", header=1)
