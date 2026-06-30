"""Brauzerda sinash uchun imzolangan dev initData yaratib, admin_web/.env.local ga yozadi.

Eslatma: bu FAQAT lokal dev uchun. .env.local git'ga tushmaydi.
"""
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bot.config import load_config

config = load_config()
token = config.bot_token
admin_id = config.admin_ids[0]

params = {
    "user": json.dumps({"id": admin_id, "first_name": "Azamat", "username": "azamat"}, separators=(",", ":")),
    "auth_date": str(int(time.time())),
    "query_id": "DEV",
}
dcs = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
params["hash"] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
init_data = urlencode(params)

env_path = ROOT / "admin_web" / ".env.local"
env_path.write_text(
    f"VITE_API_URL=http://localhost:8000\nVITE_DEV_INIT_DATA={init_data}\n",
    encoding="utf-8",
)
print("admin_web/.env.local yozildi (dev initData).")
