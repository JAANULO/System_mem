import os
from PIL import Image

# Konfiguracja
FOLDER_MEMOW = "memy"
PREFIX = "mem_"

print("Rozpoczynam ujednolicanie i zmianę nazw...")

# Skanujemy folder w poszukiwaniu obrazków
memy = [plik for plik in os.listdir(FOLDER_MEMOW) if plik.lower().endswith(('.png', '.jpg', '.jpeg'))]

licznik = 1

for stara_nazwa in memy:
    stara_sciezka = os.path.join(FOLDER_MEMOW, stara_nazwa)

    # Wymuszamy, aby nowa nazwa ZAWSZE miała końcówkę .jpg
    nowa_nazwa = f"{PREFIX}{licznik}.jpg"
    nowa_sciezka = os.path.join(FOLDER_MEMOW, nowa_nazwa)

    try:
        # Otwieramy stary plik (niezależnie czy to .png, .jpeg czy .jpg)
        with Image.open(stara_sciezka) as img:
            # Konwertujemy do trybu RGB (wymagane, by zapisać przezroczyste PNG jako JPG)
            rgb_im = img.convert('RGB')
            # Zapisujemy obrazek w nowym miejscu jako ustandaryzowany plik JPEG
            rgb_im.save(nowa_sciezka, 'JPEG')

        # Sprzątanie: usuwamy stary plik, jeśli jego nazwa lub rozszerzenie były inne
        if stara_sciezka != nowa_sciezka:
            os.remove(stara_sciezka)

        licznik += 1
    except Exception as e:
        print(f"⚠️ Błąd przy przetwarzaniu pliku {stara_nazwa}: {e}")

print(f"✅ Sukces! Przekonwertowano i uporządkowano {licznik - 1} plików.")