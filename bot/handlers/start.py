"""/start buyrug'i — mijozni kutib olish."""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>! 💈\n\n"
        "<b>Tilla Barber</b> botiga xush kelibsiz.\n\n"
        "Bu yerdan tez orada navbatga yozilishingiz mumkin bo'ladi."
    )
