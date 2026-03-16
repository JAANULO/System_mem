import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# ==========================================
# TUTAJ WPISZ LICZBĘ Z TWOJEGO WYKRESU:
LICZBA_GRUP = 8
# ==========================================

PLIK_CECH = "cechy_memow.csv"

print(f"Rozpoczynam podział memów na {LICZBA_GRUP} grup...")

# 1. Wczytanie danych
df = pd.read_csv(PLIK_CECH)
cechy = df[['waga_kb', 'szerokosc', 'wysokosc', 'proporcje', 'jasnosc', 'kolor_R', 'kolor_G', 'kolor_B']]

# 2. Standaryzacja (wymagane przy K-Means!)
scaler = StandardScaler()
cechy_ustandaryzowane = scaler.fit_transform(cechy)

# 3. Uruchomienie algorytmu K-Means (Uczenie maszyny)
kmeans = KMeans(n_clusters=LICZBA_GRUP, init='k-means++', random_state=42)
kmeans.fit(cechy_ustandaryzowane)

# 4. Magia! Zapisujemy wynik do nowej kolumny w naszym pliku
df['Grupa'] = kmeans.labels_

# 5. Zapisanie gotowej bazy
df.to_csv(PLIK_CECH, index=False)

print(f"✅ Sukces! Memy zostały przydzielone do grup od 0 do {LICZBA_GRUP - 1}.")
print("Wyniki zapisano w pliku cechy_memow.csv")