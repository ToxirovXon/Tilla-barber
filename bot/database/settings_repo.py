"""Sozlamalar (avtomatik xabarlar). key-value (jsonb) jadval.

Placeholderlar: {name}=ism, {time}=vaqt, {service}=xizmat, {percent}=foiz.
"""
import asyncio

from bot.database.client import get_supabase

TABLE = "settings"

DEFAULTS = {
    "reminder": {
        "enabled": True,
        "hours": 2,
        "text": "🔔 Eslatma! Bugun soat {time} da navbatingiz bor.\n✂️ {service}\nKutib qolamiz! 💈",
    },
    "retention": {
        "enabled": False,
        "days": 35,
        "text": "Assalomu alaykum, {name}! 😊 Ancha ko'rishmadik. Soch olish vaqti keldimi? Bron qiling — sizni kutamiz 💈",
    },
    "birthday": {
        "enabled": False,
        "percent": 20,
        "text": "🎂 {name}, tug'ilgan kuningiz muborak! Bugun barcha xizmatlarga {percent}% chegirma sizga. Kutamiz! 💈",
    },
}


async def get_all() -> dict:
    """Saqlangan qiymatlar + defaultlar (birlashtirilgan)."""
    def _query():
        rows = get_supabase().table(TABLE).select("*").execute().data
        return {r["key"]: r["value"] for r in rows}

    stored = await asyncio.to_thread(_query)
    merged = {}
    for key, default in DEFAULTS.items():
        merged[key] = {**default, **(stored.get(key) or {})}
    return merged


async def save(items: dict) -> None:
    """items: {key: {..config..}}."""
    def _query():
        rows = [{"key": k, "value": v} for k, v in items.items()]
        get_supabase().table(TABLE).upsert(rows).execute()

    return await asyncio.to_thread(_query)
