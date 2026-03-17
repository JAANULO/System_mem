import os
import hashlib

FOLDER_MEMOW = "data/memy"


def bezpieczna_zmiana_nazw():
    print("Rozpoczynam bezpieczną standaryzację nazw (MD5)...")

    # Ujednolicona lista rozszerzeń
    pliki = [p for p in os.listdir(FOLDER_MEMOW) if p.lower().endswith(('.jpg', '.jpeg', '.png'))]

    licznik_zmian = 0
    licznik_duplikatow = 0

    for plik in pliki:
        stara_sciezka = os.path.join(FOLDER_MEMOW, plik)

        with open(stara_sciezka, "rb") as f:
            hash_md5 = hashlib.md5()
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
            hash_pliku = hash_md5.hexdigest()

            #bajty = f.read()
            #hash_pliku = hashlib.md5(bajty).hexdigest()

        # Pobranie oryginalnego rozszerzenia, aby nie uszkodzić plików PNG
        _, rozszerzenie = os.path.splitext(plik)

        nowa_nazwa = f"{hash_pliku[:10]}{rozszerzenie.lower()}"
        nowa_sciezka = os.path.join(FOLDER_MEMOW, nowa_nazwa)

        if stara_sciezka == nowa_sciezka:
            continue

        if os.path.exists(nowa_sciezka):
            print(f"Znaleziono duplikat! Usuwam: {plik}")
            os.remove(stara_sciezka)
            licznik_duplikatow += 1
        else:
            os.rename(stara_sciezka, nowa_sciezka)
            licznik_zmian += 1

    print("-" * 40)
    print(f"Zakończono! Zmieniono nazwę {licznik_zmian} plików.")
    if licznik_duplikatow > 0:
        print(f"Przy okazji usunięto {licznik_duplikatow} identycznych duplikatów.")


if __name__ == "__main__":
    bezpieczna_zmiana_nazw()