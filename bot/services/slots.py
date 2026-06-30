"""Bo'sh vaqtlarni (slot) hisoblash.

Bitta usta (akam) bo'lgani uchun har qanday ustma-ust tushish slotni band qiladi.
"""
from datetime import date, datetime, time, timedelta

from bot.utils.tz import TASHKENT

# Slot boshlanish qadami (daqiqa) — masalan har 30 daqiqada bron boshlanadi
SLOT_STEP_MIN = 30


def generate_slots(
    day: date,
    open_time: time,
    close_time: time,
    duration_min: int,
    busy: list[tuple[datetime, datetime]],
    now: datetime | None = None,
) -> list[datetime]:
    """Berilgan kun uchun bo'sh slot boshlanish vaqtlari ro'yxati.

    day         — qaysi kun
    open/close  — ish vaqti boshi/oxiri
    duration    — tanlangan xizmat davomiyligi (daqiqa)
    busy        — band intervallar [(start, end), ...]
    now         — joriy vaqt (o'tib ketgan slotlarni o'tkazib yuborish uchun)
    """
    slots: list[datetime] = []
    cursor = datetime.combine(day, open_time, tzinfo=TASHKENT)
    close_dt = datetime.combine(day, close_time, tzinfo=TASHKENT)
    step = timedelta(minutes=SLOT_STEP_MIN)
    dur = timedelta(minutes=duration_min)

    while cursor + dur <= close_dt:
        slot_end = cursor + dur

        # O'tib ketgan vaqtlarni ko'rsatmaymiz
        if now is not None and cursor <= now:
            cursor += step
            continue

        # Band intervallar bilan ustma-ust tushmasligini tekshiramiz
        overlap = any(
            not (slot_end <= b_start or cursor >= b_end) for b_start, b_end in busy
        )
        if not overlap:
            slots.append(cursor)

        cursor += step

    return slots
