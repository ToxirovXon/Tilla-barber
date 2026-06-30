"""Ish vaqti jadvali bilan ishlash."""
import asyncio

from bot.database.client import get_supabase

TABLE = "working_hours"


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
