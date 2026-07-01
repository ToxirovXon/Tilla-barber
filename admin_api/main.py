"""Admin panel backend (FastAPI). Telegram Web App shu API bilan ishlaydi.

Ishga tushirish: uvicorn admin_api.main:app --reload --port 8000
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta

from aiogram.types import Update
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from admin_api import notify
from admin_api.auth import require_admin
from bot.database import bookings_repo, clients_repo, services_repo, working_hours_repo
from bot.runner import build, run_polling
from bot.utils.tz import TASHKENT, fmt_date, fmt_time
from bot.utils.tz import now as now_tk

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)

# Webhook xavfsizlik tokeni (Telegram har so'rovda shu sarlavhani yuboradi)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "tilla-barber-hook-7a3f9c2e")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup HECH QACHON qulamaydi — xatoni app.state ga yozib, API ni tirik saqlaydi."""
    app.state.bot = None
    app.state.dp = None
    app.state.startup_error = None
    try:
        domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        run_bot_local = os.getenv("RUN_BOT", "").strip() == "1"

        if domain:
            bot, dp = build()
            app.state.bot = bot
            app.state.dp = dp
            url = f"https://{domain}/webhook"
            await bot.set_webhook(
                url,
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
            )
            logger.info(f"Webhook o'rnatildi: {url}")

            # Scheduler: eslatma (har 5 daq) + kunlik hisobot (20:00)
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from bot import scheduler as sched
            aps = AsyncIOScheduler(timezone=TASHKENT)
            aps.add_job(sched.send_reminders, "interval", minutes=5, id="reminders")
            aps.add_job(sched.send_daily_report, "cron", hour=20, minute=0, id="daily_report")
            aps.start()
            app.state.scheduler = aps
            logger.info("Scheduler ishga tushdi (eslatma 5 daq, hisobot 20:00)")
        elif run_bot_local:
            asyncio.create_task(run_polling())
            logger.info("Bot polling (lokal)")
    except Exception as e:
        app.state.startup_error = repr(e)
        logger.exception("Startup xato")
    yield


app = FastAPI(title="Tilla Barber Admin API", lifespan=lifespan)


@app.post("/webhook")
async def telegram_webhook(request: Request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="forbidden")
    if request.app.state.bot is None:
        raise HTTPException(status_code=503, detail="bot tayyor emas")
    data = await request.json()
    update = Update.model_validate(data, context={"bot": request.app.state.bot})
    await request.app.state.dp.feed_update(request.app.state.bot, update)
    return {"ok": True}


@app.get("/api/debug")
async def debug():
    """Nima buzilganini masofadan ko'rish (maxfiy qiymatlar YO'Q, faqat bor/yo'q)."""
    def present(k: str) -> bool:
        return bool(os.getenv(k))

    cfg_loads, cfg_err = True, None
    try:
        from bot.config import load_config
        load_config()
    except Exception as e:
        cfg_loads, cfg_err = False, repr(e)

    return {
        "env_present": {
            "BOT_TOKEN": present("BOT_TOKEN"),
            "SUPABASE_URL": present("SUPABASE_URL"),
            "SUPABASE_KEY": present("SUPABASE_KEY"),
        },
        "env_values": {
            "ADMIN_IDS": os.getenv("ADMIN_IDS"),
            "RUN_BOT": os.getenv("RUN_BOT"),
            "WEBAPP_URL": os.getenv("WEBAPP_URL"),
            "RAILWAY_PUBLIC_DOMAIN": os.getenv("RAILWAY_PUBLIC_DOMAIN"),
        },
        "config_loads": cfg_loads,
        "config_error": cfg_err,
        "startup_error": getattr(app.state, "startup_error", None),
        "bot_ready": app.state.bot is not None,
    }

# Dev uchun barcha manbalardan ruxsat (auth header orqali himoyalangan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Pydantic modellar ----------

class ServiceIn(BaseModel):
    name: str
    price: int
    duration: int
    sort_order: int = 0


class ServiceUpdate(BaseModel):
    name: str | None = None
    price: int | None = None
    duration: int | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class ClientIn(BaseModel):
    full_name: str
    phone: str


class BookingCreate(BaseModel):
    service_id: int
    start_at: str                      # ISO datetime (Toshkent)
    client_id: int | None = None       # mavjud mijoz
    new_client: ClientIn | None = None # yoki yangi mijoz


class BookingUpdate(BaseModel):
    service_id: int | None = None
    start_at: str | None = None
    status: str | None = None


class CancelBody(BaseModel):
    message: str | None = None         # admin yozgan maxsus matn


class WorkingDay(BaseModel):
    weekday: int                       # 0=Dushanba ... 6=Yakshanba
    is_open: bool
    open_time: str | None = None       # "09:00"
    close_time: str | None = None
    break_start: str | None = None     # tushlik boshi (ixtiyoriy)
    break_end: str | None = None


class WorkingHoursIn(BaseModel):
    days: list[WorkingDay]


class BroadcastIn(BaseModel):
    message: str


# ---------- Health (auth talab qilmaydi) ----------

@app.get("/api/health")
async def health():
    return {"ok": True}


@app.get("/api/me")
async def me(admin: dict = Depends(require_admin)):
    return {"id": admin.get("id"), "name": admin.get("first_name")}


# ---------- Bronlar ----------

@app.get("/api/bookings")
async def bookings_for_day(day: str | None = None, admin: dict = Depends(require_admin)):
    d = datetime.strptime(day, "%Y-%m-%d").date() if day else now_tk().date()
    start = datetime.combine(d, time(0, 0), tzinfo=TASHKENT)
    end = start + timedelta(days=1)
    rows = await bookings_repo.list_bookings(start, end)
    return {"date": d.isoformat(), "items": rows}


@app.get("/api/bookings/range")
async def bookings_range(start: str, end: str, admin: dict = Depends(require_admin)):
    """Kalendar uchun: [start, end) oralig'idagi barcha bronlar (YYYY-MM-DD)."""
    s = datetime.combine(datetime.strptime(start, "%Y-%m-%d").date(), time(0, 0), tzinfo=TASHKENT)
    e = datetime.combine(datetime.strptime(end, "%Y-%m-%d").date(), time(0, 0), tzinfo=TASHKENT)
    rows = await bookings_repo.list_bookings(s, e)
    return {"items": rows}


@app.post("/api/bookings")
async def create_manual_booking(body: BookingCreate, admin: dict = Depends(require_admin)):
    """Admin qo'lda bron qo'shadi. Yangi mijoz bo'lsa — bazaga qo'shiladi."""
    service = await services_repo.get_service(body.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Xizmat topilmadi")

    # Mijozni aniqlaymiz
    if body.new_client:
        client = await clients_repo.create_manual_client(
            full_name=body.new_client.full_name, phone=body.new_client.phone
        )
    elif body.client_id:
        client = await clients_repo.get_client_by_id(body.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    else:
        raise HTTPException(status_code=400, detail="Mijoz ko'rsatilmagan")

    start = datetime.fromisoformat(body.start_at)
    if start.tzinfo is None:
        start = start.replace(tzinfo=TASHKENT)
    end = start + timedelta(minutes=service["duration"])

    booking = await bookings_repo.create_booking(
        client_id=client["id"], service_id=service["id"],
        start_at=start, end_at=end, price=service["price"], source="manual",
    )
    # Admin qo'shgani uchun darrov tasdiqlangan
    await bookings_repo.update_status(booking["id"], "confirmed")
    return {"ok": True, "booking_id": booking["id"], "client": client}


@app.patch("/api/bookings/{booking_id}")
async def edit_booking(booking_id: int, body: BookingUpdate, admin: dict = Depends(require_admin)):
    booking = await bookings_repo.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Bron topilmadi")

    fields: dict = {}
    if body.status is not None:
        fields["status"] = body.status
    if body.service_id is not None:
        fields["service_id"] = body.service_id
    if body.start_at is not None:
        start = datetime.fromisoformat(body.start_at)
        if start.tzinfo is None:
            start = start.replace(tzinfo=TASHKENT)
        svc_id = body.service_id or booking["service_id"]
        svc = await services_repo.get_service(svc_id)
        dur = svc["duration"] if svc else 40
        fields["start_at"] = start.isoformat()
        fields["end_at"] = (start + timedelta(minutes=dur)).isoformat()

    if not fields:
        raise HTTPException(status_code=400, detail="O'zgartirish yo'q")
    updated = await bookings_repo.update_booking(booking_id, fields)
    return {"ok": True, "booking": updated}


@app.post("/api/bookings/{booking_id}/confirm")
async def confirm_booking(booking_id: int, admin: dict = Depends(require_admin)):
    return await _set_booking_status(booking_id, "confirmed")


@app.post("/api/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int, body: CancelBody | None = None, admin: dict = Depends(require_admin)
):
    custom = body.message if body else None
    return await _set_booking_status(
        booking_id, "cancelled", custom_message=custom, cancelled_by="admin"
    )


async def _set_booking_status(
    booking_id: int, status: str, custom_message: str | None = None, cancelled_by: str | None = None
):
    booking = await bookings_repo.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Bron topilmadi")

    await bookings_repo.update_status(booking_id, status, cancelled_by=cancelled_by)

    client = booking.get("clients") or {}
    service = booking.get("services") or {}
    start = datetime.fromisoformat(booking["start_at"])
    tg_id = client.get("telegram_id")
    if tg_id:
        if custom_message:
            await notify.send_message(tg_id, custom_message)
        elif status == "confirmed":
            await notify.send_message(
                tg_id,
                "✅ <b>Navbatingiz tasdiqlandi!</b>\n\n"
                f"✂️ {service.get('name')}\n"
                f"📅 {fmt_date(start.date())}, 🕐 {fmt_time(start)}\n\nKutib qolamiz! 💈",
            )
        elif status == "cancelled":
            await notify.send_message(
                tg_id,
                "❌ <b>Navbatingiz bekor qilindi.</b>\n\n"
                f"✂️ {service.get('name')}\n"
                f"📅 {fmt_date(start.date())}, 🕐 {fmt_time(start)}\n\n"
                "Boshqa vaqtga yozilishingiz mumkin.",
            )
    return {"ok": True, "status": status}


# ---------- Xizmatlar (CRUD) ----------

@app.get("/api/services")
async def list_services(admin: dict = Depends(require_admin)):
    return {"items": await services_repo.list_all_services()}


@app.post("/api/services")
async def create_service(body: ServiceIn, admin: dict = Depends(require_admin)):
    return await services_repo.create_service(
        name=body.name, price=body.price, duration=body.duration, sort_order=body.sort_order
    )


@app.patch("/api/services/{service_id}")
async def update_service(service_id: int, body: ServiceUpdate, admin: dict = Depends(require_admin)):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="O'zgartirish uchun maydon yo'q")
    updated = await services_repo.update_service(service_id, fields)
    if not updated:
        raise HTTPException(status_code=404, detail="Xizmat topilmadi")
    return updated


@app.delete("/api/services/{service_id}")
async def delete_service(service_id: int, admin: dict = Depends(require_admin)):
    await services_repo.deactivate_service(service_id)
    return {"ok": True}


# ---------- Mijozlar ----------

@app.get("/api/clients")
async def list_clients(q: str | None = None, admin: dict = Depends(require_admin)):
    if q:
        return {"items": await clients_repo.search_clients(q)}
    return {"items": await clients_repo.list_clients()}


@app.post("/api/clients")
async def create_client(body: ClientIn, admin: dict = Depends(require_admin)):
    return await clients_repo.create_manual_client(full_name=body.full_name, phone=body.phone)


# ---------- Broadcast (hamma mijozga xabar) ----------

@app.post("/api/broadcast")
async def broadcast(body: BroadcastIn, admin: dict = Depends(require_admin)):
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Xabar bo'sh")
    clients = await clients_repo.list_clients()
    targets = [c for c in clients if c.get("telegram_id")]
    sent = 0
    for c in targets:
        if await notify.send_message(c["telegram_id"], body.message):
            sent += 1
        await asyncio.sleep(0.05)  # Telegram limitidan oshmaslik uchun
    return {"ok": True, "sent": sent, "total": len(targets)}


# ---------- Ish vaqti ----------

@app.get("/api/working-hours")
async def get_working_hours(admin: dict = Depends(require_admin)):
    return {"items": await working_hours_repo.list_all()}


@app.put("/api/working-hours")
async def put_working_hours(body: WorkingHoursIn, admin: dict = Depends(require_admin)):
    rows = []
    for d in body.days:
        row = d.model_dump()
        # bo'sh vaqtlarni None qilamiz (yopiq kun uchun)
        for k in ("open_time", "close_time", "break_start", "break_end"):
            if not row.get(k):
                row[k] = None
        rows.append(row)
    await working_hours_repo.upsert_days(rows)
    return {"ok": True}


# ---------- Statistika ----------

@app.get("/api/stats")
async def stats(days: int = 30, admin: dict = Depends(require_admin)):
    end = now_tk()
    start = datetime.combine((end - timedelta(days=days)).date(), time(0, 0), tzinfo=TASHKENT)
    rows = await bookings_repo.list_bookings(start, end + timedelta(days=1))

    total = len(rows)
    by_status: dict[str, int] = {}
    revenue = 0
    for b in rows:
        by_status[b["status"]] = by_status.get(b["status"], 0) + 1
        # Daromad FAQAT mijoz kelib xizmatdan foydalangan (completed) bronlardan
        if b["status"] == "completed":
            revenue += b.get("price") or 0

    return {
        "days": days,
        "total_bookings": total,
        "by_status": by_status,
        "revenue": revenue,
        "completed": by_status.get("completed", 0),
        "no_show": by_status.get("no_show", 0),
        "clients_total": len(await clients_repo.list_clients()),
    }
