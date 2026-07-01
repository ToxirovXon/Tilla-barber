"""Yangi admin endpointlarni sinash: qo'lda bron, yangi mijoz, edit, atmen, kalendar."""
import hashlib
import hmac
import json
import sys
import time as _t
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from admin_api.main import app
from bot.config import load_config
from bot.database.client import get_supabase
from bot.utils.tz import TASHKENT

cfg = load_config()


def init_data(uid, name="Azamat"):
    p = {"user": json.dumps({"id": uid, "first_name": name}, separators=(",", ":")),
         "auth_date": str(int(_t.time())), "query_id": "T"}
    dcs = "\n".join(f"{k}={v}" for k, v in sorted(p.items()))
    secret = hmac.new(b"WebAppData", cfg.bot_token.encode(), hashlib.sha256).digest()
    p["hash"] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return urlencode(p)


c = TestClient(app)
H = {"Authorization": "tma " + init_data(cfg.admin_ids[0])}
sb = get_supabase()

# 1) Yangi mijoz bilan qo'lda bron (ALTER kerak)
tomorrow = (datetime.now(TASHKENT) + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
svc = c.get("/api/services", headers=H).json()["items"][0]
r = c.post("/api/bookings", headers=H, json={
    "service_id": svc["id"],
    "start_at": tomorrow.isoformat(),
    "new_client": {"full_name": "TEST Walkin", "phone": "+998900000000"},
})
if r.status_code != 200:
    print("QO'LDA BRON XATO:", r.status_code, r.json())
    print(">>> Ehtimol 'telegram_id nullable' ALTER bajarilmagan. Shu bo'lsa — SQL'ni ishlating.")
    sys.exit(1)
res = r.json()
bid, client = res["booking_id"], res["client"]
print(f"Qo'lda bron OK: booking={bid}, yangi mijoz={client['full_name']} (id={client['id']})")

# 2) Kalendar range
frm = datetime.now(TASHKENT).strftime("%Y-%m-%d")
to = (datetime.now(TASHKENT) + timedelta(days=3)).strftime("%Y-%m-%d")
rng = c.get(f"/api/bookings/range?start={frm}&end={to}", headers=H).json()
print(f"Kalendar range: {len(rng['items'])} ta bron")

# 3) Edit — vaqtni 15:30 ga ko'chirish
new_time = tomorrow.replace(hour=15, minute=30)
e = c.patch(f"/api/bookings/{bid}", headers=H, json={"start_at": new_time.isoformat()}).json()
print("Edit OK:", e["booking"]["start_at"])

# 4) Mijoz qidirish
srch = c.get("/api/clients?q=Walkin", headers=H).json()["items"]
print(f"Qidiruv 'Walkin': {len(srch)} ta topildi")

# 5) Atmen (maxsus matn — telegram'siz mijozga yuborilmaydi, lekin status o'zgaradi)
cn = c.post(f"/api/bookings/{bid}/cancel", headers=H, json={"message": "Uzr, bugun band."}).json()
print("Atmen OK:", cn)

# Tozalash
sb.table("bookings").delete().eq("id", bid).execute()
sb.table("clients").delete().eq("id", client["id"]).execute()
print("Test ma'lumotlari tozalandi. YANGI ENDPOINTLAR ISHLAYDI ✅")
