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


async def list_all_services() -> list[dict]:
    """Barcha xizmatlar (faol va nofaol) — admin uchun."""
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .select("*")
            .order("sort_order")
            .order("id")
            .execute()
        )
        return res.data

    return await asyncio.to_thread(_query)


async def create_service(name: str, price: int, duration: int, sort_order: int = 0) -> dict:
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .insert(
                {
                    "name": name,
                    "price": price,
                    "duration": duration,
                    "sort_order": sort_order,
                }
            )
            .execute()
        )
        return res.data[0]

    return await asyncio.to_thread(_query)


async def update_service(service_id: int, fields: dict) -> dict | None:
    def _query():
        res = (
            get_supabase()
            .table(TABLE)
            .update(fields)
            .eq("id", service_id)
            .execute()
        )
        return res.data[0] if res.data else None

    return await asyncio.to_thread(_query)


async def deactivate_service(service_id: int) -> None:
    """Xizmatni o'chirish o'rniga nofaol qilamiz (bron tarixi saqlanadi)."""
    def _query():
        get_supabase().table(TABLE).update({"is_active": False}).eq("id", service_id).execute()

    return await asyncio.to_thread(_query)
