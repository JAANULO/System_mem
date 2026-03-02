import pandas as pd
import easyocr
import os
import sys
import warnings

# Wyłączenie ostrzeżeń z biblioteki PyTorch
warnings.filterwarnings("ignore", category=UserWarning)

# Konfiguracja
PLIK_CECH = "cechy_memow.csv"
FOLDER_MEMOW = "memy"


def pasek_postepu(aktualny, total, prefiks='Analiza OCR'):
    if total == 0:
        return
    procent = 100 * (aktualny / float(total))
    zapelnienie = int(40 * aktualny // total)
    pasek = '█' * zapelnienie + '-' * (40 - zapelnienie)
    sys.stdout.write(f'\r{prefiks} |{pasek}| {aktualny}/{total} ({procent:.1f}%) ')
    sys.stdout.flush()
    if aktualny == total:
        print()


print("Ładowanie modelu AI do czytania tekstu (EasyOCR)...")
reader = easyocr.Reader(['pl', 'en'], gpu=True)

df = pd.read_csv(PLIK_CECH)

if 'czy_ma_tekst' not in df.columns:
    df['czy_ma_tekst'] = 0
    df['wykryty_tekst'] = ""

calkowita_liczba = len(df)
bledy = 0
z_tekstem = 0

print("Rozpoczynam analizę OCR...")

if calkowita_liczba > 0:
    for index, row in df.iterrows():
        plik = row['nazwa_pliku']
        sciezka = os.path.join(FOLDER_MEMOW, plik)

        try:
            wyniki = reader.readtext(sciezka, detail=0)
            caly_tekst = " ".join(wyniki).strip()

            if len(caly_tekst) > 0:
                df.at[index, 'czy_ma_tekst'] = 1
                df.at[index, 'wykryty_tekst'] = caly_tekst
                z_tekstem += 1
            else:
                df.at[index, 'czy_ma_tekst'] = 0
                df.at[index, 'wykryty_tekst'] = ""
        except Exception:
            bledy += 1

        pasek_postepu(index + 1, calkowita_liczba)

    df.to_csv(PLIK_CECH, index=False)

    przetworzone = calkowita_liczba - bledy
    procent_sukcesu = (przetworzone / calkowita_liczba) * 100
    dlugosc_paska = 40
    zapelnienie_sukcesu = int((przetworzone / calkowita_liczba) * dlugosc_paska)
    wizualny_pasek = '█' * zapelnienie_sukcesu + '░' * (dlugosc_paska - zapelnienie_sukcesu)

    print(f"\n📊 Skuteczność analizy: |{wizualny_pasek}| {przetworzone}/{calkowita_liczba} ({procent_sukcesu:.1f}%)")
    print(f"Znaleziono tekst na {z_tekstem} obrazach.")

    if bledy > 0:
        print(f"Błędy przetwarzania (zignorowano): {bledy}")

    print(f"Gotowe. Zaktualizowano plik {PLIK_CECH}.")
else:
    print("Brak danych w pliku CSV do przetworzenia.")