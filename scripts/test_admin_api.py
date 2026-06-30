"""Admin API'ni sinash: imzolangan initData yasab, endpointlarni tekshirish."""
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from admin_api.main import app
from bot.config import load_config

config = load_config()
TOKEN = config.bot_token
ADMIN_ID = config.admin_ids[0]


def build_init_data(user: dict) -> str:
    params = {
        "user": json.dumps(user, separators=(",", ":")),
        "auth_date": str(int(time.time())),
        "query_id": "TEST",
    }
    dcs = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
    params["hash"] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return urlencode(params)


client = TestClient(app)
admin_init = build_init_data({"id": ADMIN_ID, "first_name": "Azamat"})
H = {"Authorization": f"tma {admin_init}"}

print("health:", client.get("/api/health").json())

# Auth'siz -> 401
r = client.get("/api/me")
print("auth'siz /api/me:", r.status_code, "(401 kutilgan)")

# Admin emas -> 403
bad = build_init_data({"id": 111, "first_name": "Begona"})
r = client.get("/api/me", headers={"Authorization": f"tma {bad}"})
print("begona /api/me:", r.status_code, "(403 kutilgan)")

# Admin -> 200
print("admin /api/me:", client.get("/api/me", headers=H).json())

# Xizmatlar
r = client.get("/api/services", headers=H).json()
print("services:", [s["name"] for s in r["items"]])

# Bugungi bronlar
r = client.get("/api/bookings", headers=H).json()
print("bugungi bronlar:", r["date"], "->", len(r["items"]), "ta")

# Statistika
print("stats(30k):", client.get("/api/stats?days=30", headers=H).json())

# Xizmat CRUD sinovi: qo'shish -> yangilash -> nofaol qilish
created = client.post("/api/services", headers=H, json={"name": "TEST Vosk", "price": 25000, "duration": 15}).json()
print("create:", created["name"], created["price"])
upd = client.patch(f"/api/services/{created['id']}", headers=H, json={"price": 27000}).json()
print("update narx:", upd["price"])
client.delete(f"/api/services/{created['id']}", headers=H)
after = client.get("/api/services", headers=H).json()
test_left = [s for s in after["items"] if s["id"] == created["id"]]
print("delete (nofaol):", "is_active =", test_left[0]["is_active"] if test_left else "?")

# Tozalash uchun test xizmatini butunlay o'chiramiz
from bot.database.client import get_supabase
get_supabase().table("services").delete().eq("id", created["id"]).execute()
print("Test xizmat o'chirildi. ADMIN API ISHLAYDI.")
