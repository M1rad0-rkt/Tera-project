import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = sns.load_dataset("iris")

print(df.head())
print(df.info())

df = df.dropna()

print(df.describe())

sns.scatterplot(
    x="Axe x",
    y="Axe y",
    data=df,
    hue="species"
)

plt.title("Titre")
plt.show()

x= df.drop("species", axis=1)
y = df["species"]
