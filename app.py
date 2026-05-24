import streamlit as st

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Vynnra Master Hub", layout="wide")

# Sidebar Navigasi
with st.sidebar:
    st.title("🛰️ Command Center")
    app_mode = st.radio("Pilih Modul:", ["📊 Crypto Analytics", "✨ Vynnra Web Architect", "💬 AI Chat"])
    st.divider()

# Logika Routing Aplikasi
if app_mode == "📊 Crypto Analytics":
    # (Di sini nanti kita masukkan kode Trading Bot versi lengkap)
    st.header("📊 Crypto Analytics")
    st.write("Modul analisis pasar sedang aktif...")

elif app_mode == "✨ Vynnra Web Architect":
    # (Di sini nanti kita masukkan logika Vynnra)
    st.header("✨ Vynnra: AI Web Architect")
    st.write("Vynnra siap membangun arsitektur web-mu...")

elif app_mode == "💬 AI Chat":
    # (Di sini nanti kita masukkan logika Chat AI Claude)
    st.header("💬 AI Crypto Assistant")
    st.write("Diskusi strategi dengan Claude...")
