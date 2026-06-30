"""Test ma'lumotlar: xizmatlar + ish vaqti.

Ishga tushirish: python scripts/seed.py
Qayta ishga tushirilsa — eski test xizmatlarini tozalab, qaytadan yozadi.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.database.client import get_supabase

sb = get_supabase()

# --- Xizmatlar (test) ---
SERVICES = [
    {"name": "Soch olish", "price": 50000, "duration": 40, "sort_order": 1},
    {"name": "Soqol olish", "price": 30000, "duration": 20, "sort_order": 2},
    {"name": "Soch + soqol", "price": 70000, "duration": 60, "sort_order": 3},
    {"name": "Bolalar sochi", "price": 40000, "duration": 30, "sort_order": 4},
]

# Eski xizmatlarni tozalaymiz (faqat test uchun)
sb.table("services").delete().neq("id", 0).execute()
sb.table("services").insert(SERVICES).execute()
print(f"Xizmatlar yozildi: {len(SERVICES)} ta")

# --- Ish vaqti (test): Dushanba–Shanba 09:00–20:00, Yakshanba yopiq ---
HOURS = []
for wd in range(7):
    if wd == 6:  # Yakshanba
        HOURS.append({"weekday": wd, "is_open": False, "open_time": None, "close_time": None})
    else:
        HOURS.append({"weekday": wd, "is_open": True, "open_time": "09:00", "close_time": "20:00"})

sb.table("working_hours").upsert(HOURS).execute()
print(f"Ish vaqti yozildi: 7 kun (Yakshanba yopiq)")

print("Seed tugadi.")
