"""Admin panel backend (FastAPI). Telegram Web App shu API bilan ishlaydi.

Ishga tushirish: uvicorn admin_api.main:app --reload --port 8000
"""
from datetime import datetime, time, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from admin_api import notify
from admin_api.auth import require_admin
from bot.database import bookings_repo, clients_repo, services_repo, working_hours_repo
from bot.utils.tz import TASHKENT, fmt_date, fmt_time
from bot.utils.tz import now as now_tk

app = FastAPI(title="Tilla Barber Admin API")

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


@app.get("/api/bookings/upcoming")
async def bookings_upcoming(days: int = 7, admin: dict = Depends(require_admin)):
    start = now_tk()
    end = datetime.combine((start + timedelta(days=days)).date(), time(0, 0), tzinfo=TASHKENT)
    rows = await bookings_repo.list_bookings(start, end)
    return {"items": rows}


@app.post("/api/bookings/{booking_id}/confirm")
async def confirm_booking(booking_id: int, admin: dict = Depends(require_admin)):
    return await _set_booking_status(booking_id, "confirmed")


@app.post("/api/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: int, admin: dict = Depends(require_admin)):
    return await _set_booking_status(booking_id, "cancelled")


async def _set_booking_status(booking_id: int, status: str):
    booking = await bookings_repo.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Bron topilmadi")

    await bookings_repo.update_status(booking_id, status)

    client = booking.get("clients") or {}
    service = booking.get("services") or {}
    start = datetime.fromisoformat(booking["start_at"])
    tg_id = client.get("telegram_id")
    if tg_id:
        if status == "confirmed":
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
async def list_clients(admin: dict = Depends(require_admin)):
    return {"items": await clients_repo.list_clients()}


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
        if b["status"] in ("confirmed", "completed"):
            revenue += b.get("price") or 0

    return {
        "days": days,
        "total_bookings": total,
        "by_status": by_status,
        "revenue": revenue,
        "clients_total": len(await clients_repo.list_clients()),
    }
