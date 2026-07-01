"""Mijozlar jadvali bilan ishlash (CRUD).

Supabase klienti sinxron, shuning uchun so'rovlarni asyncio.to_thread orqali
alohida oqimda bajaramiz — bot event-loop bloklanmaydi.
"""
import asyncio

from bot.database.client import get_supabase

TABLE = "clients"


async def get_client_by_telegram_id(telegram_id: int) -> dict | None:
    """Telegram ID bo'yicha mijozni topish. Topilmasa None."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*")
            .eq("telegram_id", telegram_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    return await asyncio.to_thread(_query)


async def create_client_record(
    telegram_id: int,
    full_name: str,
    phone: str,
    birthday: str | None,
    username: str | None = None,
) -> dict:
    """Yangi mijozni saqlash. birthday — 'YYYY-MM-DD' yoki None."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .insert(
                {
                    "telegram_id": telegram_id,
                    "username": username,
                    "full_name": full_name,
                    "phone": phone,
                    "birthday": birthday,
                }
            )
            .execute()
        )
        return res.data[0]

    return await asyncio.to_thread(_query)


async def get_client_by_id(client_id: int) -> dict | None:
    def _query():
        res = get_supabase().table(TABLE).select("*").eq("id", client_id).limit(1).execute()
        return res.data[0] if res.data else None

    return await asyncio.to_thread(_query)


async def create_manual_client(full_name: str, phone: str) -> dict:
    """Admin qo'lda qo'shgan mijoz (Telegram'siz bo'lishi mumkin)."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .insert({"full_name": full_name, "phone": phone})
            .execute()
        )
        return res.data[0]

    return await asyncio.to_thread(_query)


async def search_clients(q: str, limit: int = 20) -> list[dict]:
    """Ism yoki telefon bo'yicha qidirish (admin bron qo'shishda)."""
    pattern = f"%{q}%"
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*")
            .or_(f"full_name.ilike.{pattern},phone.ilike.{pattern}")
            .limit(limit)
            .execute()
        )
        return res.data

    return await asyncio.to_thread(_query)


async def list_clients(limit: int = 500) -> list[dict]:
    """Barcha mijozlar (admin CRM uchun), yangidan eskiga."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data

    return await asyncio.to_thread(_query)


async def set_retention_sent(client_id: int, dt) -> None:
    def _query():
        get_supabase().table(TABLE).update({"last_retention_sent": dt.isoformat()}).eq("id", client_id).execute()

    return await asyncio.to_thread(_query)


async def set_birthday_greeted(client_id: int, day) -> None:
    def _query():
        get_supabase().table(TABLE).update({"last_birthday_greeted": day.isoformat()}).eq("id", client_id).execute()

    return await asyncio.to_thread(_query)


async def update_username(telegram_id: int, username: str | None) -> None:
    """Mijozning Telegram username'ini yangilash (o'zgargan bo'lsa)."""
    def _query():
        get_supabase().table(TABLE).update({"username": username}).eq(
            "telegram_id", telegram_id
        ).execute()

    await asyncio.to_thread(_query)
