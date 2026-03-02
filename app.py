import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
import random
import plotly.express as px

# ==========================================
# 1. KONFIGURACJA
# ==========================================
FOLDER_MEMOW = "memy"
PLIK_WYNIKOW = "wyniki.csv"
PLIK_CECH = "cechy_memow.csv"

st.set_page_config(page_title="Meme System", layout="wide")

if not os.path.exists(PLIK_WYNIKOW):
    with open(PLIK_WYNIKOW, "w", encoding="utf-8") as f:
        f.write("nazwa_pliku,ocena\n")

# ==========================================
# 2. PAMIĘĆ PODRĘCZNA I BUFOROWANIE (MAX PRĘDKOŚĆ)
# ==========================================
if 'lista_memow' not in st.session_state:
    st.session_state.lista_memow = [p for p in os.listdir(FOLDER_MEMOW) if p.lower().endswith(('.jpg', '.png'))]
    if not st.session_state.lista_memow:
        st.error("Brak memów w folderze!")
        st.stop()

if 'aktualny_mem' not in st.session_state:
    st.session_state.aktualny_mem = random.choice(st.session_state.lista_memow)

# INŻYNIERSKI BUFOR: Zbieramy głosy w RAMie!
if 'bufor_glosow' not in st.session_state:
    st.session_state.bufor_glosow = []


def zapisz_bufor_na_dysk():
    if st.session_state.bufor_glosow:
        with open(PLIK_WYNIKOW, "a", encoding="utf-8") as f:
            f.writelines(st.session_state.bufor_glosow)
        st.session_state.bufor_glosow = []  # Czyścimy bufor po zapisie


def glosuj(ocena):
    # Dopisujemy wynik do szybkiego bufora w RAM, a nie na wolny dysk!
    st.session_state.bufor_glosow.append(f"{st.session_state.aktualny_mem},{ocena}\n")

    # Zapisz na dysk tylko, gdy zbierze się 5 głosów (tzw. Batching)
    if len(st.session_state.bufor_glosow) >= 5:
        zapisz_bufor_na_dysk()

    st.session_state.aktualny_mem = random.choice(st.session_state.lista_memow)


# ==========================================
# 3. INTERFEJS (MENU BOCZNE ZAMIAST ZAKŁADEK)
# ==========================================
st.sidebar.title("Nawigacja")
# Menu boczne zapobiega uruchamianiu ciężkiego kodu z innych stron
strona = st.sidebar.radio("Wybierz moduł:", ["👆 Ocenianie (Tinder)", "🤖 Korekta OCR", "📈 Dashboard"])

# Zapisz bufor za każdym razem, gdy użytkownik wychodzi z zakładki oceniania
if strona != "👆 Ocenianie (Tinder)":
    zapisz_bufor_na_dysk()

if strona == "👆 Ocenianie (Tinder)":
    st.title("🔥 Ocenianie Memów")
    st.write(f"*(Głosy w buforze RAM oczekujące na zapis: {len(st.session_state.bufor_glosow)}/5)*")

    sciezka = os.path.join(FOLDER_MEMOW, st.session_state.aktualny_mem)
    st.image(sciezka, width="stretch")

    kol_l, kol_p = st.columns(2)
    with kol_l:
        if st.button("❌ Odrzuć", width="stretch"):
            glosuj(-1)
            st.rerun()
    with kol_p:
        if st.button("❤️ Lubię", width="stretch"):
            glosuj(1)
            st.rerun()

elif strona == "🤖 Korekta OCR":
    st.title("Ocena i korekta modelu OCR")
    if os.path.exists(PLIK_CECH):
        df_c = pd.read_csv(PLIK_CECH)
        if 'czy_ma_tekst' in df_c.columns:
            memy_ocr = df_c[df_c['czy_ma_tekst'] == 1]
            for index, row in memy_ocr.iterrows():
                k1, k2 = st.columns([1, 2])
                with k1:
                    st.image(os.path.join(FOLDER_MEMOW, row['nazwa_pliku']), width="stretch")
                with k2:
                    nowy_t = st.text_input("Tekst:", value=row['wykryty_tekst'], key=f"in_{index}")
                    if st.button("💾 Zapisz poprawkę", key=f"save_{index}"):
                        df_c.at[index, 'wykryty_tekst'] = nowy_t
                        df_c.to_csv(PLIK_CECH, index=False)
                        st.toast("Zapisano!")
                st.divider()
    else:
        st.warning("Brak pliku z cechami!")

elif strona == "📈 Dashboard":
    st.title("📊 Twoje Statystyki")
    if os.path.exists(PLIK_CECH) and os.path.exists(PLIK_WYNIKOW):
        df_c = pd.read_csv(PLIK_CECH)
        df_w = pd.read_csv(PLIK_WYNIKOW)
        if 'czy_ma_tekst' in df_c.columns and not df_w.empty:
            df_full = pd.merge(df_w, df_c, on='nazwa_pliku')
            if not df_full.empty:
                df_full['Ocena'] = df_full['ocena'].map({1: 'Lubię ❤️', -1: 'Odrzucone ❌'})
                df_full['Typ'] = df_full['czy_ma_tekst'].map({1: 'Z tekstem', 0: 'Sam obraz'})
                fig = px.histogram(df_full, x="Typ", color="Ocena", barmode="group",
                                   color_discrete_map={'Lubię ❤️': '#00cc96', 'Odrzucone ❌': '#ff4b4b'})
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Brak wspólnych danych.")
    else:
        st.info("Brak plików z danymi.")

# ==========================================
# 4. OBSŁUGA KLAWIATURY I GESTÓW DOTYKOWYCH (JS)
# ==========================================
if strona == "👆 Ocenianie (Tinder)":
    components.html(
        """
    <script>
    const parentWindow = window.parent;
    const doc = parentWindow.document;

    if (!parentWindow.listenerAdded) {
        parentWindow.listenerAdded = true;

        // --- 1. OBSŁUGA KLAWIATURY (PC) ---
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

        // --- 2. OBSŁUGA SWIPE NA EKRANIE DOTYKOWYM (TELEFON) ---
        let touchstartX = 0;
        let touchendX = 0;
        let touchstartY = 0;
        let touchendY = 0;

        doc.addEventListener('touchstart', function(event) {
            touchstartX = event.changedTouches[0].screenX;
            touchstartY = event.changedTouches[0].screenY;
        }, {passive: true});

        doc.addEventListener('touchend', function(event) {
            touchendX = event.changedTouches[0].screenX;
            touchendY = event.changedTouches[0].screenY;
            handleGesture();
        }, {passive: true});

        function handleGesture() {
            const deltaX = touchendX - touchstartX;
            const deltaY = touchendY - touchstartY;

            // Sprawdzamy, czy to poziomy swipe, a nie przewijanie strony w dół
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                if (doc.activeElement.tagName === 'INPUT' || doc.activeElement.tagName === 'TEXTAREA') return;

                if (deltaX < 0) {
                    // Swipe w lewo
                    const b = Array.from(doc.querySelectorAll('button')).find(btn => btn.innerText.includes('Odrzuć'));
                    if(b) b.click();
                } else if (deltaX > 0) {
                    // Swipe w prawo
                    const b = Array.from(doc.querySelectorAll('button')).find(btn => btn.innerText.includes('Lubię'));
                    if(b) b.click();
                }
            }
        }
    }
    </script>
        """, height=0, width=0)