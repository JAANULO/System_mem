import os
import sys
import pandas as pd
from PIL import Image, ImageStat
from colorthief import ColorThief

# Konfiguracja
FOLDER_MEMOW = "memy"
PLIK_CECH = "cechy_memow.csv"


# Funkcja generująca pasek postępu
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
    print(f"Brak plików .jpg w folderze {FOLDER_MEMOW}.")
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

            # 2. NOWA CECHA: Dominujący kolor (R, G, B)
            color_thief = ColorThief(sciezka)
            dominujacy_kolor = color_thief.get_color(quality=1)

            # Zapisujemy wszystko do naszej bazy
            dane_cech.append({
                "nazwa_pliku": plik,
                "waga_kb": round(waga_kb, 2),
                "szerokosc": szerokosc,
                "wysokosc": wysokosc,
                "proporcje": round(proporcje, 2),
                "jasnosc": round(jasnosc, 2),
                "kolor_R": dominujacy_kolor[0],
                "kolor_G": dominujacy_kolor[1],
                "kolor_B": dominujacy_kolor[2]
            })

        except Exception as e:
            print(f"\n❌ Błąd przy ekstrakcji pliku {plik}: {e}")

        # Aktualizacja paska postępu
        pasek_postepu(i, calkowita_liczba)

    # Zapisanie zebranych danych do nowej bazy
    df = pd.DataFrame(dane_cech)
    df.to_csv(PLIK_CECH, index=False)

    # Statystyki końcowe
    udane_skany = len(dane_cech)
    procent_sukcesu = (udane_skany / calkowita_liczba) * 100
    dlugosc_paska = 40
    zapelnienie_sukcesu = int((udane_skany / calkowita_liczba) * dlugosc_paska)
    wizualny_pasek = '█' * zapelnienie_sukcesu + '░' * (dlugosc_paska - zapelnienie_sukcesu)

    print(f"\n📊 Skuteczność analizy: |{wizualny_pasek}| {udane_skany}/{calkowita_liczba} ({procent_sukcesu:.1f}%)")

    if bledy > 0:
        print(f"Błędy przetwarzania (zignorowano): {bledy}")

    print(f"✅ Gotowe! Zaktualizowano plik {PLIK_CECH} o kolory RGB z {udane_skany} memów.")