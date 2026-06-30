"""Telegram Web App "initData" ni tekshirish va admin huquqini aniqlash.

Telegram har bir Web App ochilganda initData yuboradi (foydalanuvchi + hash).
Hash bot tokeni bilan HMAC-SHA256 orqali tekshiriladi — soxtalashtirib bo'lmaydi.
Hujjat: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException

from bot.config import load_config


def validate_init_data(init_data: str) -> dict | None:
    """initData to'g'ri bo'lsa — ichidagi ma'lumotni (user bilan) qaytaradi, aks holda None."""
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    token = load_config().bot_token
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, received_hash):
        return None

    if "user" in parsed:
        try:
            parsed["user"] = json.loads(parsed["user"])
        except json.JSONDecodeError:
            parsed["user"] = {}
    return parsed


def require_admin(authorization: str = Header(default="")) -> dict:
    """FastAPI dependency: "Authorization: tma <initData>" sarlavhasini tekshiradi.

    Faqat ADMIN_IDS ro'yxatidagi foydalanuvchini o'tkazadi.
    """
    if not authorization.startswith("tma "):
        raise HTTPException(status_code=401, detail="initData yo'q")

    init_data = authorization[4:]
    data = validate_init_data(init_data)
    if data is None:
        raise HTTPException(status_code=401, detail="initData yaroqsiz")

    user = data.get("user") or {}
    if user.get("id") not in load_config().admin_ids:
        raise HTTPException(status_code=403, detail="Siz admin emassiz")

    return user
