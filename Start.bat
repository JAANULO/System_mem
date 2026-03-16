@echo off
cd /d "C:\Users\atona\Desktop\Projekty\System_memow"

python src\05_narzedzia\sprawdz_nowe.py
if %ERRORLEVEL% EQU 1 (
    echo Wykryto zmiany w folderze. Aktualizacja bazy danych...
    python src\01_przygotowanie\bezpieczne_nazwy.py
    python src\02_ekstrakcja\ekstrakcja_cech.py
    python src\02_ekstrakcja\czytaj_tekst.py
    python src\02_ekstrakcja\czytanie_AI.py
) else (
    echo Brak zmian w folderze. Pomijanie aktualizacji.
)

echo Uruchamianie aplikacji...
python -m streamlit run app.py
pause