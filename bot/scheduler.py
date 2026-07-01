"""Vaqt bo'yicha avtomatik vazifalar: eslatma va kunlik hisobot."""
import logging
from datetime import datetime, time, timedelta

from bot import notify
from bot.config import load_config
from bot.database import bookings_repo
from bot.utils.tz import TASHKENT, fmt_date, fmt_time
from bot.utils.tz import now as now_tk

logger = logging.getLogger(__name__)

REMIND_BEFORE_HOURS = 2


def _money(v: int) -> str:
    return f"{v:,}".replace(",", " ")


async def send_reminders() -> None:
    """2 soat qolgan tasdiqlangan bronlarga eslatma yuboradi."""
    now = now_tk()
    window_end = now + timedelta(hours=REMIND_BEFORE_HOURS)
    rows = await bookings_repo.get_reminder_due(now, window_end)

    for b in rows:
        client = b.get("clients") or {}
        service = b.get("services") or {}
        tg = client.get("telegram_id")
        start = datetime.fromisoformat(b["start_at"])
        if tg:
            await notify.send_message(
                tg,
                "🔔 <b>Eslatma!</b>\n\n"
                f"Bugun soat <b>{fmt_time(start)}</b> da navbatingiz bor.\n"
                f"✂️ {service.get('name')}\n\n"
                "Kutib qolamiz! 💈",
            )
        await bookings_repo.mark_reminder_sent(b["id"])

    if rows:
        logger.info(f"Eslatma yuborildi: {len(rows)} ta")


async def send_daily_report() -> None:
    """Har kuni akamga: bugungi natija + ertangi navbatlar."""
    now = now_tk()
    today0 = datetime.combine(now.date(), time(0, 0), tzinfo=TASHKENT)
    tomorrow0 = today0 + timedelta(days=1)
    dayafter0 = today0 + timedelta(days=2)

    today = await bookings_repo.list_bookings(today0, tomorrow0)
    tomorrow = await bookings_repo.list_bookings(tomorrow0, dayafter0)

    completed = [b for b in today if b["status"] == "completed"]
    revenue = sum((b.get("price") or 0) for b in completed)
    no_show = len([b for b in today if b["status"] == "no_show"])
    tomorrow_active = sorted(
        [b for b in tomorrow if b["status"] in ("pending", "confirmed")],
        key=lambda x: x["start_at"],
    )

    lines = [
        f"📊 <b>Kunlik hisobot</b> — {fmt_date(now.date())}",
        "",
        f"✅ Keldi: <b>{len(completed)}</b> ta",
        f"💰 Daromad: <b>{_money(revenue)}</b> so'm",
        f"🚫 Kelmadi: {no_show} ta",
        "",
        f"📅 Ertaga: <b>{len(tomorrow_active)}</b> ta navbat",
    ]
    for b in tomorrow_active:
        c = b.get("clients") or {}
        s = b.get("services") or {}
        start = datetime.fromisoformat(b["start_at"])
        lines.append(f"  • {fmt_time(start)} — {c.get('full_name', '—')} ({s.get('name', '')})")

    text = "\n".join(lines)
    for admin_id in load_config().admin_ids:
        await notify.send_message(admin_id, text)
    logger.info("Kunlik hisobot yuborildi")
