import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

PLIK_CECH = "cechy_memow.csv"

print("Wczytywanie danych i standaryzacja (teraz z kolorami!)...")
df = pd.read_csv(PLIK_CECH)

# ZMIANA: Dodaliśmy kolumny z kolorami RGB do analizy!
cechy = df[['waga_kb', 'szerokosc', 'wysokosc', 'proporcje', 'jasnosc', 'kolor_R', 'kolor_G', 'kolor_B']]

# Standaryzacja (żeby waga w KB nie przyćmiła kolorów w skali 0-255)
scaler = StandardScaler()
cechy_ustandaryzowane = scaler.fit_transform(cechy)

print("Obliczanie WCSS (Metoda Łokcia)...")
wcss = []
max_klastrow = min(11, len(df))

for i in range(1, max_klastrow):
    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
    kmeans.fit(cechy_ustandaryzowane)
    wcss.append(kmeans.inertia_)

# Rysowanie wykresu
plt.figure(figsize=(10, 6))
plt.plot(range(1, max_klastrow), wcss, marker='o', linestyle='--', color='r') # Zmieniłem kolor linii na czerwony dla odróżnienia
plt.title('Metoda Łokcia - Wersja z Kolorami RGB')
plt.xlabel('Liczba klastrów (K)')
plt.ylabel('WCSS (Suma kwadratów błędów)')
plt.xticks(range(1, max_klastrow))
plt.grid(True)
plt.show()