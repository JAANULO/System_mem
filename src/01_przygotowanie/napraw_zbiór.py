import os
import shutil
from PIL import Image

FOLDER = "memy"
FOLDER_ZEPSUTE = "zepsute_memy"

if not os.path.exists(FOLDER_ZEPSUTE):
    os.makedirs(FOLDER_ZEPSUTE)

pliki = [p for p in os.listdir(FOLDER) if p.lower().endswith(('.jpg', '.jpeg', '.png'))]
licznik = 0

print("🔍 Szukanie uszkodzonych plików...")

for plik in pliki:
    sciezka = os.path.join(FOLDER, plik)
    try:
        # verify() sprawdza integralność pliku bez ładowania go w całości do RAM
        with Image.open(sciezka) as img:
            img.verify()
    except Exception as e:
        print(f"❌ Wykryto uszkodzony plik: {plik} -> Przenoszę...")
        sciezka_zepsute = os.path.join(FOLDER_ZEPSUTE, plik)
        shutil.move(sciezka, sciezka_zepsute)
        licznik += 1

print("-" * 40)
print(f"✅ Zakończono! Przeniesiono {licznik} plików z błędami do folderu '{FOLDER_ZEPSUTE}'.")