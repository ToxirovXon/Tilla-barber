"""Bazadagi mijozlarni ko'rsatish (tekshiruv uchun)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.database.client import get_supabase

res = get_supabase().table("clients").select("*").order("created_at").execute()
print("Bazadagi mijozlar soni:", len(res.data))
for c in res.data:
    print(
        f"  #{c['id']} | {c['full_name']} | {c['phone']} | "
        f"tug: {c['birthday']} | tg: {c['telegram_id']}"
    )
