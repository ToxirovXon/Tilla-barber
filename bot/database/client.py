"""Supabase ulanishi (bir marta yaratiladi)."""
from supabase import Client, create_client

from bot.config import load_config

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        config = load_config()
        if not config.supabase_url or not config.supabase_key:
            raise RuntimeError(
                "Supabase sozlanmagan. .env faylida SUPABASE_URL va SUPABASE_KEY ni to'ldiring."
            )
        _client = create_client(config.supabase_url, config.supabase_key)
    return _client
