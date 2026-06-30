"""Navbatga yozilish oqimi: xizmat → kun → vaqt → tasdiq → adminga xabar."""
from datetime import datetime, time, timedelta

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import load_config
from bot.database import (
    bookings_repo,
    clients_repo,
    services_repo,
    working_hours_repo,
)
from bot.services.slots import generate_slots
from bot.utils.tz import TASHKENT, fmt_date, fmt_time
from bot.utils.tz import now as now_tk

router = Router()


# ---------- yordamchilar ----------

def _money(v: int) -> str:
    return f"{v:,}".replace(",", " ")


def _parse_time(v: str) -> time:
    return time.fromisoformat(v)  # "09:00:00" yoki "09:00"


def _parse_dt(v: str) -> datetime:
    return datetime.fromisoformat(v)


def _day_label(d) -> str:
    today = now_tk().date()
    if d == today:
        return "Bugun"
    if d == today + timedelta(days=1):
        return "Ertaga"
    return fmt_date(d)


async def _open_days(n: int) -> list:
    """Bugundan boshlab keyingi n ta ochiq kun."""
    result = []
    d = now_tk().date()
    for _ in range(14):
        wh = await working_hours_repo.get_day(d.weekday())
        if wh and wh.get("is_open"):
            result.append(d)
            if len(result) >= n:
                break
        d += timedelta(days=1)
    return result


async def _services_keyboard():
    services = await services_repo.list_active_services()
    kb = InlineKeyboardBuilder()
    for s in services:
        kb.button(
            text=f"{s['name']} — {_money(s['price'])} so'm",
            callback_data=f"bk:svc:{s['id']}",
        )
    kb.adjust(1)
    return services, kb


# ---------- 1. Xizmat tanlash ----------

@router.message(F.text == "📅 Navbatga yozilish")
async def start_booking(message: Message) -> None:
    services, kb = await _services_keyboard()
    if not services:
        await message.answer("Hozircha xizmatlar qo'shilmagan. Birozdan keyin urinib ko'ring.")
        return
    await message.answer("Qaysi xizmatga yozilasiz?", reply_markup=kb.as_markup())


@router.callback_query(F.data == "bk:services")
async def back_to_services(cb: CallbackQuery) -> None:
    services, kb = await _services_keyboard()
    await cb.message.edit_text("Qaysi xizmatga yozilasiz?", reply_markup=kb.as_markup())
    await cb.answer()


# ---------- 2. Kun tanlash ----------

@router.callback_query(F.data.startswith("bk:svc:"))
async def choose_day(cb: CallbackQuery) -> None:
    service_id = int(cb.data.split(":")[2])
    service = await services_repo.get_service(service_id)
    if not service:
        await cb.answer("Xizmat topilmadi", show_alert=True)
        return

    days = await _open_days(7)
    kb = InlineKeyboardBuilder()
    for d in days:
        kb.button(
            text=_day_label(d),
            callback_data=f"bk:day:{service_id}:{d.strftime('%Y%m%d')}",
        )
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="« Orqaga", callback_data="bk:services"))
    await cb.message.edit_text(
        f"<b>{service['name']}</b>\nQaysi kunga yozilasiz?",
        reply_markup=kb.as_markup(),
    )
    await cb.answer()


# ---------- 3. Vaqt tanlash ----------

@router.callback_query(F.data.startswith("bk:day:"))
async def choose_slot(cb: CallbackQuery) -> None:
    _, _, svcid, ymd = cb.data.split(":")
    service_id = int(svcid)
    day = datetime.strptime(ymd, "%Y%m%d").date()

    service = await services_repo.get_service(service_id)
    wh = await working_hours_repo.get_day(day.weekday())
    if not service or not wh or not wh.get("is_open"):
        await cb.answer("Bu kun ish kuni emas", show_alert=True)
        return

    open_t = _parse_time(wh["open_time"])
    close_t = _parse_time(wh["close_time"])
    day_start = datetime.combine(day, time(0, 0), tzinfo=TASHKENT)
    day_end = day_start + timedelta(days=1)

    rows = await bookings_repo.get_bookings_for_day(day_start, day_end)
    busy = [(_parse_dt(b["start_at"]), _parse_dt(b["end_at"])) for b in rows]
    now = now_tk() if day == now_tk().date() else None

    slots = generate_slots(day, open_t, close_t, service["duration"], busy, now=now)
    if not slots:
        await cb.answer("Bu kunda bo'sh vaqt qolmadi", show_alert=True)
        return

    kb = InlineKeyboardBuilder()
    for s in slots:
        kb.button(
            text=fmt_time(s),
            callback_data=f"bk:slot:{service_id}:{ymd}:{s.strftime('%H%M')}",
        )
    kb.adjust(4)
    kb.row(InlineKeyboardButton(text="« Orqaga", callback_data=f"bk:svc:{service_id}"))
    await cb.message.edit_text(
        f"<b>{service['name']}</b> — {_day_label(day)}\nBo'sh vaqtni tanlang:",
        reply_markup=kb.as_markup(),
    )
    await cb.answer()


# ---------- 4. Tasdiqlash ----------

@router.callback_query(F.data.startswith("bk:slot:"))
async def confirm_slot(cb: CallbackQuery) -> None:
    _, _, svcid, ymd, hm = cb.data.split(":")
    service = await services_repo.get_service(int(svcid))
    if not service:
        await cb.answer("Xizmat topilmadi", show_alert=True)
        return
    day = datetime.strptime(ymd, "%Y%m%d").date()
    start = datetime.combine(day, time(int(hm[:2]), int(hm[2:])), tzinfo=TASHKENT)

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlash", callback_data=f"bk:ok:{svcid}:{ymd}:{hm}")
    kb.button(text="« Bekor qilish", callback_data="bk:cancel")
    kb.adjust(1)
    await cb.message.edit_text(
        "<b>Navbatni tasdiqlang:</b>\n\n"
        f"✂️ {service['name']}\n"
        f"💰 {_money(service['price'])} so'm\n"
        f"📅 {_day_label(day)}\n"
        f"🕐 {fmt_time(start)}",
        reply_markup=kb.as_markup(),
    )
    await cb.answer()


# ---------- 5. Bronni saqlash + adminga xabar ----------

@router.callback_query(F.data.startswith("bk:ok:"))
async def do_book(cb: CallbackQuery, bot: Bot) -> None:
    _, _, svcid, ymd, hm = cb.data.split(":")
    service = await services_repo.get_service(int(svcid))
    client = await clients_repo.get_client_by_telegram_id(cb.from_user.id)
    if not service or not client:
        await cb.answer("Xatolik yuz berdi", show_alert=True)
        return

    day = datetime.strptime(ymd, "%Y%m%d").date()
    start = datetime.combine(day, time(int(hm[:2]), int(hm[2:])), tzinfo=TASHKENT)
    end = start + timedelta(minutes=service["duration"])

    # Qayta tekshirish — bu vaqt hali bo'shmi (ikki kishi bir vaqtni bosib qolmasligi uchun)
    day_start = datetime.combine(day, time(0, 0), tzinfo=TASHKENT)
    rows = await bookings_repo.get_bookings_for_day(day_start, day_start + timedelta(days=1))
    busy = [(_parse_dt(b["start_at"]), _parse_dt(b["end_at"])) for b in rows]
    if any(not (end <= bs or start >= be) for bs, be in busy):
        await cb.answer("Afsus, bu vaqt band bo'lib qoldi. Boshqa vaqt tanlang.", show_alert=True)
        return

    await bookings_repo.create_booking(
        client_id=client["id"],
        service_id=service["id"],
        start_at=start,
        end_at=end,
        price=service["price"],
        source="bot",
    )
    await cb.message.edit_text(
        "✅ <b>Navbatingiz qabul qilindi!</b>\n\n"
        f"✂️ {service['name']}\n"
        f"📅 {_day_label(day)}, 🕐 {fmt_time(start)}\n\n"
        "Akamiz tez orada tasdiqlaydi. Kutib qolamiz! 💈"
    )
    await cb.answer()
    await _notify_admins(bot, client, service, start)


async def _notify_admins(bot: Bot, client: dict, service: dict, start: datetime) -> None:
    config = load_config()
    uname = f"@{client['username']}" if client.get("username") else "—"
    text = (
        "🆕 <b>Yangi bron!</b>\n\n"
        f"👤 {client['full_name']} ({uname})\n"
        f"📞 {client['phone']}\n"
        f"✂️ {service['name']} — {_money(service['price'])} so'm\n"
        f"📅 {fmt_date(start.date())}\n"
        f"🕐 {fmt_time(start)}"
    )
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass


@router.callback_query(F.data == "bk:cancel")
async def cancel_booking(cb: CallbackQuery) -> None:
    await cb.message.edit_text("Bekor qilindi. Asosiy menyudan davom etishingiz mumkin 👇")
    await cb.answer()


# ---------- Mening navbatlarim ----------

@router.message(F.text == "📋 Mening navbatlarim")
async def my_bookings(message: Message) -> None:
    client = await clients_repo.get_client_by_telegram_id(message.from_user.id)
    if not client:
        await message.answer("Avval /start bosing.")
        return

    items = await bookings_repo.get_client_upcoming(client["id"], now_tk())
    if not items:
        await message.answer("Sizda kelgusi navbat yo'q. «📅 Navbatga yozilish» orqali yoziling.")
        return

    status_uz = {"pending": "⏳ kutilmoqda", "confirmed": "✅ tasdiqlangan"}
    lines = ["<b>Kelgusi navbatlaringiz:</b>\n"]
    for b in items:
        svc = b.get("services") or {}
        start = _parse_dt(b["start_at"])
        st = status_uz.get(b["status"], b["status"])
        lines.append(f"✂️ {svc.get('name', '—')} — {fmt_date(start.date())}, {fmt_time(start)} ({st})")
    await message.answer("\n".join(lines))
