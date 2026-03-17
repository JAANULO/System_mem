import os
import sys
import pandas as pd

FOLDER = "data/memy"
CSV = "data/cechy_memow.csv"

if not os.path.exists(CSV):
    print("Brak pliku CSV. Wymagane pełne skanowanie.")
    sys.exit(1)

# 1. Pobranie nazw plików z folderu
pliki_w_folderze = {p for p in os.listdir(FOLDER) if p.lower().endswith(('.jpg', '.jpeg', '.png'))}

#pliki_w_folderze = set([p for p in os.listdir(FOLDER) if p.lower().endswith(('.jpg', '.jpeg', '.png'))])

try:
    df = pd.read_csv(CSV)

    # 2. Automatyczne wykrywanie nazwy kolumny w CSV
    kolumna = None
    for mozliwa_nazwa in ['nazwa_pliku', 'plik', 'file', 'nazwa']:
        if mozliwa_nazwa in df.columns:
            kolumna = mozliwa_nazwa
            break

    if not kolumna:
        print(f"Błąd: Nie znaleziono kolumny z nazwą pliku w CSV. Dostępne kolumny: {df.columns.tolist()}")
        sys.exit(1)

    # 3. Pobranie samych nazw plików z bazy
    pliki_w_bazie = set([os.path.basename(str(p)) for p in df[kolumna].tolist()])

    # 4. Szukanie różnic w obie strony
    if pliki_w_folderze == pliki_w_bazie:
        print("Baza jest aktualna. Pomijam skanowanie.")
        sys.exit(0)
    else:
        nowe = pliki_w_folderze - pliki_w_bazie
        usuniete = pliki_w_bazie - pliki_w_folderze

        print("Baza jest nieaktualna.")
        if nowe:
            print(f"➕ Wykryto {len(nowe)} nowych plików w folderze.")
        if usuniete:
            print(f"➖ Wykryto brak {len(usuniete)} plików (zostały usunięte z folderu).")

        sys.exit(1)  # Zwraca błąd, żeby plik .bat uruchomił skanowanie

except Exception as e:
    print(f"Błąd odczytu bazy: {e}")
    sys.exit(1)