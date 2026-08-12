import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd

df = pd.read_csv("../../data/processed/data_clean.csv")

# 1. Charge l'image de fond
img = mpimg.imread('fianarantsoa.png')

# 2. Définit les bornes géographiques de l'image (coordonnées des 4 coins)
lon_min, lon_max = 47.05, 47.12
lat_min, lat_max = -21.48, -21.42

# 3. Crée la figure
fig, ax = plt.subplots(figsize=(10, 8))

# 4. Affiche l'image en fond avec 'extent' pour la caler sur les coordonnées géo
ax.imshow(img, extent=[lon_min, lon_max, lat_min, lat_max])

# 5. Tes données lat/lon en scatter, par-dessus

latitude_mean = (
    df.groupby(df["id_install"])["latitude"]
    .mean()
    .sort_index()
)
longitude_mean = (
    df.groupby(df["id_install"])["longitude"]
    .mean()
    .sort_index()
)

 # ex: indice de pollution
df = pd.DataFrame({
    'latitude': latitude_mean,
    'longitude': longitude_mean
})

sc = ax.scatter(df['longitude'], df['latitude'], 
                 s=150, c='red', edgecolors='black', zorder=5)

# Ajoute les identifiants de chaque station
for id_install, row in df.iterrows():
    ax.annotate(id_install, (row['longitude'], row['latitude']), 
                textcoords="offset points", xytext=(5, 5), 
                fontsize=8, fontweight='bold')

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Installations - Fianarantsoa")
ax.set_aspect('equal')

plt.show()