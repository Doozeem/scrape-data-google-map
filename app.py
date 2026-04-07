import sys
import asyncio
import urllib.parse

# FIX WINDOWS ASYNCIO FOR PLAYWRIGHT
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import pandas as pd
from Maps_Module import scrape_google_maps

# --- INITIAL CONFIG ---
st.set_page_config(
    page_title="DOOZE PROJECT | COMMAND CENTER", 
    page_icon="🧪", 
    layout="wide"
)

# --- ADVANCED NEON CSS INJECTION ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono:wght@300;500&display=swap');

    /* Background Utama */
    .stApp {
        background-color: #000000;
        color: #39FF14;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 2px solid #39FF14;
    }

    /* Judul Utama Glitch/Neon Effect */
    .title-container {
        border: 2px solid #39FF14;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 0px 20px #39FF14;
        text-align: center;
        margin-bottom: 30px;
        background: rgba(57, 255, 20, 0.05);
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 60px;
        font-weight: 700;
        color: #39FF14;
        letter-spacing: 5px;
        text-shadow: 0px 0px 10px #39FF14, 0px 0px 30px #39FF14;
        margin: 0;
    }

    /* Metric Cards Custom */
    div[data-testid="stMetric"] {
        background: rgba(57, 255, 20, 0.05);
        border: 1px solid #39FF14;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(57, 255, 20, 0.2);
    }
    
    div[data-testid="stMetricValue"] {
        color: #39FF14 !important;
        font-family: 'Orbitron', sans-serif;
    }

    /* Button Styling Neon */
    .stButton>button {
        background-color: transparent;
        color: #39FF14;
        border: 2px solid #39FF14;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        padding: 15px 30px;
        border-radius: 5px;
        transition: all 0.4s ease;
        text-transform: uppercase;
    }

    .stButton>button:hover {
        background-color: #39FF14;
        color: #000;
        box-shadow: 0px 0px 30px #39FF14;
    }

    /* Text Input & Area */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #050505;
        color: #39FF14;
        border: 1px solid #39FF14;
    }

    /* Table Customization */
    .stDataFrame {
        border: 1px solid #39FF14;
        border-radius: 10px;
    }

    /* Progress Bar Green */
    .stProgress > div > div > div > div {
        background-color: #39FF14;
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

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("<h2 style='color: #39FF14; font-family: Orbitron;'>⚙️ SYSTEM_OPS</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    bisnis = st.text_input("📍 TARGET_TYPE", "Restoran")
    lokasi = st.text_input("🌐 SECTOR_ZONE", "Jakarta Selatan")
    limit = st.slider("📊 DATA_DEPTH", 5, 100, 10)
    
    st.markdown("---")
    st.markdown("### 💬 COMMS_TEMPLATE")
    pesan_wa = st.text_area("PESAN PROMOSI", 
        value="Halo [NAMA], kami dari Dooze Project mendeteksi potensi besar pada bisnis Anda...", 
        height=150)
    
    st.markdown("---")
    tombol = st.button("EXECUTE INFILTRATION")

# --- MAIN DASHBOARD ---
st.markdown('<div class="title-container"><h1 class="main-title">DOOZE PROJECT</h1></div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-family: JetBrains Mono; color: #39FF14;'>[ STATUS: SYSTEM READY | ENCRYPTION: ACTIVE ]</p>", unsafe_allow_html=True)

if tombol:
    query = f"{bisnis} di {lokasi}"
    
    # Visual Processing Indicator
    with st.status("📡 Menyambungkan ke Radar Google...", expanded=True) as status:
        st.write("Menginisialisasi Protokol Orion...")
        df = scrape_google_maps(query, limit)
        st.write("Mengekstrak Koordinat dan Intelijen...")
        status.update(label="✅ INFILTRASI BERHASIL", state="complete", expanded=False)

    if not df.empty:
        # Link WA Generator
        df['WhatsApp'] = df.apply(lambda x: format_wa_link(x['Telepon'], x['Nama'], pesan_wa), axis=1)
        
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        email_valid = len(df[df['Email'].str.contains('@', na=False)])
        col1.metric("TARGETS_LOCKED", len(df))
        col2.metric("ELITE_EMAILS", email_valid)
        col3.metric("COMMS_READY", len(df[df['Telepon'] != "N/A"]))

        # Data Display
        st.markdown("### 🗃️ RETRIEVED_INTELLIGENCE")
        st.dataframe(
            df, 
            column_config={
                "WhatsApp": st.column_config.LinkColumn("ACTION", display_text="💬 SEND CHAT"),
                "Website": st.column_config.LinkColumn("WEB_SOURCE")
            }, 
            use_container_width=True,
            hide_index=True
        )
        
        # Charts Area
        st.markdown("---")
        st.markdown("### 📊 ANALYTICS_GRID")
        st.bar_chart(df['Kategori'].value_counts())
        
        # Export Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 DOWNLOAD ENCRYPTED_DATABASE (CSV)", 
            data=csv, 
            file_name=f"DOOZE_{lokasi}.csv", 
            mime='text/csv'
        )
    else:
        st.error("Gagal mendapatkan data. Periksa radar sistem.")

st.markdown("---")
st.markdown("<p style='text-align: center; font-family: JetBrains Mono; color: #1E5E12;'>SYSTEM_DOOZE_v3.5_LOG_04/07/2026</p>", unsafe_allow_html=True)