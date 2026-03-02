import os
import sys
import pandas as pd

FOLDER = "memy"
CSV = "cechy_memow.csv"

if not os.path.exists(CSV):
    print("Brak pliku CSV.")
    sys.exit(1)

pliki_w_folderze = set([p for p in os.listdir(FOLDER) if p.lower().endswith(('.jpg', '.jpeg', '.png'))])

try:
    df = pd.read_csv(CSV)

    # 1. Automatyczne wykrywanie nazwy kolumny
    kolumna = None
    for mozliwa_nazwa in ['nazwa_pliku', 'plik', 'file', 'nazwa']:
        if mozliwa_nazwa in df.columns:
            kolumna = mozliwa_nazwa
            break

    if not kolumna:
        print(f"Błąd: Nie znaleziono kolumny z nazwą pliku w CSV. Dostępne kolumny: {df.columns.tolist()}")
        sys.exit(1)

    # 2. Pobranie samych nazw (usuwa foldery ze ścieżki, jeśli są)
    pliki_w_bazie = set([os.path.basename(str(p)) for p in df[kolumna].tolist()])

    # 3. Szukanie różnic
    brakuje_w_bazie = pliki_w_folderze - pliki_w_bazie

    if not brakuje_w_bazie:
        print("Baza jest aktualna. Pomijam skanowanie.")
        sys.exit(0)
    else:
        print(f"Baza jest nieaktualna. Brakuje {len(brakuje_w_bazie)} plików w CSV.")
        print(f"Przykładowe brakujące pliki: {list(brakuje_w_bazie)[:3]}")
        sys.exit(1)

except Exception as e:
    print(f"Błąd odczytu bazy: {e}")
    sys.exit(1)