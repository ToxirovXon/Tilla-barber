"""Ish vaqti jadvali bilan ishlash."""
import asyncio

from bot.database.client import get_supabase

TABLE = "working_hours"


async def list_all() -> list[dict]:
    """Barcha 7 kun (admin sozlamasi uchun)."""
    def _query():
        res = get_supabase().table(TABLE).select("*").order("weekday").execute()
        return res.data

    return await asyncio.to_thread(_query)


async def upsert_days(rows: list[dict]) -> None:
    """Kunlarni saqlash (weekday PK bo'yicha upsert)."""
    def _query():
        get_supabase().table(TABLE).upsert(rows).execute()

    return await asyncio.to_thread(_query)


async def get_day(weekday: int) -> dict | None:
    """weekday: 0=Dushanba ... 6=Yakshanba. Topilmasa None (yopiq deb hisoblanadi)."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*")
            .eq("weekday", weekday)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    return await asyncio.to_thread(_query)
