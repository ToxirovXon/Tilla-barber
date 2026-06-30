"""Xizmatlar jadvali bilan ishlash."""
import asyncio

from bot.database.client import get_supabase

TABLE = "services"


async def list_active_services() -> list[dict]:
    """Faol xizmatlar (mijozга ko'rsatish uchun)."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*")
            .eq("is_active", True)
            .order("sort_order")
            .order("id")
            .execute()
        )
        return res.data

    return await asyncio.to_thread(_query)


async def get_service(service_id: int) -> dict | None:
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*")
            .eq("id", service_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    return await asyncio.to_thread(_query)
