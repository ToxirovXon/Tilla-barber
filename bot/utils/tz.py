"""Toshkent vaqt zonasi yordamchilari (UTC+5, yozgi vaqt yo'q)."""
from datetime import datetime
from zoneinfo import ZoneInfo

TASHKENT = ZoneInfo("Asia/Tashkent")

# O'zbekcha hafta kunlari (0=Dushanba ... 6=Yakshanba)
WEEKDAYS_UZ = [
    "Dushanba",
    "Seshanba",
    "Chorshanba",
    "Payshanba",
    "Juma",
    "Shanba",
    "Yakshanba",
]

MONTHS_UZ = [
    "yanvar", "fevral", "mart", "aprel", "may", "iyun",
    "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr",
]


def now() -> datetime:
    return datetime.now(TASHKENT)


def fmt_date(d) -> str:
    """15 avgust, Juma"""
    return f"{d.day} {MONTHS_UZ[d.month - 1]}, {WEEKDAYS_UZ[d.weekday()]}"


def fmt_time(dt: datetime) -> str:
    """10:30"""
    return dt.astimezone(TASHKENT).strftime("%H:%M")
