# System_memów

Zaawansowany system do zarządzania, analizy i kategoryzacji memów z
użyciem sztucznej inteligencji i uczenia maszynowego.

------------------------------------------------------------------------

# 📋 Spis treści

1.  Opis ogólny\
2.  Struktura projektu\
3.  Wymagania\
4.  Instalacja\
5.  Uruchamianie i Pipeline

------------------------------------------------------------------------

# 🎯 Opis ogólny

Projekt **System_memów** to kompleksowe narzędzie (data pipeline) do
przetwarzania, analizy i oceny zbiorów obrazów. System wykorzystuje
techniki:

-   Computer Vision\
-   Machine Learning\
-   Artificial Intelligence

do głębokiej kategoryzacji materiałów wizualnych.

## Główne funkcje

-   🎬 Interaktywna aplikacja **Streamlit** do oceniania memów
    (Tinder-like UI)
-   🤖 Analiza AI (**CLIP**, **YOLOv8**, **FaceNet**)
-   🎨 Ekstrakcja cech wizualnych (RGB, rozmiar, jasność, EXIF/GPS)
-   📖 OCR (EasyOCR)
-   📊 Automatyczna klasteryzacja (**K-Means**, **DBSCAN**)
-   🔍 Walidacja integralności plików (**MD5 hashing**)

------------------------------------------------------------------------

# 📁 Struktura projektu

    System_mem/
    │
    ├── data/
    │   ├── memy/
    │   ├── zepsute_memy/
    │   ├── cechy_memow.csv
    │   ├── obiekty_memow.csv
    │   ├── wyniki.csv
    │   ├── lokalizacje.csv
    │   └── baza_hybrydowa.pkl
    │
    ├── src/
    │   ├── 01_przygotowanie/
    │   │   ├── bezpieczne_nazwy.py
    │   │   ├── zmien_nazwy.py
    │   │   └── napraw_zbior.py
    │
    │   ├── 02_ekstrakcja/
    │   │   ├── ekstrakcja_cech.py
    │   │   ├── czytaj_tekst.py
    │   │   ├── czytanie_AI.py
    │   │   └── skaner_gps.py
    │
    │   ├── 03_modele_ML/
    │   │   ├── szukanie_grup.py
    │   │   ├── grupuj_memy.py
    │   │   └── digital_asset_management.py
    │
    │   ├── 04_generatory/
    │   │   ├── generuj_gradient.py
    │   │   └── generuj_mozaike.py
    │
    │   └── 05_narzedzia/
    │       ├── sprawdz_nowe.py
    │       └── pokazanie_bazy.py
    │
    ├── app.py
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

# 🎬 app.py --- Interfejs Webowy

Aplikacja Streamlit zawiera cztery główne moduły:

### 1️⃣ Ocenianie memów (Tinder UI)

-   szybkie głosowanie
-   zapisy buforowane w RAM
-   zapis do pliku co 5 głosów

### 2️⃣ Korekta OCR

Możliwość ręcznego poprawienia tekstu odczytanego przez OCR.

### 3️⃣ Jak widzi to AI

Wyświetlanie **bounding boxes YOLO** na obrazach.

### 4️⃣ Dashboard

Interaktywne wykresy **Plotly** analizujące:

-   preferencje użytkowników
-   trendy ocen
-   statystyki zbioru

------------------------------------------------------------------------

# 📦 Wymagania

-   Python **3.8+**

Najważniejsze biblioteki:

-   streamlit
-   pandas
-   scikit-learn
-   torch
-   ultralytics
-   easyocr

Lista pełnych zależności znajduje się w `requirements.txt`.

------------------------------------------------------------------------

# 🚀 Instalacja

## 1️⃣ Klonowanie repozytorium

``` bash
git clone https://github.com/JAANULO/System_mem.git
cd System_mem
```

## 2️⃣ Utworzenie wirtualnego środowiska

``` bash
python -m venv venv
```

### Windows

``` bash
venv\Scripts\activate
```

### Linux / Mac

``` bash
source venv/bin/activate
```

## 3️⃣ Instalacja bibliotek

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# 📈 Uruchamianie Pipeline

## 1️⃣ Dodaj obrazy

Wklej memy do folderu:

    data/memy/

## 2️⃣ Czyszczenie danych

``` bash
python src/01_przygotowanie/bezpieczne_nazwy.py
python src/01_przygotowanie/napraw_zbior.py
```

## 3️⃣ Ekstrakcja cech

``` bash
python src/02_ekstrakcja/ekstrakcja_cech.py
python src/02_ekstrakcja/czytanie_AI.py
python src/02_ekstrakcja/czytaj_tekst.py
```

## 4️⃣ Strojenie modeli ML

``` bash
python src/03_modele_ML/szukanie_grup.py
```

Na wykresie **WCSS** znajdź punkt załamania krzywej (metoda łokcia) i
ustaw:

    LICZBA_GRUP = X

w pliku:

    grupuj_memy.py

## 5️⃣ Klasteryzacja

``` bash
python src/03_modele_ML/grupuj_memy.py
```

## 6️⃣ Uruchomienie aplikacji

``` bash
streamlit run app.py
```

------------------------------------------------------------------------

# 🔧 Konfiguracja ścieżek

W plikach w folderze `src`:

``` python
FOLDER_MEMOW = "../../data/memy"
PLIK_CECH = "../../data/cechy_memow.csv"
```

W pliku `app.py`:

``` python
FOLDER_MEMOW = "data/memy"
PLIK_WYNIKOW = "data/wyniki.csv"
```

