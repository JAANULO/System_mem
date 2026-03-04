import os
import sys
import pandas as pd
import numpy as np
from PIL import Image

# ==========================================
# KONFIGURACJA
# ==========================================
FOLDER_ZRODLOWY = "memy"
PLIK_CECH = "cechy_memow.csv"
WYNIK_MOZAIKI = "mozaika_gradient_pro.jpg"

SIATKA_X = 100
SIATKA_Y = 60
ROZMIAR_KAFELKA = 40
MOC_KARY = 8000


# ==========================================

# --- INŻYNIERSKI PASEK POSTĘPU ---
def pasek_postepu(aktualny, total, prefiks=''):
    procent = 100 * (aktualny / float(total))
    zapelnienie = int(40 * aktualny // total)  # Długość paska to 40 znaków
    pasek = '█' * zapelnienie + '-' * (40 - zapelnienie)
    # \r nadpisuje obecną linijkę w konsoli!
    sys.stdout.write(f'\r{prefiks} |{pasek}| {procent:.1f}% ')
    sys.stdout.flush()
    if aktualny == total:
        print()  # Przejdź do nowej linii po zakończeniu


def generuj_gradient():
    print("--- ROZPOCZYNAMY TWORZENIE ZAAWANSOWANEGO GRADIENTU ---")

    if not os.path.exists(PLIK_CECH):
        print(f"BŁĄD: Brak bazy {PLIK_CECH}!")
        return

    df = pd.read_csv(PLIK_CECH)
    baza_rgb = df[['kolor_R', 'kolor_G', 'kolor_B']].values.astype('float32')
    nazwy_plikow = df['nazwa_pliku'].values

    licznik_uzyc = {nazwa: 0 for nazwa in nazwy_plikow}
    total_operacji = SIATKA_X * SIATKA_Y

    # 1. FAZA MATEMATYCZNA
    print("🎨 Generowanie mocnej palety barw...")
    pixele_celu = np.zeros((SIATKA_Y, SIATKA_X, 3), dtype='float32')

    kolor_LG = np.array([255, 0, 50])
    kolor_PG = np.array([0, 100, 255])
    kolor_LD = np.array([255, 200, 0])
    kolor_PD = np.array([0, 255, 150])

    for y in range(SIATKA_Y):
        for x in range(SIATKA_X):
            waga_x = x / (SIATKA_X - 1)
            waga_y = y / (SIATKA_Y - 1)
            gora = kolor_LG * (1 - waga_x) + kolor_PG * waga_x
            dol = kolor_LD * (1 - waga_x) + kolor_PD * waga_x
            pixele_celu[y, x] = gora * (1 - waga_y) + dol * waga_y

    # 2. DOBIERANIE ZDJĘĆ Z PASEKIEM POSTĘPU
    print("🧠 Dobieranie zdjęć (System Anty-Klonowania):")
    mapa_kafelkow = np.empty((SIATKA_Y, SIATKA_X), dtype=object)
    obecna_operacja = 0

    for y in range(SIATKA_Y):
        for x in range(SIATKA_X):
            target_rgb = pixele_celu[y, x]
            odleglosci_baza = np.sum((baza_rgb - target_rgb) ** 2, axis=1)

            kary = np.array([licznik_uzyc[nazwa] * MOC_KARY for nazwa in nazwy_plikow])
            odleglosci_z_kara = odleglosci_baza + kary

            najlepszy_indeks = np.argmin(odleglosci_z_kara)
            zwyciezca = nazwy_plikow[najlepszy_indeks]

            mapa_kafelkow[y, x] = zwyciezca
            licznik_uzyc[zwyciezca] += 1

            # Aktualizacja paska postępu
            obecna_operacja += 1
            if obecna_operacja % 50 == 0 or obecna_operacja == total_operacji:
                pasek_postepu(obecna_operacja, total_operacji, "Faza 1/2")

    # 3. SKŁADANIE OBRAZU Z PASEKIEM POSTĘPU
    print("🖼️ Sklejanie fizycznej mozaiki na płótnie:")
    szerokosc_koncowa = SIATKA_X * ROZMIAR_KAFELKA
    wysokosc_koncowa = SIATKA_Y * ROZMIAR_KAFELKA
    plotno = Image.new('RGB', (szerokosc_koncowa, wysokosc_koncowa))
    obecna_operacja = 0

    for y in range(SIATKA_Y):
        for x in range(SIATKA_X):
            plik_kafelka = mapa_kafelkow[y, x]
            sciezka_zrodlowa = os.path.join(FOLDER_ZRODLOWY, plik_kafelka)
            try:
                img = Image.open(sciezka_zrodlowa).convert('RGB')
                img = img.resize((ROZMIAR_KAFELKA, ROZMIAR_KAFELKA))
                plotno.paste(img, (x * ROZMIAR_KAFELKA, y * ROZMIAR_KAFELKA))
            except Exception:
                pass

            # Aktualizacja paska postępu
            obecna_operacja += 1
            if obecna_operacja % 50 == 0 or obecna_operacja == total_operacji:
                pasek_postepu(obecna_operacja, total_operacji, "Faza 2/2")

    plotno.save(WYNIK_MOZAIKI)

    # --- NOWA FUNKCJA: STATYSTYKA UNIKALNYCH ZDJĘĆ ---
    unikalne_uzyte = sum(1 for ilosc in licznik_uzyc.values() if ilosc > 0)
    calkowita_liczba = len(nazwy_plikow)
    procent_uzycia = (unikalne_uzyte / calkowita_liczba) * 100

    print(f"\n📊 Użyte obrazy {unikalne_uzyte}/{calkowita_liczba}  {procent_uzycia:.0f}%")
    print(f"\n✅ GOTOWE! Pomyślnie zapisano plik: {WYNIK_MOZAIKI}")


if __name__ == "__main__":
    generuj_gradient()