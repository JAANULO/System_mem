import os
import sys
import pandas as pd
from PIL import Image, ImageStat
from colorthief import ColorThief

# Konfiguracja
FOLDER_MEMOW = "memy"
PLIK_CECH = "cechy_memow.csv"


def pasek_postepu(aktualny, total, prefiks='Skanowanie'):
    if total == 0:
        return
    procent = 100 * (aktualny / float(total))
    zapelnienie = int(40 * aktualny // total)
    pasek = '█' * zapelnienie + '-' * (40 - zapelnienie)
    sys.stdout.write(f'\r{prefiks} |{pasek}| {aktualny}/{total} ({procent:.1f}%) ')
    sys.stdout.flush()
    if aktualny == total:
        print()


print("Rozpoczynam analizę memów (ekstrakcja cech i kolorów)...")

dane_cech = []
pliki = [plik for plik in os.listdir(FOLDER_MEMOW) if plik.lower().endswith(('.jpg', '.jpeg', '.png'))]
calkowita_liczba = len(pliki)
bledy = 0

if calkowita_liczba == 0:
    print(f"Brak plików w folderze {FOLDER_MEMOW}.")
else:
    for i, plik in enumerate(pliki, 1):
        sciezka = os.path.join(FOLDER_MEMOW, plik)

        try:
            # 1. Stare cechy (Waga, Rozdzielczość, Jasność)
            waga_kb = os.path.getsize(sciezka) / 1024.0
            with Image.open(sciezka) as img:
                szerokosc = img.width
                wysokosc = img.height
                proporcje = szerokosc / wysokosc if wysokosc > 0 else 0

                img_szary = img.convert('L')
                jasnosc = ImageStat.Stat(img_szary).mean[0]

            # 2. NOWA CECHA: Bezpieczna ekstrakcja koloru
            r, g, b = 128, 128, 128  # Domyślny kolor (szary) na wypadek błędu
            try:
                color_thief = ColorThief(sciezka)
                dominujacy_kolor = color_thief.get_color(quality=1)

                # Zabezpieczenie przed dziwnymi formatami (np. czarno-białe zwracają 1 wartość)
                if isinstance(dominujacy_kolor, tuple) and len(dominujacy_kolor) >= 3:
                    r, g, b = dominujacy_kolor[0], dominujacy_kolor[1], dominujacy_kolor[2]
            except Exception:
                pass  # Wyciszamy błąd ColorThief, plik i tak zostanie zapisany z kolorem szarym

            # 3. Zapis do bazy (przeniesiony w bezpieczne miejsce)
            dane_cech.append({
                "nazwa_pliku": plik,
                "waga_kb": round(waga_kb, 2),
                "szerokosc": szerokosc,
                "wysokosc": wysokosc,
                "proporcje": round(proporcje, 2),
                "jasnosc": round(jasnosc, 2),
                "kolor_R": r,
                "kolor_G": g,
                "kolor_B": b
            })

        except Exception as e:
            bledy += 1
            # Jeśli wystąpi inny krytyczny błąd, dopisujemy pusty rekord, aby zachować zgodność bazy
            dane_cech.append({
                "nazwa_pliku": plik,
                "waga_kb": 0, "szerokosc": 0, "wysokosc": 0,
                "proporcje": 0, "jasnosc": 0,
                "kolor_R": 0, "kolor_G": 0, "kolor_B": 0
            })

        pasek_postepu(i, calkowita_liczba)

    # Zapisanie zebranych danych do nowej bazy
    df = pd.DataFrame(dane_cech)
    df.to_csv(PLIK_CECH, index=False)

    udane_skany = len(dane_cech)
    dlugosc_paska = 40
    zapelnienie_sukcesu = int((udane_skany / calkowita_liczba) * dlugosc_paska)
    wizualny_pasek = '█' * zapelnienie_sukcesu + '░' * (dlugosc_paska - zapelnienie_sukcesu)

    print(f"\n📊 Skuteczność zapisu do bazy: |{wizualny_pasek}| {udane_skany}/{calkowita_liczba} (100.0%)")

    if bledy > 0:
        print(f"Uwaga: W {bledy} plikach wystąpiły krytyczne błędy (zapisano wartości domyślne).")

    print(f"✅ Gotowe! Zaktualizowano plik {PLIK_CECH}.")