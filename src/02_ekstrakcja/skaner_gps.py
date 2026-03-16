import os
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

FOLDER_ZDJEC = "memy"
PLIK_GPS = "lokalizacje.csv"


# Magiczna funkcja matematyczna: Zamienia Stopnie/Minuty/Sekundy na ułamek dziesiętny
def konwertuj_na_dziesietne(wartosc):
    d = float(wartosc[0])
    m = float(wartosc[1])
    s = float(wartosc[2])
    return d + (m / 60.0) + (s / 3600.0)


def pobierz_wspolrzedne(sciezka_zdjecia):
    try:
        img = Image.open(sciezka_zdjecia)
        exif = img._getexif()
        if not exif:
            return None, None

        gps_info = {}
        # Dekodowanie ukrytych tagów EXIF
        for tag, wartosc in exif.items():
            zdekodowany_tag = TAGS.get(tag, tag)
            if zdekodowany_tag == "GPSInfo":
                for t in wartosc:
                    sub_tag = GPSTAGS.get(t, t)
                    gps_info[sub_tag] = wartosc[t]

        # Jeśli zdjęcie ma ukryte tagi GPS
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            szerokosc = konwertuj_na_dziesietne(gps_info["GPSLatitude"])
            dlugosc = konwertuj_na_dziesietne(gps_info["GPSLongitude"])

            # Jeśli jesteśmy na półkuli południowej (S) lub zachodniej (W), odwracamy znak
            if gps_info.get("GPSLatitudeRef") == "S":
                szerokosc = -szerokosc
            if gps_info.get("GPSLongitudeRef") == "W":
                dlugosc = -dlugosc

            return szerokosc, dlugosc

    except Exception as e:
        print(f"⚠️ Błąd odczytu EXIF dla {sciezka_zdjecia}: {e}")

    return None, None

def skanuj_folder():
    print(f"🌍 Rozpoczynam skanowanie folderu '{FOLDER_ZDJEC}'...")
    dane = []
    pliki = [p for p in os.listdir(FOLDER_ZDJEC) if p.lower().endswith(('.jpg', '.jpeg'))]

    znaleziono_gps = 0

    for plik in pliki:
        sciezka = os.path.join(FOLDER_ZDJEC, plik)
        lat, lon = pobierz_wspolrzedne(sciezka)

        if lat is not None and lon is not None:
            dane.append({"plik": plik, "lat": lat, "lon": lon})
            znaleziono_gps += 1

    # Zapisujemy wyniki do Pandas DataFrame i do CSV
    if dane:
        df = pd.DataFrame(dane)
        df.to_csv(PLIK_GPS, index=False)
        print(f"✅ Sukces! Znaleziono lokalizację dla {znaleziono_gps} zdjęć.")
        print(f"Zapisano dane do pliku {PLIK_GPS}.")
    else:
        print("❌ Nie znaleziono żadnych zdjęć z danymi GPS. Upewnij się, że zdjęcia mają zachowane metadane (EXIF).")


if __name__ == "__main__":
    if not os.path.exists(FOLDER_ZDJEC):
        os.makedirs(FOLDER_ZDJEC)
        print(f"📁 Utworzono folder '{FOLDER_ZDJEC}'. Wrzuć tam zdjęcia ze smartfona i uruchom ponownie!")
    else:
        skanuj_folder()