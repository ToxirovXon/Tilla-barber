"""Muhit o'zgaruvchilarini (.env) o'qish va tekshirish."""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_ids: list[int] = field(default_factory=list)
    supabase_url: str | None = None
    supabase_key: str | None = None


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. .env faylini yarating va tokenni qo'ying "
            "(.env.example namunasidan nusxa oling)."
        )

    admin_raw = os.getenv("ADMIN_IDS", "")
    admin_ids = [int(x) for x in admin_raw.split(",") if x.strip().isdigit()]

    return Config(
        bot_token=token,
        admin_ids=admin_ids,
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY"),
    )
