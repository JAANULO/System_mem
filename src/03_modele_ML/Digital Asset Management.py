import os
import sys
import torch
import pandas as pd
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from transformers import CLIPProcessor, CLIPModel
from sklearn.cluster import DBSCAN
import warnings

if np.__version__.startswith("2."):
    np.int = int
    np.float = float
    np.bool = bool

warnings.filterwarnings("ignore")

# --- KONFIGURACJA ---
# Upewnij się, że ten folder ze zdjęciami istnieje na pulpicie/w projekcie!
FOLDER_ZDJEC = "memy"
PLIK_WYNIKOWY = "baza_hybrydowa.pkl"
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def pasek_postepu(current, total, bar_length=40):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * "█" + "█"
    padding = int(bar_length - len(arrow)) * "-"
    ending = '\n' if current == total else '\r'
    print(f"Przetwarzanie |{arrow}{padding}| {current}/{total} ({fraction*100:.1f}%)", end=ending)

# --- KROK 1: INICJALIZACJA MODELI ---
print("Krok 1: Inicjalizacja modeli na urządzeniu:", device)

# CLIP (Semantyka)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Facenet (Twarze)
mtcnn = MTCNN(keep_all=False, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# --- KROK 2: PRZETWARZANIE PLIKÓW ---
if not os.path.exists(FOLDER_ZDJEC):
    print(f"BŁĄD: Folder '{FOLDER_ZDJEC}' nie istnieje!")
    sys.exit()

pliki = [f for f in os.listdir(FOLDER_ZDJEC) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
calkowita_liczba = len(pliki)
dane_obrazow = []
wektory_twarzy_do_klastrowania = []
indeksy_twarzy = []
bledy = 0

print(f"Krok 2: Wektoryzacja twarzy i semantyki ({calkowita_liczba} plików)...")

if calkowita_liczba > 0:
    for i, plik in enumerate(pliki):
        sciezka = os.path.join(FOLDER_ZDJEC, plik)
        try:
            img = Image.open(sciezka).convert('RGB')

            # --- Wektoryzacja semantyczna (CLIP) ---
            inputs = clip_processor(images=img, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = clip_model.get_image_features(**inputs)

                # --- BEZPIECZNE WYCIĄGANIE WEKTORA ---
                if isinstance(outputs, torch.Tensor):
                    clip_wektor = outputs.cpu().numpy().flatten()
                elif hasattr(outputs, "image_embeds"):
                    clip_wektor = outputs.image_embeds.cpu().numpy().flatten()
                else:
                    # Ostateczność: bierzemy pierwszy element wyjściowy
                    clip_wektor = outputs[0].cpu().numpy().flatten()

            # --- Detekcja i wektoryzacja twarzy (Facenet) ---
            twarz_wektor = None
            twarz_kropnieta = mtcnn(img)

            if twarz_kropnieta is not None:
                # mtcnn zwraca tensor [3, 160, 160], resnet wymaga [1, 3, 160, 160]
                twarz_kropnieta = twarz_kropnieta.unsqueeze(0).to(device)
                with torch.no_grad():
                    twarz_cechy = resnet(twarz_kropnieta)
                    twarz_wektor = twarz_cechy.cpu().numpy().flatten()

            # Zapis do struktury
            rekord = {
                "nazwa_pliku": plik,
                "clip_wektor": clip_wektor,
                "klasa_osoby": "Brak_twarzy"  # Wartość domyślna
            }
            dane_obrazow.append(rekord)

            if twarz_wektor is not None:
                wektory_twarzy_do_klastrowania.append(twarz_wektor)
                indeksy_twarzy.append(len(dane_obrazow) - 1)

        except Exception as e:
            print(f"\nBłąd w pliku {plik}: {e}")
            bledy += 1

        pasek_postepu(i + 1, calkowita_liczba)

    print("Krok 3: Klastrowanie wykrytych twarzy (DBSCAN)...")
    if len(wektory_twarzy_do_klastrowania) > 0:
        matryca_twarzy = np.array(wektory_twarzy_do_klastrowania)

        # Parametr eps i min_samples zależą od zbioru.
        # eps=0.7 to standard dla znormalizowanych wektorów VGGface2.
        klastrowanie = DBSCAN(eps=0.6, min_samples=2, metric='euclidean').fit(matryca_twarzy)
        etykiety = klastrowanie.labels_

        # Aktualizacja rekordów o nazwy klas
        for idx_wiersza, etykieta in zip(indeksy_twarzy, etykiety):
            if etykieta == -1:
                dane_obrazow[idx_wiersza]["klasa_osoby"] = "Osoba_nieznana"
            else:
                dane_obrazow[idx_wiersza]["klasa_osoby"] = f"Osoba_{etykieta}"

        unikalne_osoby = len(set(etykiety)) - (1 if -1 in etykiety else 0)
        print(f"Zidentyfikowano unikalnych osób: {unikalne_osoby}")
    else:
        print("Nie wykryto żadnych twarzy w zbiorze.")

    print(f"Krok 4: Zapisywanie hybrydowej bazy danych do {PLIK_WYNIKOWY}...")
    df = pd.DataFrame(dane_obrazow)
    df.to_pickle(PLIK_WYNIKOWY)

    przetworzone = calkowita_liczba - bledy
    dlugosc_paska = 40
    zapelnienie = int((przetworzone / calkowita_liczba) * dlugosc_paska)
    wiz_pasek = '█' * zapelnienie + '░' * (dlugosc_paska - zapelnienie)

    print(
        f"\n📊 Skuteczność: |{wiz_pasek}| {przetworzone}/{calkowita_liczba} ({przetworzone / calkowita_liczba * 100:.1f}%)")
    if bledy > 0:
        print(f"Błędy przetwarzania (zignorowano): {bledy}")
else:
    print("Brak plików do przetworzenia.")