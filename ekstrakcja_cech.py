import os
import sys
import pandas as pd
from PIL import Image, ImageStat
from colorthief import ColorThief

# Konfiguracja
FOLDER_MEMOW = "memy"
PLIK_CECH = "cechy_memow.csv"

def pasek_postepu(aktualny, total, prefiks='Skanowanie'):
    if total == 0: return
    procent = 100 * (aktualny / float(total))
    zapelnienie = int(40 * aktualny // total)
    pasek = '█' * zapelnienie + '-' * (40 - zapelnienie)
    sys.stdout.write(f'\r{prefiks} |{pasek}| {aktualny}/{total} ({procent:.1f}%) ')
    sys.stdout.flush()
    if aktualny == total: print()

print("Rozpoczynam aktualizację bazy memów...")

# 1. Pobranie listy plików z folderu
pliki_w_folderze = set([p for p in os.listdir(FOLDER_MEMOW) if p.lower().endswith(('.jpg', '.jpeg', '.png'))])

# 2. Wczytanie starych danych z bazy (jeśli istnieje)
stare_dane = []
pliki_w_bazie = set()

if os.path.exists(PLIK_CECH):
    try:
        df_stare = pd.read_csv(PLIK_CECH)
        # Zostawiamy w bazie TYLKO te pliki, które nadal istnieją w folderze (usuwamy skasowane memy z pamięci)
        df_stare = df_stare[df_stare['nazwa_pliku'].isin(pliki_w_folderze)]
        pliki_w_bazie = set(df_stare['nazwa_pliku'].tolist())
        stare_dane = df_stare.to_dict('records')
    except Exception:
        pass

# 3. Wyodrębnienie tylko NOWYCH plików do przeskanowania
nowe_pliki = list(pliki_w_folderze - pliki_w_bazie)
liczba_nowych = len(nowe_pliki)

if liczba_nowych == 0:
    print("Brak nowych plików do ekstrakcji. Aktualizacja wpisów o usuniętych memach...")
    pd.DataFrame(stare_dane).to_csv(PLIK_CECH, index=False)
    print("✅ Gotowe! Baza zaktualizowana.")
    sys.exit(0)

print(f"Znaleziono {liczba_nowych} nowych plików do analizy.")
nowe_dane = []
bledy = 0

# 4. Skanowanie TYLKO nowych plików
for i, plik in enumerate(nowe_pliki, 1):
    sciezka = os.path.join(FOLDER_MEMOW, plik)

    try:
        waga_kb = os.path.getsize(sciezka) / 1024.0
        with Image.open(sciezka) as img:
            szerokosc = img.width
            wysokosc = img.height
            proporcje = szerokosc / wysokosc if wysokosc > 0 else 0
            img_szary = img.convert('L')
            jasnosc = ImageStat.Stat(img_szary).mean[0]

        r, g, b = 128, 128, 128
        try:
            color_thief = ColorThief(sciezka)
            dominujacy_kolor = color_thief.get_color(quality=1)
            if isinstance(dominujacy_kolor, tuple) and len(dominujacy_kolor) >= 3:
                r, g, b = dominujacy_kolor[0], dominujacy_kolor[1], dominujacy_kolor[2]
        except Exception:
            pass

        nowe_dane.append({
            "nazwa_pliku": plik, "waga_kb": round(waga_kb, 2), "szerokosc": szerokosc,
            "wysokosc": wysokosc, "proporcje": round(proporcje, 2), "jasnosc": round(jasnosc, 2),
            "kolor_R": r, "kolor_G": g, "kolor_B": b
        })

    except Exception as e:
        bledy += 1
        nowe_dane.append({
            "nazwa_pliku": plik, "waga_kb": 0, "szerokosc": 0, "wysokosc": 0,
            "proporcje": 0, "jasnosc": 0, "kolor_R": 0, "kolor_G": 0, "kolor_B": 0
        })

    pasek_postepu(i, liczba_nowych, prefiks='Analiza nowości')

# 5. Połączenie starych wyników z nowymi i zapisanie całości
wszystkie_dane = stare_dane + nowe_dane
df_wynik = pd.DataFrame(wszystkie_dane)
df_wynik.to_csv(PLIK_CECH, index=False)

print(f"✅ Gotowe! W bazie znajduje się teraz {len(wszystkie_dane)} wpisów.")