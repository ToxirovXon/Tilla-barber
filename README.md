# Tilla Barber — Telegram bot

Sartaroshxona uchun bron + CRM + shop boti va admin panel.
To'liq tavsif: [TZ.md](TZ.md)

## Texnologiyalar
- Python 3.12 + Aiogram 3
- Supabase (PostgreSQL)
- Admin panel: Telegram Web App (React) — keyingi bosqich
- To'lov: Payme + Click — keyingi bosqich

## Lokal ishga tushirish

```bash
# 1. Virtual muhit yaratish
python -m venv venv

# 2. Muhitni faollashtirish (Windows PowerShell)
venv\Scripts\Activate.ps1

# 3. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 4. Sozlamalar
#    .env.example dan nusxa olib .env yarating va to'ldiring
copy .env.example .env

# 5. Botni ishga tushirish
python -m bot
```

## Holat
- [x] Loyiha skeleti, /start
- [x] Mijoz ro'yxatdan o'tishi (ism, tel, tug'ilgan kun) + Supabase
- [x] Mijoz tomoni bron: xizmat → kun → vaqt → tasdiq → adminga xabar
- [x] Admin bronni tasdiqlash/bekor qilish (+ mijoz o'zi bekor qilishi)
- [ ] Admin panel (Telegram Web App)
- [ ] To'lov (Payme/Click)
