import os
import sys
import pandas as pd
from ultralytics import YOLO
import warnings

# Wyłączenie zbędnych ostrzeżeń
warnings.filterwarnings("ignore")

FOLDER_MEMOW = "memy"
PLIK_OBIEKTOW = "obiekty_memow.csv"


def pasek_postepu(aktualny, total, prefiks='Detekcja AI'):
    if total == 0: return
    procent = 100 * (aktualny / float(total))
    zapelnienie = int(40 * aktualny // total)
    pasek = '█' * zapelnienie + '-' * (40 - zapelnienie)
    sys.stdout.write(f'\r{prefiks} |{pasek}| {aktualny}/{total} ({procent:.1f}%) ')
    sys.stdout.flush()
    if aktualny == total: print()


print("Rozpoczynam weryfikację bazy obiektów AI...")

# 1. Sprawdzanie plików w folderze
pliki_w_folderze = set([p for p in os.listdir(FOLDER_MEMOW) if p.lower().endswith(('.jpg', '.jpeg', '.png'))])

# 2. Wczytanie starych wyników (jeśli istnieją) i usunięcie wpisów o skasowanych plikach
stare_dane = pd.DataFrame()
pliki_w_bazie = set()

if os.path.exists(PLIK_OBIEKTOW):
    stare_dane = pd.read_csv(PLIK_OBIEKTOW)
    if not stare_dane.empty and 'nazwa_pliku' in stare_dane.columns:
        stare_dane = stare_dane[stare_dane['nazwa_pliku'].isin(pliki_w_folderze)]
        pliki_w_bazie = set(stare_dane['nazwa_pliku'].unique())

# 3. Szukanie tylko nowych plików
nowe_pliki = list(pliki_w_folderze - pliki_w_bazie)

if not nowe_pliki:
    print("Brak nowych memów. Detekcja obiektów pominięta.")
    if not stare_dane.empty:
        stare_dane.to_csv(PLIK_OBIEKTOW, index=False)
    sys.exit(0)

print(f"Znaleziono {len(nowe_pliki)} nowych zdjęć. Ładowanie modelu YOLOv8...")
# YOLOv8n (nano) to najlżejsza i najszybsza wersja modelu. Przy pierwszym uruchomieniu pobierze się automatycznie (ok. 6 MB).
model = YOLO('yolov8n.pt', verbose=False)

nowe_wiersze = []
bledy = 0

# 4. Skanowanie nowości
for i, plik in enumerate(nowe_pliki, 1):
    sciezka = os.path.join(FOLDER_MEMOW, plik)
    try:
        # Detekcja obiektów na zdjęciu
        wyniki = model(sciezka, verbose=False)[0]

        znaleziono_obiekty = False
        for box in wyniki.boxes:
            etykieta = wyniki.names[int(box.cls)]
            pewnosc = float(box.conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()  # Współrzędne ramki

            nowe_wiersze.append({
                "nazwa_pliku": plik,
                "obiekt": etykieta,
                "pewnosc": round(pewnosc, 2),
                "x1": round(x1, 1), "y1": round(y1, 1),
                "x2": round(x2, 1), "y2": round(y2, 1)
            })
            znaleziono_obiekty = True

        # Jeśli AI nic nie znajdzie, dodajemy pusty wpis, aby plik był "odznaczony" jako sprawdzony
        if not znaleziono_obiekty:
            nowe_wiersze.append({
                "nazwa_pliku": plik, "obiekt": "brak", "pewnosc": 0.0,
                "x1": 0, "y1": 0, "x2": 0, "y2": 0
            })

    except Exception:
        bledy += 1
        nowe_wiersze.append({
            "nazwa_pliku": plik, "obiekt": "blad", "pewnosc": 0.0,
            "x1": 0, "y1": 0, "x2": 0, "y2": 0
        })

    pasek_postepu(i, len(nowe_pliki), prefiks='Skanowanie AI')

# 5. Łączenie i zapis do CSV
df_nowe = pd.DataFrame(nowe_wiersze)
df_wynik = pd.concat([stare_dane, df_nowe], ignore_index=True) if not stare_dane.empty else df_nowe
df_wynik.to_csv(PLIK_OBIEKTOW, index=False)

print(f"✅ Gotowe! Wykryto obiekty na {len(nowe_pliki)} nowych zdjęciach.")