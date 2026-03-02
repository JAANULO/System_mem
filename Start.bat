@echo off
cd /d "C:\Users\atona\Desktop\Projekty\System_memow"

python sprawdz_nowe.py

if %ERRORLEVEL% EQU 1 (
    echo Wykryto zmiany w folderze. Aktualizacja bazy danych...

    python bezpieczne_nazwy.py

    python ekstrakcja_cech.py

) else (
    echo Brak zmian w folderze. Pomijanie aktualizacji.
)

echo Uruchamianie aplikacji...
python -m streamlit run app.py
pause