import streamlit as st
import requests

# Konfigurasi Halaman Khusus Vynnra
st.set_page_config(page_title="Vynnra v3.0 | The Ultimate Architect", layout="wide")
st.title("✨ Vynnra: AI Web Architect")

# Konfigurasi API
auth_token = st.secrets.get("OPENROUTER_API_KEY") 
base_url = "https://openrouter.ai/api"
model_name = "anthropic/claude-3.5-sonnet"

# Prompt Arsitek (Pusat Logika)
VYNNRA_PRO_PROMPT = """
Kamu adalah Vynnra v3.0, AI Web Architect.
Tugas: Membangun proyek Next.js 14 (App Router) menggunakan TypeScript dan Tailwind CSS.
Perintah:
1. Berikan struktur folder proyek terlebih dahulu.
2. Berikan isi file per file (Next.js, Tailwind, Components).
3. Gunakan ShadcnUI untuk komponen.
4. Kamu harus selalu mengingat konteks file sebelumnya jika user meminta revisi.
"""

# Inisialisasi Memori Vynnra
if "vynnra_history" not in st.session_state: st.session_state.vynnra_history = []
if "current_code" not in st.session_state: st.session_state.current_code = ""

# Layout: Chat di kiri, Preview di kanan
col1, col2 = st.columns([1, 1])

with col1:
    chat_container = st.container(height=600)
    for msg in st.session_state.vynnra_history:
        with chat_container.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("Vynnra, bangunkan website..."):
        st.session_state.vynnra_history.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"): st.markdown(prompt)
        
        with chat_container.chat_message("assistant"):
            with st.status("Vynnra sedang mendesain arsitektur...", expanded=True):
                payload = {
                    "model": model_name,
                    "messages": [{"role": "system", "content": VYNNRA_PRO_PROMPT}] + st.session_state.vynnra_history
                }
                res = requests.post(
                    f"{base_url}/v1/chat/completions", 
                    json=payload, 
                    headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
                ).json()
                
                answer = res['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.vynnra_history.append({"role": "assistant", "content": answer})
                st.session_state.current_code = answer

with col2:
    st.subheader("💻 Source & Preview")
    tab_code, tab_preview = st.tabs(["Kode (.tsx)", "Live Preview"])
    with tab_code:
        st.code(st.session_state.current_code, language="typescript")
    with tab_preview:
        st.info("Render komponen Next.js/Tailwind...")
        st.components.v1.html(f"""
            <script src="https://cdn.tailwindcss.com"></script>
            <div class="p-4 bg-white min-h-screen text-black">{st.session_state.current_code}</div>
        """, height=600, scrolling=True)
