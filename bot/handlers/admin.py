"""Admin (akam) tomoni: panel tugmasi + bronni tasdiqlash / bekor qilish."""
import os
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    MenuButtonWebApp,
    Message,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import load_config
from bot.database import bookings_repo
from bot.utils.tz import fmt_date, fmt_time

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in load_config().admin_ids


@router.message(Command("admin"))
async def admin_panel(message: Message, bot: Bot) -> None:
    if not _is_admin(message.from_user.id):
        return  # admin bo'lmaganlarga jim

    url = os.getenv("WEBAPP_URL")
    if not url:
        await message.answer("⚠️ Admin panel manzili (WEBAPP_URL) sozlanmagan.")
        return

    # Yozuv yonida doimiy "Panel" tugmasini o'rnatamiz
    try:
        await bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=MenuButtonWebApp(text="🖥 Panel", web_app=WebAppInfo(url=url)),
        )
    except Exception:
        pass

    kb = InlineKeyboardBuilder()
    kb.button(text="🖥 Admin panelni ochish", web_app=WebAppInfo(url=url))
    await message.answer(
        "<b>Tilla Barber — boshqaruv paneli</b>\n\n"
        "Quyidagi tugma orqali oching. Bundan keyin yozuv yonidagi «🖥 Panel» "
        "tugmasi ham doim shu yerda turadi.",
        reply_markup=kb.as_markup(),
    )


@router.callback_query(F.data.startswith("adm:"))
async def admin_action(cb: CallbackQuery, bot: Bot) -> None:
    if not _is_admin(cb.from_user.id):
        await cb.answer("Bu tugma faqat admin uchun", show_alert=True)
        return

    _, action, bid = cb.data.split(":")
    booking = await bookings_repo.get_booking(int(bid))
    if not booking:
        await cb.answer("Bron topilmadi", show_alert=True)
        return
    if booking["status"] != "pending":
        await cb.answer(f"Bu bron allaqachon ko'rib chiqilgan ({booking['status']})", show_alert=True)
        return

    client = booking.get("clients") or {}
    service = booking.get("services") or {}
    start = datetime.fromisoformat(booking["start_at"])

    if action == "ok":
        await bookings_repo.update_status(int(bid), "confirmed")
        await cb.message.edit_text(cb.message.html_text + "\n\n✅ <b>TASDIQLANDI</b>")
        await cb.answer("Tasdiqlandi ✅")
        if client.get("telegram_id"):
            await _safe_send(
                bot, client["telegram_id"],
                "✅ <b>Navbatingiz tasdiqlandi!</b>\n\n"
                f"✂️ {service.get('name')}\n"
                f"📅 {fmt_date(start.date())}, 🕐 {fmt_time(start)}\n\n"
                "Kutib qolamiz! 💈",
            )

    elif action == "no":
        await bookings_repo.update_status(int(bid), "cancelled", cancelled_by="admin")
        await cb.message.edit_text(cb.message.html_text + "\n\n❌ <b>BEKOR QILINDI</b>")
        await cb.answer("Bekor qilindi")
        if client.get("telegram_id"):
            await _safe_send(
                bot, client["telegram_id"],
                "❌ <b>Afsuski, navbatingiz bekor qilindi.</b>\n\n"
                f"✂️ {service.get('name')}\n"
                f"📅 {fmt_date(start.date())}, 🕐 {fmt_time(start)}\n\n"
                "Boshqa vaqtga yozilishingiz mumkin.",
            )


async def _safe_send(bot: Bot, chat_id: int, text: str) -> None:
    try:
        await bot.send_message(chat_id, text)
    except Exception:
        pass
