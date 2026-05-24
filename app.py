import streamlit as st
import requests

st.set_page_config(page_title="Vynnra v5.0 | Web Architect", layout="wide")

# Konfigurasi dari Secrets
auth_token = st.secrets.get("ANTHROPIC_AUTH_TOKEN")
base_url = st.secrets.get("ANTHROPIC_BASE_URL")
model_name = st.secrets.get("ANTHROPIC_MODEL")

# SYSTEM PROMPT V5.0 (Architect Logic)
VYNNRA_SYSTEM = """
Kamu adalah Vynnra v5.0, Web Architect sekelas Replit Agent.
Tugas: Membangun aplikasi Next.js/React.
Aturan:
1. Output WAJIB dipisah: Bagian penjelasan, lalu blok kode ```tsx ... ```.
2. Gunakan Tailwind CSS CDN untuk preview agar visual langsung muncul.
3. Struktur file harus modular (Components, Layout, Page).
4. Berpikir logis (Chain of Thought): Tulis rencana arsitektur sebelum coding.
"""

if "messages" not in st.session_state: st.session_state.messages = []

# Layout Utama
col_chat, col_prev = st.columns([1, 1])

with col_chat:
    st.title("✨ Vynnra v5.0")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("Vynnra, buatkan dashboard..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.status("Vynnra sedang merancang arsitektur...", expanded=True):
                payload = {
                    "model": model_name,
                    "max_tokens": 4096,
                    "system": VYNNRA_SYSTEM,
                    "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                }
                res = requests.post(
                    f"{base_url}/v1/messages", 
                    json=payload, 
                    headers={"x-api-key": auth_token, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
                ).json()
                
                answer = res['content'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

with col_prev:
    st.subheader("🛠️ Live Build Preview")
    # Mencari kode terakhir di history
    last_msg = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"), "")
    
    # Ekstraksi kode dari blok ```tsx
    code_content = ""
    if "```tsx" in last_msg:
        code_content = last_msg.split("```tsx")[1].split("```")[0]
    elif "```" in last_msg:
        code_content = last_msg.split("```")[1].split("```")[0]

    if code_content:
        st.components.v1.html(f"""
            <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
            <script src="[https://unpkg.com/lucide@latest](https://unpkg.com/lucide@latest)"></script>
            <div id="root">{code_content}</div>
        """, height=700, scrolling=True)
    else:
        st.info("Vynnra sedang merancang arsitektur... tunggu hasil kodenya.")
