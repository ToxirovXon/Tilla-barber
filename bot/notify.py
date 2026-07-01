"""Telegram'ga to'g'ridan-to'g'ri xabar yuborish (bot jarayonidan mustaqil, HTTP orqali).

Ham admin API, ham scheduler shu funksiyadan foydalanadi.
"""
import httpx

from bot.config import load_config


def _url(method: str) -> str:
    return f"https://api.telegram.org/bot{load_config().bot_token}/{method}"


async def send_message(chat_id: int, text: str) -> bool:
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(_url("sendMessage"), json=payload)
            return r.status_code == 200
    except Exception:
        return False


async def send_photo_file(chat_id: int, filename: str, content: bytes, caption: str) -> str | None:
    """Rasmni fayl sifatida yuboradi va Telegram file_id ni qaytaradi (keyingilar uchun)."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                _url("sendPhoto"),
                data={"chat_id": str(chat_id), "caption": caption, "parse_mode": "HTML"},
                files={"photo": (filename or "image.jpg", content)},
            )
            if r.status_code == 200:
                photos = r.json()["result"]["photo"]
                return photos[-1]["file_id"]
    except Exception:
        pass
    return None


async def send_photo_id(chat_id: int, file_id: str, caption: str) -> bool:
    """Oldin yuklangan rasmni file_id orqali yuboradi (qayta yuklamasdan)."""
    payload = {"chat_id": chat_id, "photo": file_id, "caption": caption, "parse_mode": "HTML"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(_url("sendPhoto"), json=payload)
            return r.status_code == 200
    except Exception:
        return False
