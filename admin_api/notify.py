"""Bot jarayonidan mustaqil ravishda Telegram xabar yuborish (HTTP orqali).

Admin panel (FastAPI) alohida jarayon — ishlab turgan bot instansiyasiga
murojaat qila olmaydi, shuning uchun xabarni to'g'ridan-to'g'ri Telegram API
orqali yuboramiz.
"""
import httpx

from bot.config import load_config


async def send_message(chat_id: int, text: str) -> None:
    token = load_config().bot_token
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json=payload)
    except Exception:
        pass
