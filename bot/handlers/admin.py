"""Admin (akam) tomoni: bronni tasdiqlash / bekor qilish."""
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from bot.config import load_config
from bot.database import bookings_repo
from bot.utils.tz import fmt_date, fmt_time

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in load_config().admin_ids


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
        await bookings_repo.update_status(int(bid), "cancelled")
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
