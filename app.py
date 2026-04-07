import sys
import os
import subprocess
import urllib.parse
import asyncio

# ==========================================
# PROTOKOL INITIALISASI ENGINE (CLOUD & LOKAL)
# ==========================================
def install_playwright_binaries():
    try:
        # Cek apakah folder browser sudah ada di server Cloud
        if not os.path.exists("/home/appuser/.cache/ms-playwright"):
            # Hanya instal browser Chromium (TANPA install-deps agar tidak kena blokir server)
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    except Exception:
        pass 

# Fix untuk Windows (Agar lancar di PC Lokal)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import pandas as pd
from Maps_Module import scrape_google_maps

# Jalankan pengecekan engine sebelum UI dimuat
install_playwright_binaries()

# ==========================================
# KONFIGURASI TAMPILAN NEON ELITE
# ==========================================
st.set_page_config(page_title="DOOZE PROJECT | COMMAND CENTER", page_icon="🧪", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono:wght@300;500&display=swap');

    .stApp { background-color: #000000; color: #39FF14; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 2px solid #39FF14; }

    .title-container {
        border: 2px solid #39FF14; padding: 20px; border-radius: 15px;
        box-shadow: 0px 0px 20px #39FF14; text-align: center; margin-bottom: 30px;
        background: rgba(57, 255, 20, 0.05);
    }
    .main-title {
        font-family: 'Orbitron', sans-serif; font-size: 60px; color: #39FF14;
        letter-spacing: 5px; text-shadow: 0px 0px 10px #39FF14; margin: 0;
    }
    div[data-testid="stMetric"] {
        background: rgba(57, 255, 20, 0.05); border: 1px solid #39FF14;
        padding: 15px; border-radius: 10px;
    }
    div[data-testid="stMetricValue"] { color: #39FF14 !important; font-family: 'Orbitron', sans-serif; }
    .stButton>button {
        background-color: transparent; color: #39FF14; border: 2px solid #39FF14;
        font-family: 'Orbitron', sans-serif; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #39FF14; color: #000; box-shadow: 0px 0px 30px #39FF14; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #050505; color: #39FF14; border: 1px solid #39FF14;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def format_wa_link(phone, business_name, template_message):
    if not phone or phone == "N/A": return None
    clean_phone = "".join(filter(str.isdigit, phone))
    if clean_phone.startswith("0"): clean_phone = "62" + clean_phone[1:]
    encoded_msg = urllib.parse.quote(template_message.replace("[NAMA]", business_name))
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.markdown("<h2 style='color: #39FF14; font-family: Orbitron;'>⚙️ SYSTEM_OPS</h2>", unsafe_allow_html=True)
    bisnis = st.text_input("📍 TARGET_TYPE", "Restoran")
    lokasi = st.text_input("🌐 SECTOR_ZONE", "Jakarta Selatan")
    limit = st.slider("📊 DATA_DEPTH", 5, 100, 10)
    st.markdown("### 💬 COMMS_TEMPLATE")
    pesan_wa = st.text_area("PESAN PROMOSI", 
        value="Halo [NAMA], kami dari Dooze Project mendeteksi potensi besar pada bisnis Anda...", height=150)
    tombol = st.button("EXECUTE INFILTRATION")

# --- MAIN DASHBOARD ---
st.markdown('<div class="title-container"><h1 class="main-title">DOOZE PROJECT</h1></div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-family: JetBrains Mono; color: #39FF14;'>[ STATUS: SYSTEM READY | CLOUD ENGINE ACTIVE ]</p>", unsafe_allow_html=True)

if tombol:
    query = f"{bisnis} di {lokasi}"
    with st.status("📡 Infiltrasi Radar Google...", expanded=True) as status:
        st.write("Mengaktifkan Orion Engine...")
        df = scrape_google_maps(query, limit)
        status.update(label="✅ DATA DIAMANKAN", state="complete", expanded=False)

    if not df.empty:
        df['WhatsApp'] = df.apply(lambda x: format_wa_link(x['Telepon'], x['Nama'], pesan_wa), axis=1)
        
        col1, col2, col3 = st.columns(3)
        email_valid = len(df[df['Email'].str.contains('@', na=False)])
        col1.metric("TARGETS_LOCKED", len(df))
        col2.metric("ELITE_EMAILS", email_valid)
        col3.metric("COMMS_READY", len(df[df['Telepon'] != "N/A"]))

        st.dataframe(
            df, 
            column_config={
                "WhatsApp": st.column_config.LinkColumn("ACTION", display_text="💬 SEND WA"),
                "Website": st.column_config.LinkColumn("SOURCE")
            }, 
            use_container_width=True, hide_index=True
        )
        
        st.bar_chart(df['Kategori'].value_counts())
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 DOWNLOAD DATABASE (CSV)", data=csv, file_name=f"DOOZE_{lokasi}.csv", mime='text/csv')
    else:
        st.error("Gagal mendapatkan data. Target mungkin tidak ada atau koneksi terputus.")

st.markdown("---")
st.markdown("<p style='text-align: center; font-family: JetBrains Mono; color: #1E5E12;'>SYSTEM_DOOZE_v3.5_LOG_04/07/2026</p>", unsafe_allow_html=True)
