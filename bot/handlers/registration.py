"""/start va mijozni ro'yxatdan o'tkazish (ism → telefon → tug'ilgan kun)."""
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.database.clients_repo import create_client_record, get_client_by_telegram_id
from bot.keyboards.reply import phone_request_kb, skip_kb
from bot.states.registration import Registration

router = Router()

_SKIP_WORDS = {"o'tkazib yuborish", "otkazib yuborish", "skip"}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    existing = await get_client_by_telegram_id(message.from_user.id)

    if existing:
        await message.answer(
            f"Assalomu alaykum, <b>{existing['full_name']}</b>! 💈\n\n"
            "<b>Tilla Barber</b>'ga xush kelibsiz.\n"
            "Tez orada bu yerdan navbatga yozilishingiz mumkin bo'ladi.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await state.set_state(Registration.full_name)
    await message.answer(
        "Assalomu alaykum! 💈 <b>Tilla Barber</b>'ga xush kelibsiz.\n\n"
        "Sizni ro'yxatdan o'tkazamiz. <b>Ism familiyangizni</b> yozing:",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Registration.full_name, F.text)
async def reg_full_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Iltimos, to'liq ism familiyangizni yozing:")
        return

    await state.update_data(full_name=name)
    await state.set_state(Registration.phone)
    await message.answer(
        "Rahmat! Endi <b>telefon raqamingizni</b> yuboring.\n"
        "Pastdagi tugmani bossangiz avtomatik yuboriladi 👇",
        reply_markup=phone_request_kb(),
    )


@router.message(Registration.phone, F.contact)
async def reg_phone_contact(message: Message, state: FSMContext) -> None:
    await _save_phone_and_ask_birthday(message, state, message.contact.phone_number)


@router.message(Registration.phone, F.text)
async def reg_phone_text(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 9:
        await message.answer(
            "Raqam noto'g'ri ko'rinadi. Qaytadan kiriting yoki tugmadan foydalaning:"
        )
        return
    await _save_phone_and_ask_birthday(message, state, phone)


async def _save_phone_and_ask_birthday(
    message: Message, state: FSMContext, phone: str
) -> None:
    await state.update_data(phone=phone)
    await state.set_state(Registration.birthday)
    await message.answer(
        "Ajoyib! Oxirgi savol — <b>tug'ilgan kuningiz</b> qachon?\n"
        "Format: <code>kun.oy.yil</code> (masalan <code>15.08.1995</code>)\n\n"
        "Tug'ilgan kuningizda sizga maxsus chegirma bo'ladi 🎂",
        reply_markup=skip_kb(),
    )


@router.message(Registration.birthday, F.text)
async def reg_birthday(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    birthday: str | None = None

    if text.lower() not in _SKIP_WORDS:
        try:
            birthday = datetime.strptime(text, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            await message.answer(
                "Sana formati noto'g'ri. <code>kun.oy.yil</code> ko'rinishida yozing "
                "(masalan <code>15.08.1995</code>) yoki \"O'tkazib yuborish\"ni bosing:"
            )
            return

    data = await state.get_data()
    await create_client_record(
        telegram_id=message.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        birthday=birthday,
    )
    await state.clear()
    await message.answer(
        f"Rahmat, <b>{data['full_name']}</b>! ✅\n"
        "Siz ro'yxatdan o'tdingiz.\n\n"
        "Tez orada bu yerdan navbatga yozilishingiz mumkin bo'ladi. 💈",
        reply_markup=ReplyKeyboardRemove(),
    )
