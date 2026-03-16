import os
import pandas as pd
import numpy as np
from PIL import Image

# ==========================================
# KONFIGURACJA
# ==========================================
PLIK_DOCELOWY = "cel.jpg"
FOLDER_ZRODLOWY = "memy"
PLIK_CECH = "cechy_memow.csv"
WYNIK_MOZAIKI = "mozaika_wynik.jpg"

# Ustalamy tylko ile kafelków chcemy mieć na SZEROKOŚĆ.
# Wysokość program policzy sam z proporcji obrazka!
SIATKA_X = 80
ROZMIAR_KAFELKA = 40


# ==========================================

def generuj():
    print("--- ROZPOCZYNAMY INTELIGENTNE TWORZENIE MOZAIKI ---")

    # 1. Wczytanie bazy danych
    if not os.path.exists(PLIK_CECH):
        print(f"BŁĄD: Brak pliku {PLIK_CECH}! Uruchom najpierw ekstrakcję cech.")
        return

    print("Wczytuję dane o kolorach z bazy...")
    df = pd.read_csv(PLIK_CECH)

    # Zamiana na czystą matematykę dla wydajności
    baza_rgb = df[['kolor_R', 'kolor_G', 'kolor_B']].values.astype('float32')
    nazwy_plikow = df['nazwa_pliku'].values

    # 2. Przygotowanie obrazu docelowego i wyliczenie proporcji
    if not os.path.exists(PLIK_DOCELOWY):
        print(f"BŁĄD: Brak pliku {PLIK_DOCELOWY}!")
        return

    cel_img = Image.open(PLIK_DOCELOWY).convert('RGB')
    szer_oryginalna, wys_oryginalna = cel_img.size
    print(f"Oryginalny wymiar zdjęcia: {szer_oryginalna}x{wys_oryginalna} pikseli")

    # --- MATEMATYKA PROPORCJI ---
    proporcja = wys_oryginalna / szer_oryginalna
    SIATKA_Y = int(SIATKA_X * proporcja)
    print(f"Wyliczona siatka kafelków: {SIATKA_X} na szerokość i {SIATKA_Y} na wysokość")

    # Zmniejszamy obraz docelowy do naszej wyliczonej siatki
    cel_maly = cel_img.resize((SIATKA_X, SIATKA_Y), Image.Resampling.LANCZOS)
    pixele_celu = np.array(cel_maly).astype('float32')

    # 3. Faza Matematyczna - Dobieranie kafelków
    print("Szukam najlepszych dopasowań kolorystycznych...")
    mapa_kafelkow = np.empty((SIATKA_Y, SIATKA_X), dtype=object)

    for y in range(SIATKA_Y):
        for x in range(SIATKA_X):
            target_rgb = pixele_celu[y, x]
            odleglosci = np.sum((baza_rgb - target_rgb) ** 2, axis=1)
            najlepszy_indeks = np.argmin(odleglosci)
            mapa_kafelkow[y, x] = nazwy_plikow[najlepszy_indeks]

    # 4. Faza Składania - Klejenie obrazu
    print("Rozpoczynam sklejanie mozaiki (to chwilę potrwa)...")
    szerokosc_koncowa = SIATKA_X * ROZMIAR_KAFELKA
    wysokosc_koncowa = SIATKA_Y * ROZMIAR_KAFELKA

    print(f"Spodziewany rozmiar końcowy pliku: {szerokosc_koncowa}x{wysokosc_koncowa} pikseli")
    plotno = Image.new('RGB', (szerokosc_koncowa, wysokosc_koncowa))

    licznik = 0
    total_kafelkow = SIATKA_X * SIATKA_Y

    for y in range(SIATKA_Y):
        for x in range(SIATKA_X):
            plik_kafelka = mapa_kafelkow[y, x]
            sciezka_zrodlowa = os.path.join(FOLDER_ZRODLOWY, plik_kafelka)

            try:
                img = Image.open(sciezka_zrodlowa).convert('RGB')
                # Upewniamy się, że każdy kafelek ma pożądany rozmiar
                img = img.resize((ROZMIAR_KAFELKA, ROZMIAR_KAFELKA))

                pos_x = x * ROZMIAR_KAFELKA
                pos_y = y * ROZMIAR_KAFELKA

                plotno.paste(img, (pos_x, pos_y))

            except Exception as e:
                print(f"Błąd przy kafelku {plik_kafelka}: {e}")

            licznik += 1
            # Zmniejszyłem częstotliwość logowania, żeby nie zaśmiecać konsoli
            if licznik % 500 == 0 or licznik == total_kafelkow:
                print(f"Wklejono: {licznik} / {total_kafelkow} kafelków...")

    # 5. Zapisanie wyniku
    print(f"Zapisuję wynik do {WYNIK_MOZAIKI}...")
    plotno.save(WYNIK_MOZAIKI)
    print("✅ GOTOWE! Proporcje zostały zachowane!")


if __name__ == "__main__":
    generuj()