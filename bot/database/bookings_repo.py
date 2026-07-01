"""Bronlar jadvali bilan ishlash."""
import asyncio
from datetime import datetime

from bot.database.client import get_supabase

TABLE = "bookings"

# Vaqtni band qiladigan statuslar (bo'sh slot hisoblashda inobatga olinadi)
ACTIVE_STATUSES = ("pending", "confirmed")


async def get_bookings_for_day(day_start: datetime, day_end: datetime) -> list[dict]:
    """Berilgan kun oralig'idagi faol bronlar (band vaqtlarni aniqlash uchun)."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("start_at, end_at, status")
            .gte("start_at", day_start.isoformat())
            .lt("start_at", day_end.isoformat())
            .in_("status", list(ACTIVE_STATUSES))
            .execute()
        )
        return res.data

    return await asyncio.to_thread(_query)


async def create_booking(
    client_id: int,
    service_id: int,
    start_at: datetime,
    end_at: datetime,
    price: int,
    source: str = "bot",
) -> dict:
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .insert(
                {
                    "client_id": client_id,
                    "service_id": service_id,
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                    "price": price,
                    "source": source,
                    "status": "pending",
                }
            )
            .execute()
        )
        return res.data[0]

    return await asyncio.to_thread(_query)


async def list_bookings(start: datetime, end: datetime) -> list[dict]:
    """Berilgan oraliqdagi barcha bronlar (admin uchun, hamma status)."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*, clients(full_name, username, phone), services(name)")
            .gte("start_at", start.isoformat())
            .lt("start_at", end.isoformat())
            .order("start_at")
            .execute()
        )
        return res.data

    return await asyncio.to_thread(_query)


async def get_booking(booking_id: int) -> dict | None:
    """Bitta bron — mijoz va xizmat ma'lumotlari bilan birga."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*, clients(telegram_id, full_name, username, phone), services(name, price)")
            .eq("id", booking_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    return await asyncio.to_thread(_query)


async def update_status(booking_id: int, status: str) -> None:
    def _query():
        get_supabase().table(TABLE).update({"status": status}).eq("id", booking_id).execute()

    return await asyncio.to_thread(_query)


async def update_booking(booking_id: int, fields: dict) -> dict | None:
    """Bronni tahrirlash (vaqt, xizmat, status)."""
    def _query():
        res = get_supabase().table(TABLE).update(fields).eq("id", booking_id).execute()
        return res.data[0] if res.data else None

    return await asyncio.to_thread(_query)


async def get_client_upcoming(client_id: int, from_dt: datetime) -> list[dict]:
    """Mijozning kelgusi bronlari (xizmat nomi bilan birga)."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*, services(name, price)")
            .eq("client_id", client_id)
            .gte("start_at", from_dt.isoformat())
            .in_("status", list(ACTIVE_STATUSES))
            .order("start_at")
            .execute()
        )
        return res.data

    return await asyncio.to_thread(_query)
