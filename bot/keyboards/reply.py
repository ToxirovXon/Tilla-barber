"""Oddiy (reply) tugmalar."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def phone_request_kb() -> ReplyKeyboardMarkup:
    """Telefon raqamni avtomatik ulashish tugmasi."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def skip_kb() -> ReplyKeyboardMarkup:
    """O'tkazib yuborish tugmasi (tug'ilgan kun ixtiyoriy)."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="O'tkazib yuborish")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
