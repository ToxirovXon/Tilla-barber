"""Bron zanjirini real baza bilan tekshirish (Telegram'siz)."""
import asyncio
import sys
from datetime import datetime, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.database import bookings_repo, clients_repo, services_repo, working_hours_repo
from bot.database.client import get_supabase
from bot.services.slots import generate_slots
from bot.utils.tz import TASHKENT, fmt_time
from bot.utils.tz import now as now_tk


async def main():
    # 1) xizmatlar
    services = await services_repo.list_active_services()
    print("Xizmatlar:", [f"{s['name']}({s['duration']}daq)" for s in services])
    service = services[0]

    # 2) ochiq kun top (ertaga, band emas deb)
    day = now_tk().date() + timedelta(days=1)
    for _ in range(7):
        wh = await working_hours_repo.get_day(day.weekday())
        if wh and wh["is_open"]:
            break
        day += timedelta(days=1)
    wh = await working_hours_repo.get_day(day.weekday())
    print(f"Tanlangan kun: {day} (ish: {wh['open_time']}-{wh['close_time']})")

    # 3) slotlar
    day_start = datetime.combine(day, time(0, 0), tzinfo=TASHKENT)
    rows = await bookings_repo.get_bookings_for_day(day_start, day_start + timedelta(days=1))
    busy = [(datetime.fromisoformat(b["start_at"]), datetime.fromisoformat(b["end_at"])) for b in rows]
    open_t = time.fromisoformat(wh["open_time"])
    close_t = time.fromisoformat(wh["close_time"])
    slots = generate_slots(day, open_t, close_t, service["duration"], busy)
    print(f"Bo'sh slotlar ({len(slots)} ta), birinchi 5:", [fmt_time(s) for s in slots[:5]])

    # 4) birinchi slotга bron yaratamiz
    client = await clients_repo.get_client_by_telegram_id(1825068258)
    start = slots[0]
    end = start + timedelta(minutes=service["duration"])
    booking = await bookings_repo.create_booking(
        client_id=client["id"], service_id=service["id"],
        start_at=start, end_at=end, price=service["price"], source="bot",
    )
    print(f"Bron yaratildi: id={booking['id']}, {fmt_time(start)}-{fmt_time(end)}, status={booking['status']}, source={booking['source']}")

    # 5) endi o'sha slot band bo'lishi kerak
    rows2 = await bookings_repo.get_bookings_for_day(day_start, day_start + timedelta(days=1))
    busy2 = [(datetime.fromisoformat(b["start_at"]), datetime.fromisoformat(b["end_at"])) for b in rows2]
    slots2 = generate_slots(day, open_t, close_t, service["duration"], busy2)
    booked = fmt_time(start)
    still_free = [fmt_time(s) for s in slots2]
    print(f"Bron qilingan slot ({booked}) endi ro'yxatda yo'qmi: {'HA ✅' if booked not in still_free else 'YO`Q ❌'}")

    # 6) mening navbatlarim
    upcoming = await bookings_repo.get_client_upcoming(client["id"], now_tk())
    print(f"Mijoz kelgusi bronlari: {len(upcoming)} ta")
    for u in upcoming:
        print(f"   {u.get('services', {}).get('name')} — {fmt_time(datetime.fromisoformat(u['start_at']))} ({u['status']})")

    # 7) tozalash (test bronini o'chiramiz)
    get_supabase().table("bookings").delete().eq("id", booking["id"]).execute()
    print(f"Test broni o'chirildi (id={booking['id']}). Test MUVAFFAQIYATLI.")


asyncio.run(main())
