import streamlit as st
import requests
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vynnra | AI Web Architect", layout="wide")

# --- 2. API SETUP (From Secrets) ---
auth_token = st.secrets.get("ANTHROPIC_AUTH_TOKEN")
base_url = st.secrets.get("ANTHROPIC_BASE_URL")
model_name = "claude-3-5-sonnet-20240620" # Model terbaik untuk coding Next.js

# --- 3. SYSTEM PROMPT (The "Soul" of Vynnra) ---
VYNNRA_SYSTEM_PROMPT = """
Kamu adalah Vynnra, AI Architect senior yang ahli dalam Next.js 14, TypeScript (TSX), dan Tailwind CSS.
Tugasmu:
1. Membangun komponen web modern, bersih, dan fungsional.
2. Selalu gunakan Tailwind CSS untuk styling.
3. Gunakan Lucide-React untuk ikon.
4. Output kode harus dalam format file .tsx yang valid (Next.js App Router).
5. Jangan berikan penjelasan terlalu panjang, fokuslah pada kualitas kode.
6. Penting: Setiap kode harus self-contained (semua komponen dalam satu file jika memungkinkan).
"""

# --- 4. LAYOUT DESIGN ---
st.title("✨ Vynnra: Next.js Architect")

col_chat, col_preview = st.columns([1, 1])

# Inisialisasi Memori Vynnra
if "vynnra_messages" not in st.session_state:
    st.session_state.vynnra_messages = []
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""

# --- 5. CHAT INTERFACE (Kiri) ---
with col_chat:
    st.subheader("💬 Vynnra Chat")
    chat_container = st.container(height=500)
    
    for message in st.session_state.vynnra_messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Vynnra, bangunkan saya dashboard admin dengan Next.js..."):
        st.session_state.vynnra_messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        with chat_container.chat_message("assistant"):
            with st.spinner("Vynnra sedang merancang arsitektur TSX..."):
                headers = {
                    "x-api-key": auth_token,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                payload = {
                    "model": model_name,
                    "max_tokens": 4096,
                    "system": VYNNRA_SYSTEM_PROMPT,
                    "messages": st.session_state.vynnra_messages
                }
                
                response = requests.post(f"{base_url}/v1/messages", json=payload, headers=headers)
                
                if response.status_code == 200:
                    res_data = response.json()
                    ai_response = res_data['content'][0]['text']
                    st.markdown(ai_response)
                    st.session_state.vynnra_messages.append({"role": "assistant", "content": ai_response})
                    
                    # Simpan kode untuk preview
                    st.session_state.generated_code = ai_response
                else:
                    st.error(f"Error: {response.text}")

# --- 6. PREVIEW & CODE VIEW (Kanan) ---
with col_preview:
    tab_preview, tab_code = st.tabs(["🖼️ Live Preview", "💻 Source Code (.tsx)"])
    
    with tab_code:
        if st.session_state.generated_code:
            st.code(st.session_state.generated_code, language="typescript")
        else:
            st.info("Kode belum di-generate.")

    with tab_preview:
        if st.session_state.generated_code:
            # Simulasi Preview: Karena Next.js butuh bundler, 
            # kita akan merender kode Tailwind/HTML hasil ekstraksi.
            st.info("Render Visual (BETA)")
            # Trik: Ekstrak bagian HTML/Tailwind dari respons Claude untuk ditampilkan di iframe
            st.components.v1.html(
                f"""
                <script src="https://cdn.tailwindcss.com"></script>
                <div class="bg-slate-900 text-white min-h-screen p-4">
                    <p class="text-xs text-slate-500 mb-4">Live Preview dari Vynnra Architect</p>
                    {st.session_state.generated_code.split('```')[1] if '```' in st.session_state.generated_code else 'Generating...'}
                </div>
                """,
                height=600,
                scrolling=True
            )
        else:
            st.write("Menunggu arsitektur dari Vynnra...")
