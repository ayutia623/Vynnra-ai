import streamlit as st
import requests

# Konfigurasi Halaman
st.set_page_config(page_title="Vynnra v4.0 | Architect", layout="wide")
st.title("✨ Vynnra: AI Web Architect")

# Mengambil konfigurasi dari Streamlit Secrets (sesuai setting.json kamu)
auth_token = st.secrets.get("ANTHROPIC_AUTH_TOKEN")
base_url = st.secrets.get("ANTHROPIC_BASE_URL")
model_name = st.secrets.get("ANTHROPIC_MODEL")

# System Prompt Vynnra
VYNNRA_SYSTEM = "Kamu adalah Vynnra, AI Web Architect. Berikan kode Next.js 14 yang estetik. Gunakan format Markdown."

if "history" not in st.session_state: st.session_state.history = []

col1, col2 = st.columns([1, 1])

with col1:
    chat_container = st.container(height=500)
    for msg in st.session_state.history:
        with chat_container.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("Vynnra, bangunkan website..."):
        st.session_state.history.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"): st.markdown(prompt)
        
        with chat_container.chat_message("assistant"):
            # Menggunakan struktur request sesuai standar Anthropic (tokies.lol)
            headers = {
                "x-api-key": auth_token,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "max_tokens": 4096,
                "system": VYNNRA_SYSTEM,
                "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.history]
            }
            
            response = requests.post(f"{base_url}/v1/messages", json=payload, headers=headers)
            
            if response.status_code == 200:
                answer = response.json()['content'][0]['text']
                st.markdown(answer)
                st.session_state.history.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Error dari Tokies/Anthropic: {response.text}")

with col2:
    st.subheader("💻 Preview")
    last_code = next((m["content"] for m in reversed(st.session_state.history) if m["role"] == "assistant"), "")
    st.components.v1.html(f"""
        <script src="https://cdn.tailwindcss.com"></script>
        <div class="p-4 bg-white text-black">{last_code}</div>
    """, height=600, scrolling=True)
