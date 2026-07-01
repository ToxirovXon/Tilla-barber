"""Vaqt bo'yicha avtomatik vazifalar: eslatma, kunlik hisobot, retention, tug'ilgan kun."""
import logging
from datetime import date, datetime, time, timedelta

from bot import notify
from bot.config import load_config
from bot.database import bookings_repo, clients_repo, settings_repo
from bot.utils.tz import TASHKENT, fmt_date, fmt_time
from bot.utils.tz import now as now_tk

logger = logging.getLogger(__name__)


def _money(v: int) -> str:
    return f"{v:,}".replace(",", " ")


def _first_name(full: str | None) -> str:
    return (full or "").split(" ")[0] if full else ""


async def send_reminders() -> None:
    """Konfiguratsiyaga ko'ra qolgan tasdiqlangan bronlarga eslatma yuboradi."""
    cfg = (await settings_repo.get_all())["reminder"]
    if not cfg.get("enabled"):
        return
    hours = int(cfg.get("hours") or 2)
    tmpl = cfg.get("text") or ""

    now = now_tk()
    rows = await bookings_repo.get_reminder_due(now, now + timedelta(hours=hours))
    for b in rows:
        client = b.get("clients") or {}
        service = b.get("services") or {}
        tg = client.get("telegram_id")
        start = datetime.fromisoformat(b["start_at"])
        if tg:
            text = (
                tmpl.replace("{time}", fmt_time(start))
                .replace("{service}", service.get("name") or "")
                .replace("{name}", _first_name(client.get("full_name")))
            )
            await notify.send_message(tg, text)
        await bookings_repo.mark_reminder_sent(b["id"])
    if rows:
        logger.info(f"Eslatma yuborildi: {len(rows)} ta")


async def run_retention() -> None:
    """Ancha kelmagan mijozlarni qaytarish (sozlamadagi kun + matn)."""
    cfg = (await settings_repo.get_all())["retention"]
    if not cfg.get("enabled"):
        return
    days = int(cfg.get("days") or 35)
    tmpl = cfg.get("text") or ""

    now = now_tk()
    last = await bookings_repo.last_completed_per_client()
    clients = await clients_repo.list_clients()
    sent = 0
    for c in clients:
        tg = c.get("telegram_id")
        lv = last.get(c["id"])
        if not tg or not lv:
            continue
        if (now - lv).days < days:
            continue
        lrs = c.get("last_retention_sent")
        # Oxirgi tashrifdan keyin allaqachon yuborilgan bo'lsa — qayta yubormaymiz
        if lrs and datetime.fromisoformat(lrs) >= lv:
            continue
        text = tmpl.replace("{name}", _first_name(c.get("full_name")))
        await notify.send_message(tg, text)
        await clients_repo.set_retention_sent(c["id"], now)
        sent += 1
    if sent:
        logger.info(f"Retention yuborildi: {sent} ta")


async def run_birthday() -> None:
    """Bugun tug'ilgan kuni bo'lgan mijozlarga tabrik + chegirma."""
    cfg = (await settings_repo.get_all())["birthday"]
    if not cfg.get("enabled"):
        return
    percent = int(cfg.get("percent") or 0)
    tmpl = cfg.get("text") or ""

    today = now_tk().date()
    clients = await clients_repo.list_clients()
    sent = 0
    for c in clients:
        tg = c.get("telegram_id")
        bday = c.get("birthday")
        if not tg or not bday:
            continue
        bd = date.fromisoformat(bday)
        if (bd.month, bd.day) != (today.month, today.day):
            continue
        lbg = c.get("last_birthday_greeted")
        if lbg and date.fromisoformat(lbg) == today:
            continue
        text = tmpl.replace("{name}", _first_name(c.get("full_name"))).replace("{percent}", str(percent))
        await notify.send_message(tg, text)
        await clients_repo.set_birthday_greeted(c["id"], today)
        sent += 1
    if sent:
        logger.info(f"Tug'ilgan kun tabrigi yuborildi: {sent} ta")


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
