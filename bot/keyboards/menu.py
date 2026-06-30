"""Asosiy menyu (reply klaviatura)."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Navbatga yozilish")],
            [KeyboardButton(text="📋 Mening navbatlarim")],
        ],
        resize_keyboard=True,
    )
