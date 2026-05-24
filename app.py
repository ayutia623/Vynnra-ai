import streamlit as st
import requests
import time

st.set_page_config(page_title="Vynnra v4.0 | Animated Architect", layout="wide")

# --- ANIMATION & STYLING ---
st.markdown("""
<style>
    .thinking { font-style: italic; color: #888; display: flex; align-items: center; gap: 10px; }
    .thinking::after { content: "..."; animation: dots 1.5s infinite; }
    @keyframes dots { 0% { content: "."; } 50% { content: ".."; } 100% { content: "..."; } }
    .chat-bubble { padding: 15px; border-radius: 15px; margin: 10px 0; background: #262730; }
</style>
""", unsafe_allow_html=True)

# Konfigurasi API
auth_token = st.secrets.get("OPENROUTER_API_KEY") 
base_url = "https://openrouter.ai/api"
model_name = "anthropic/claude-3.5-sonnet"

VYNNRA_SYSTEM = "Kamu adalah Vynnra, AI Web Architect. Berikan kode Next.js 14 yang estetik. Gunakan format Markdown."

if "history" not in st.session_state: st.session_state.history = []

col1, col2 = st.columns([1, 1])

with col1:
    st.title("✨ Vynnra v4.0")
    chat_container = st.container(height=500)
    
    # Render History
    for msg in st.session_state.history:
        with chat_container.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("Vynnra, bangunkan website..."):
        st.session_state.history.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"): st.markdown(prompt)
        
        # Animasi Thinking
        with chat_container.chat_message("assistant"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown('<div class="thinking">Vynnra sedang berpikir</div>', unsafe_allow_html=True)
            
            payload = {"model": model_name, "messages": [{"role": "system", "content": VYNNRA_SYSTEM}] + st.session_state.history}
            response = requests.post(f"{base_url}/v1/chat/completions", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
            
            if response.status_code == 200:
                answer = response.json()['choices'][0]['message']['content']
                thinking_placeholder.empty() # Hapus animasi thinking
                st.markdown(answer)
                st.session_state.history.append({"role": "assistant", "content": answer})
            else:
                thinking_placeholder.empty()
                st.error("Error: Infrastruktur sedang sibuk.")

with col2:
    st.subheader("👁️ Live Preview")
    # Logika untuk menampilkan kode terakhir dari history
    last_code = next((m["content"] for m in reversed(st.session_state.history) if m["role"] == "assistant"), "")
    
    tab1, tab2 = st.tabs(["💻 Code", "🎨 Visual"])
    with tab1:
        st.code(last_code, language="typescript")
    with tab2:
        st.components.v1.html(f"""
            <script src="https://cdn.tailwindcss.com"></script>
            <div class="bg-white text-black p-5">{last_code}</div>
        """, height=600, scrolling=True)
