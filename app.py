import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
import random
import plotly.express as px
from PIL import Image, ImageDraw

# ==========================================
# 1. KONFIGURACJA
# ==========================================
FOLDER_MEMOW = "data/memy"
PLIK_WYNIKOW = "data/wyniki.csv"
PLIK_CECH = "data/cechy_memow.csv"
PLIK_OBIEKTOW = "data/obiekty_memow.csv"

st.set_page_config(page_title="Meme System", layout="wide")

if not os.path.exists(PLIK_WYNIKOW):
    with open(PLIK_WYNIKOW, "w", encoding="utf-8") as f:
        f.write("nazwa_pliku,ocena\n")

# ==========================================
# 2. PAMIĘĆ PODRĘCZNA I BUFOROWANIE
# ==========================================
if 'lista_memow' not in st.session_state:
    st.session_state.lista_memow = [p for p in os.listdir(FOLDER_MEMOW) if
                                    p.lower().endswith(('.jpg', '.png', '.jpeg'))]
    if not st.session_state.lista_memow:
        st.error("Brak memów w folderze!")
        st.stop()

if 'aktualny_mem' not in st.session_state:
    st.session_state.aktualny_mem = random.choice(st.session_state.lista_memow)

if 'bufor_glosow' not in st.session_state:
    st.session_state.bufor_glosow = []


def zapisz_bufor_na_dysk():
    if st.session_state.bufor_glosow:
        with open(PLIK_WYNIKOW, "a", encoding="utf-8") as f:
            f.writelines(st.session_state.bufor_glosow)
        st.session_state.bufor_glosow = []


def glosuj(ocena):
    st.session_state.bufor_glosow.append(f"{st.session_state.aktualny_mem},{ocena}\n")
    if len(st.session_state.bufor_glosow) >= 5:
        zapisz_bufor_na_dysk()
    st.session_state.aktualny_mem = random.choice(st.session_state.lista_memow)


# ==========================================
# 3. INTERFEJS
# ==========================================
st.sidebar.title("Nawigacja")
strona = st.sidebar.radio("Wybierz moduł:",
                          ["👆 Ocenianie (Tinder)", "🤖 Korekta OCR", "👁️ Jak widzi to AI", "📈 Dashboard"])

if strona != "👆 Ocenianie (Tinder)":
    zapisz_bufor_na_dysk()

# --- ZAKŁADKA 1: OCENIANIE ---
if strona == "👆 Ocenianie (Tinder)":
    st.title("🔥 Ocenianie Memów")
    st.write(f"*(Głosy w buforze RAM oczekujące na zapis: {len(st.session_state.bufor_glosow)}/5)*")

    sciezka = os.path.join(FOLDER_MEMOW, st.session_state.aktualny_mem)
    st.image(sciezka, use_container_width=True)

    kol_l, kol_p = st.columns(2)
    with kol_l:
        if st.button("❌ Odrzuć", use_container_width=True):
            glosuj(-1)
            st.rerun()
    with kol_p:
        if st.button("❤️ Lubię", use_container_width=True):
            glosuj(1)
            st.rerun()

# --- ZAKŁADKA 2: OCR ---
elif strona == "🤖 Korekta OCR":
    st.title("Ocena i korekta modelu OCR")
    if os.path.exists(PLIK_CECH):
        df_c = pd.read_csv(PLIK_CECH)

        if 'czy_ma_tekst' in df_c.columns:
            # POPRAWKA: Rozszerzone filtrowanie na wypadek zmiany formatu na ułamek (1.0) lub tekst ("1")
            memy_ocr = df_c[df_c['czy_ma_tekst'].isin([1, 1.0, '1', '1.0'])]

            if memy_ocr.empty:
                st.info(
                    "💡 Nie znaleziono jeszcze żadnych memów z tekstem. Upewnij się, że skrypt OCR zakończył działanie.")
            else:
                # Ograniczenie wyświetlania, by nie zablokować przeglądarki (DOM)
                memy_ocr_limit = memy_ocr.head(20)
                st.write(f"Wyświetlam {len(memy_ocr_limit)} z {len(memy_ocr)} wyników dla wydajności.")

                for index, row in memy_ocr_limit.iterrows():
                    k1, k2 = st.columns([1, 2])
                    with k1:
                        st.image(os.path.join(FOLDER_MEMOW, row['nazwa_pliku']), use_container_width=True)
                    with k2:
                        nowy_t = st.text_input("Tekst:", value=row['wykryty_tekst'], key=f"in_{index}")
                        if st.button("💾 Zapisz poprawkę", key=f"save_{index}"):
                            df_c.at[index, 'wykryty_tekst'] = nowy_t
                            df_c.to_csv(PLIK_CECH, index=False)
                            st.toast("Zapisano!")
                    st.divider()
        else:
            st.warning("Plik z cechami nie posiada jeszcze kolumny z tekstem. Uruchom ekstrakcję OCR.")
    else:
        st.warning("Brak pliku z cechami!")

# --- ZAKŁADKA 3: WIZUALIZACJA AI (YOLO) ---
elif strona == "👁️ Jak widzi to AI":
    st.title("👁️ Detekcja Obiektów na memach")
    st.write("Filtruj i przeglądaj obiekty wykryte przez algorytm YOLO.")

    # Inicjalizacja liczników w pamięci podręcznej (RAM) aplikacji
    if 'ai_index' not in st.session_state:
        st.session_state.ai_index = 0
    if 'ai_tag' not in st.session_state:
        st.session_state.ai_tag = "Wszystkie pliki"

    if os.path.exists(PLIK_OBIEKTOW):
        df_obiekty = pd.read_csv(PLIK_OBIEKTOW)
        dane_z_obiektami = df_obiekty[(df_obiekty['obiekt'] != 'brak') & (df_obiekty['obiekt'] != 'blad')]

        if dane_z_obiektami.empty:
            st.info("AI nie znalazło jeszcze żadnych konkretnych obiektów w Twojej bazie.")
        else:
            lista_tagow = sorted(dane_z_obiektami['obiekt'].unique().tolist())

            # FILTR 1: Wybór kategorii
            wybrany_tag = st.selectbox("🔍 1. Wybierz obiekt, którego szukasz:", ["Wszystkie pliki"] + lista_tagow)

            # Jeśli zmienisz kategorię, program zresetuje licznik do pierwszego zdjęcia
            if wybrany_tag != st.session_state.ai_tag:
                st.session_state.ai_tag = wybrany_tag
                st.session_state.ai_index = 0

            # Pobranie odpowiednich plików
            if wybrany_tag == "Wszystkie pliki":
                dostepne_pliki = df_obiekty['nazwa_pliku'].unique().tolist()
            else:
                dostepne_pliki = dane_z_obiektami[dane_z_obiektami['obiekt'] == wybrany_tag][
                    'nazwa_pliku'].unique().tolist()

            max_index = len(dostepne_pliki) - 1

            # Zabezpieczenie na wypadek wyjścia poza listę
            if st.session_state.ai_index > max_index:
                st.session_state.ai_index = 0

            # INTERFEJS GALERII: Przyciski nawigacyjne
            k_lewa, k_srodek, k_prawa = st.columns([1, 2, 1])

            with k_lewa:
                if st.button("⬅️ Poprzedni", use_container_width=True):
                    st.session_state.ai_index = max(0, st.session_state.ai_index - 1)

            with k_srodek:
                wybrany_mem = dostepne_pliki[st.session_state.ai_index]
                st.markdown(
                    f"<h4 style='text-align: center;'>Plik: {wybrany_mem} ({st.session_state.ai_index + 1} z {len(dostepne_pliki)})</h4>",
                    unsafe_allow_html=True)

            with k_prawa:
                if st.button("Następny ➡️", use_container_width=True):
                    st.session_state.ai_index = min(max_index, st.session_state.ai_index + 1)

            st.divider()

            # RYSOWANIE RAMEK
            sciezka_mema = os.path.join(FOLDER_MEMOW, wybrany_mem)
            dane_mema = df_obiekty[df_obiekty['nazwa_pliku'] == wybrany_mem]

            if os.path.exists(sciezka_mema):
                img = Image.open(sciezka_mema).convert("RGB")
                draw = ImageDraw.Draw(img)

                if not dane_mema.empty and dane_mema.iloc[0]['obiekt'] != "brak" and dane_mema.iloc[0][
                    'obiekt'] != "blad":
                    for _, row in dane_mema.iterrows():
                        x1, y1, x2, y2 = row['x1'], row['y1'], row['x2'], row['y2']
                        etykieta = f"{row['obiekt']} ({int(row['pewnosc'] * 100)}%)"

                        # Rysowanie ramki
                        draw.rectangle([x1, y1, x2, y2], outline="#ff4b4b", width=4)

                    st.image(img, caption=f"Model YOLOv8 - analiza pliku {wybrany_mem}", use_container_width=True)
                    st.dataframe(dane_mema[['obiekt', 'pewnosc']], use_container_width=True)
                else:
                    st.image(img, use_container_width=True)
                    st.info("Model sztucznej inteligencji nie wykrył tu żadnych konkretnych przedmiotów.")
            else:
                st.error("Plik nie istnieje na dysku.")
    else:
        st.warning("Brak pliku obiekty_memow.csv. Skrypt detekcji jeszcze nie przetworzył zdjęć.")

# --- ZAKŁADKA 4: DASHBOARD ---
elif strona == "📈 Dashboard":
    st.title("📊 Twoje Statystyki")
    if os.path.exists(PLIK_CECH) and os.path.exists(PLIK_WYNIKOW):
        df_c = pd.read_csv(PLIK_CECH)
        df_w = pd.read_csv(PLIK_WYNIKOW)

        # POPRAWKA: Obsługa pustego pliku wyników
        if df_w.empty:
            st.info(
                "💡 Brak danych do wyświetlenia. Przejdź do zakładki 'Ocenianie' i zagłosuj na przynajmniej 5 memów, aby zobaczyć pierwsze statystyki!")
        elif 'czy_ma_tekst' not in df_c.columns:
            st.warning("Brak pełnych danych w pliku cech.")
        else:
            df_full = pd.merge(df_w, df_c, on='nazwa_pliku')
            if not df_full.empty:
                df_full['Ocena'] = df_full['ocena'].map({1: 'Lubię ❤️', -1: 'Odrzucone ❌'})
                # Zabezpieczenie na ułamki w kolumnie "czy_ma_tekst"
                df_full['Typ'] = df_full['czy_ma_tekst'].map(
                    {1: 'Z tekstem', 0: 'Sam obraz', 1.0: 'Z tekstem', 0.0: 'Sam obraz'})
                df_full['Typ'] = df_full['Typ'].fillna('Nieznany')

                fig = px.histogram(df_full, x="Typ", color="Ocena", barmode="group",
                                   color_discrete_map={'Lubię ❤️': '#00cc96', 'Odrzucone ❌': '#ff4b4b'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nie ma wspólnych punktów między ocenionymi memami a bazą danych.")
    else:
        st.info("Brak plików z danymi.")

# ==========================================
# 4. OBSŁUGA KLAWIATURY I GESTÓW
# ==========================================
if strona == "👆 Ocenianie (Tinder)":
    components.html(
        """
    <script>
    const parentWindow = window.parent;
    const doc = parentWindow.document;

    if (!parentWindow.listenerAdded) {
        parentWindow.listenerAdded = true;

        doc.addEventListener('keydown', function(e) {
            if (doc.activeElement.tagName === 'INPUT' || doc.activeElement.tagName === 'TEXTAREA') return;
            if (e.key === 'ArrowLeft') {
                const b = Array.from(doc.querySelectorAll('button')).find(btn => btn.innerText.includes('Odrzuć'));
                if(b) b.click();
            } else if (e.key === 'ArrowRight') {
                const b = Array.from(doc.querySelectorAll('button')).find(btn => btn.innerText.includes('Lubię'));
                if(b) b.click();
            }
        });

        let touchstartX = 0, touchendX = 0, touchstartY = 0, touchendY = 0;
        doc.addEventListener('touchstart', e => { touchstartX = e.changedTouches[0].screenX; touchstartY = e.changedTouches[0].screenY; }, {passive: true});
        doc.addEventListener('touchend', e => { touchendX = e.changedTouches[0].screenX; touchendY = e.changedTouches[0].screenY; handleGesture(); }, {passive: true});

        function handleGesture() {
            const deltaX = touchendX - touchstartX;
            const deltaY = touchendY - touchstartY;
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                if (doc.activeElement.tagName === 'INPUT' || doc.activeElement.tagName === 'TEXTAREA') return;
                if (deltaX < 0) {
                    const b = Array.from(doc.querySelectorAll('button')).find(btn => btn.innerText.includes('Odrzuć'));
                    if(b) b.click();
                } else if (deltaX > 0) {
                    const b = Array.from(doc.querySelectorAll('button')).find(btn => btn.innerText.includes('Lubię'));
                    if(b) b.click();
                }
            }
        }
    }
    </script>
        """, height=0, width=0)