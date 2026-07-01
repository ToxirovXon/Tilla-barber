"""Telegram'ga to'g'ridan-to'g'ri xabar yuborish (bot jarayonidan mustaqil, HTTP orqali).

Ham admin API, ham scheduler shu funksiyadan foydalanadi.
"""
import httpx

from bot.config import load_config


async def send_message(chat_id: int, text: str) -> bool:
    token = load_config().bot_token
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, json=payload)
            return r.status_code == 200
    except Exception:
        return False
