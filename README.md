# System_memów

Zaawansowany system do zarządzania, analizy i kategoryzacji memów z użyciem sztucznej inteligencji i uczenia maszynowego.

---

## 📋 Spis treści

1. [Opis ogólny](#opis-ogólny)
2. [Struktura plików](#struktura-plików)
3. [Wymagania](#wymagania)
4. [Instalacja](#instalacja)
5. [Uruchamianie](#uruchamianie)

---

## 🎯 Opis ogólny

Projekt **System_memów** to kompleksowe narzędzie do przetwarzania, analizy i oceny zbiorów memów. System wykorzystuje zaawansowane techniki przetwarzania obrazów, uczenia maszynowego oraz sztucznej inteligencji do kategoryzacji i organizacji materiałów.

Główne cechy:
- 🎬 Interaktywna aplikacja Streamlit do oceniania memów
- 🤖 Analiza AI (CLIP, FaceNet) do rozpoznawania twarzy i semantyki
- 🎨 Ekstrakcja cech wizualnych (kolor, rozmiar, jasność)
- 📖 Czytanie tekstu z obrazów (OCR - EasyOCR)
- 📊 Automatyczna klasyfikacja memów na grupy (K-Means)
- 🔍 Walidacja integralności plików

---

## 📁 Struktura plików

### 🎬 **app.py** - Główna aplikacja Streamlit
**Funkcja:** Interfejs do oceniania memów w przeglądarce
- Wyświetla losowe memy z kolekcji
- Pozwala na ocenianie ich w skali (np. 1-10)
- Buforuje głosy w RAM dla wydajności
- Zapisuje wyniki do `wyniki.csv`
- Oferuje statystyki i wizualizacje

### 🔐 **bezpieczne_nazwy.py** - Standaryzacja nazw plików
**Funkcja:** Zmienia nazwy memów na bezpieczne i unikalne
- Generuje nazwy oparte na haszach MD5 zawartości pliku
- Zapewnia, że duplikaty zostaną wykryte
- Zachowuje oryginalne rozszerzenia (.jpg, .png)
- Przykład: `memorial.jpg` → `a1b2c3d4e5.jpg`

### 🎨 **ekstrakcja_cech.py** - Analiza wizualna memów
**Funkcja:** Zbiera dane o cechach wizualnych każdego mema
- Waga pliku (rozmiar w KB)
- Wymiary (szerokość, wysokość)
- Proporcje obrazu
- Jasność (brightness)
- Dominujące kolory RGB
- Eksportuje dane do `cechy_memow.csv`

### 📖 **czytaj_tekst.py** - Optyczne rozpoznawanie znaków (OCR)
**Funkcja:** Wyodrębnia tekst z obrazów memów
- Używa modelu EasyOCR (obsługuje polski i angielski)
- Pozwala na GPU (jeśli dostępne)
- Dodaje kolumnę tekstową do `cechy_memow.csv`
- Przydatne do analizy zawartości memów

### 🤖 **Digital Asset Management.py** - Zaawansowana analiza AI
**Funkcja:** Deeplearning dla rozpoznawania twarzy i semantyki
- Używa CLIP (OpenAI) do rozumienia semantyki
- FaceNet/MTCNN do detekcji i reprezentacji twarzy
- Tworzy wektory cech dla każdego mema
- Zapisuje wyniki do `baza_hybrydowa.pkl`
- Grupuje podobne memy (DBSCAN)

### 📊 **grupuj_memy.py** - Automatyczna klasyfikacja
**Funkcja:** Dzieli memy na grupy na podstawie cech
- Używa algorytmu K-Means (Machine Learning)
- Standaryzuje cechy przed klasteryzacją
- Dodaje kolumnę `Grupa` do `cechy_memow.csv`
- **Wymaga:** najpierw uruchomić `szukanie_grup.py` aby wybrać liczbę grup

### 🔍 **szukanie_grup.py** - Metoda Łokcia do wyboru liczby grup
**Funkcja:** Pomaga ustalić optymalną liczbę klastrów
- Testuje K-Means dla 1-10 grup
- Rysuje wykres WCSS (Within-Cluster Sum of Squares)
- Szukaj "łokcia" na wykresie - tam jest optymalnie
- Wynik wpisz w `grupuj_memy.py` jako `LICZBA_GRUP`

### 🛠️ **napraw_zbiór.py** - Walidacja integralności
**Funkcja:** Szuka i przesyła uszkodzonych memów
- Weryfikuje, czy każdy plik jest poprawnym obrazem
- Uszkodzonych pliki przenoszone do `zepsute_memy/`
- Bezpieczna operacja - nie usuwa, tylko przenosi

### ✅ **sprawdz_nowe.py** - Sprawdzenie nowych memów
**Funkcja:** Porównuje plik z bazą
- Wykrywa memy w folderze, które nie są w `cechy_memow.csv`
- Przydatne gdy dodajesz nowe memy
- Wyświetla listę zmian

### 📝 **zmien_nazwy.py** - Ujednolicenie nazw
**Funkcja:** Zmienia nazwy memów na ujednolicony format
- Konwertuje wszystko na kolejne numery: `mem_1.jpg`, `mem_2.jpg`...
- Konwertuje PNG na JPG
- Usuwa duplikaty rozszerzeń
- Szybka standaryzacja przed analizą

### 📊 **pokazanie_bazy.py** - Podgląd bazy
**Funkcja:** Wyświetla zawartość bazy hybrydowej
- Wczytuje `baza_hybrydowa.pkl`
- Pokazuje pierwsze 5 wierszy tabeli
- Przydatne do debugowania

### 📁 **Foldery**
- **`memy/`** - Folder zawierający wszystkie memy (obrazy)
- **`zepsute_memy/`** - Uszkodzonych pliki (automatycznie tworzone)

### 📊 **Pliki danych**
- **`cechy_memow.csv`** - Tabela z cechami wszystkich memów (generowana)
- **`wyniki.csv`** - Oceny memów z aplikacji (generowana)
- **`baza_hybrydowa.pkl`** - Baza z analiza AI (generowana)

---

## 📦 Wymagania

```
Python 3.8+
streamlit
pandas
pillow
colorthief
scikit-learn
easyocr
plotly
torch
facenet-pytorch
transformers
```

---

## 🚀 Instalacja

### Krok 1: Klonowanie repozytorium
```bash
git clone https://github.com/JAANULO/System_mem-w.git
cd System_mem-w
```

### Krok 2: Utworzenie wirtualnego środowiska (opcjonalnie)
```bash
python -m venv venv
venv\Scripts\activate
```

### Krok 3: Instalacja zależności
```bash
pip install -r requirements.txt
```

---

## 🎬 Uruchamianie

### **Opcja 1: Uruchomienie głównej aplikacji (Streamlit)**
```bash
streamlit run app.py
```
Aplikacja otworzy się w przeglądarce na `http://localhost:8501`

### **Opcja 2: Analiza memów (workflow)**

Rekomendowana kolejność uruchomienia skryptów:

1. **Standaryzacja nazw** (pierwszy raz):
   ```bash
   python zmien_nazwy.py
   ```
   lub
   ```bash
   python bezpieczne_nazwy.py
   ```

2. **Walidacja plików** (opcjonalnie):
   ```bash
   python napraw_zbiór.py
   ```

3. **Ekstrakcja cech wizualnych**:
   ```bash
   python ekstrakcja_cech.py
   ```

4. **OCR - Czytanie tekstu** (opcjonalnie, wymaga GPU):
   ```bash
   python czytaj_tekst.py
   ```

5. **Zaawansowana analiza AI** (opcjonalnie, wymaga GPU/CUDA):
   ```bash
   python Digital\ Asset\ Management.py
   ```

6. **Wybór optymalnej liczby grup**:
   ```bash
   python szukanie_grup.py
   ```
   (Obejrzyj wykres i zapamiętaj punkt "łokcia")

7. **Klasyfikacja memów na grupy**:
   ```bash
   python grupuj_memy.py
   ```

8. **Sprawdzenie nowych memów** (gdy dodasz nowe):
   ```bash
   python sprawdz_nowe.py
   ```

9. **Podgląd bazy hybrydowej** (jeśli uruchomiłeś krok 5):
   ```bash
   python pokazanie_bazy.py
   ```

### **Opcja 3: Szybki start (batch)**
```bash
Start.bat
```
(Plik automatycznie uruchamia wybrane skrypty)

---

## 📈 Przykładowy workflow

1. Dodaj memy do folderu `memy/`
2. Uruchom `python ekstrakcja_cech.py` - analiza
3. Uruchom `python szukanie_grup.py` - zobacz wykres
4. Edytuj `grupuj_memy.py` - ustaw `LICZBA_GRUP`
5. Uruchom `python grupuj_memy.py` - klasyfikacja
6. Uruchom `streamlit run app.py` - oceniaj memy!

---

## 🔧 Konfiguracja

Można edytować stałe w poszczególnych plikach:

```python
FOLDER_MEMOW = "memy"           # Folder z memami
PLIK_WYNIKOW = "wyniki.csv"     # Plik z ocenami
PLIK_CECH = "cechy_memow.csv"   # Baza cech
LICZBA_GRUP = 8                 # Liczba klastrów (w grupuj_memy.py)
```

---

## 💾 Dane wyjściowe

Projekt generuje następujące pliki:

| Plik | Opis |
|------|------|
| `cechy_memow.csv` | Wszystkie cechy memów |
| `wyniki.csv` | Oceny memów z aplikacji |
| `baza_hybrydowa.pkl` | Wektory AI + twarze |
| `zepsute_memy/` | Przeniesione uszkodzone pliki |

---

## 👨‍💻 Autor

**JAANULO**

---

## 📄 Licencja

Projekt przeznaczony do użytku edukacyjnego i badawczego.

