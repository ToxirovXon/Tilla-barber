# Tilla Barber — Bot Texnik Topshiriq (TZ)

> Versiya: 0.2 · Sana: 2026-06-30
> Loyiha: Telegram bot + admin panel, "Tilla Barber" sartaroshxonasi uchun (beta), keyin mahsulot sifatida boshqalarga sotiladi.

---

## 1. Maqsad

Sartaroshxona uchun Telegram bot:
1. Mijoz bazasini yig'ish va qayta-qayta ishlatish (CRM + retention)
2. Bron tizimi (karta orqali to'lov, depozit, no-show himoyasi)
3. Kontent (akam post yuboradi → kanalga chiqadi)
4. Shop (pre-order, 100% oldindan to'lov, zaxirasiz)
5. Akam uchun qulay admin panel (Telegram Web App)

---

## 2. Biznes modeli

- **Beta:** 1-3 oy tekin o'rnatish va sinov.
- **Keyin:** bot orqali kelgan bronlardan **10%**.
- Bot orqali bron **faqat karta** (Payme/Click) — naqd emas.
- Akam qo'lda kiritgan bronlar (keksalar, offline) — **%siz**, akamga to'liq.
- **Kassa akamning nomiga** — pul akamga tushadi.
- **Hisob-kitob:** bot har tranzaksiyani yozadi (haqiqat manbai = bot). Oy oxirida bot
  jami daromad va foydalanuvchining 10%ini avtomatik hisoblaydi → akam oyiga 1 marta o'tkazadi.
  Raqam admin panel "Statistika"da ochiq turadi.
- Mijoz bazasi — loyiha mulki; ikki tomon roziligisiz uchinchi shaxsga berilmaydi.

---

## 3. Mijoz tomoni (oddiy bot)

### 3.1 Bron
- **Xizmatlar admin paneldan boshqariladi** (akam qo'shadi/o'chiradi/narx o'zgartiradi — ro'yxat dinamik)
- Xizmat tanlash → usta tanlash (master jadval) → bo'sh vaqt tanlash
- To'lov: Payme/Click karta orqali (deposit yoki to'liq)
- **Depozit:** boshида 20-30k so'm (vaqt o'tishi bilan yoqiladi, darrov emas)
- Depozit qaytmaydi, agar mijoz kelmasa
- **No-show qoidasi:** 2 marta atmen/kelmaslik → keyingi safar 100% oldindan to'lov
- Brondan oldin eslatma (masalan 2 soat oldin)

### 3.2 Shop (pre-order)
- Katalog (akam to'ldiradi): rasm, narx, tavsif
- Zaxira yo'q — mijoz 100% to'laydi, akam 1-3 kun ichида olib keladi
- "3 kun kafolat, topilmasa to'liq qaytariladi"
- Status: kutish → yo'lda → yetdi
- Sartaroshxonadan olib ketish (yetkazib berish keyinги bosqich)

### 3.3 Mijoz profili — "sog'liq varaqasi"
- Tashrif tarixi: qachon, qaysi usta, qaysi xizmat
- Xaridlar tarixi (shop)
- Segment: yangi / doimiy / yo'qolgan / VIP / risk (no-show)
- Bonus / chegirma holati

### 3.4 Avtomatik mexanizmlar
- **Retention:** 30-40 kun kelmasa → "qaytib keling, -10%" xabari
- **Tug'ilgan kun:** o'sha kuni avtomatik tabrik + chegirma
- **Feedback:** xizmatdan keyin baho so'rash
  - 5 yulduz → "do'stlaringizga ulashing" (referal)
  - 1-3 yulduz → akamga **maxfiy**, kanalga chiqmaydi
- **Band vaqt psixologiyasi:** "bugun N joy qoldi" ko'rsatish

---

## 4. Akam tomoni — Admin panel (Telegram Web App)

Telefonda bot ichidan ochiladigan web panel. Bo'limlar:

- **🗓 Grafik:** ish vaqti sozlash, kun yopish, dam olish
- **➕ Qo'lda bron:** keksalar/offline mijozlar uchun vaqt band qilish (%siz)
- **👥 Mijozlar (CRM):** baza, qidiruv, sog'liq varaqasi, segmentlar
- **📤 Broadcast:** tanlangan segment yoki hammaga uvedomleniye yuborish
- **🛒 Shop boshqaruv:** mahsulot qo'shish/o'chirish, narx, kelgan zakazlar
- **📊 Statistika:** daromad, mijoz oqimi, eng band kunlar, yangi/yo'qolgan
- **⭐ Feedback:** sharhlar, reyting, past bahоlar
- **📊 Kunlik hisobot:** har kuni kechqurun avtomatik (mijoz soni, daromad, ertangi bronlar)

---

## 5. Texnik stack

| Qatlam | Texnologiya |
|---|---|
| Bot | Python + Aiogram 3 |
| Admin panel | Telegram Web App (React + Vite) |
| Backend API | FastAPI (yoki bot bilan birga) |
| Baza | Supabase (PostgreSQL) |
| To'lov | Payme API + Click API |
| Hosting | Railway / Render |

---

## 6. Bosqichlar (MVP → keyin)

### MVP (1-versiya) — eng zarur
- [ ] Mijoz ro'yxatdan o'tishi (ism, tel, tug'ilgan kun)
- [ ] Bron: xizmat → vaqt → karta to'lov (Payme/Click)
- [ ] Depozit + no-show qoidasi
- [ ] Akam admin panel: grafik, qo'lda bron, mijozlar ro'yxati
- [ ] Kunlik hisobot akamga

### Faza 2
- [ ] Shop (pre-order)
- [ ] Retention + tug'ilgan kun avtomatikasi
- [ ] Feedback + reyting
- [ ] Broadcast
- [ ] Statistika dashboard

### Faza 3 (mahsulotga aylantirish)
- [ ] Ko'p sartaroshxona (multi-tenant)
- [ ] Yetkazib berish
- [ ] Boshqa sartaroshlarga sotish

---

## 7. Qarorlar (qulflandi)
- [x] Nom: **Tilla Barber** · bot username — keyin aniqlanadi (`@tillabarber_bot` band bo'lmasa)
- [x] **10%** — bot bronlaridan
- [x] Kassa **akamning nomiga**; hisob-kitob oyiga 1 marta, bot ma'lumoti asosida
- [x] Xizmatlar **admin paneldan** boshqariladi (dinamik, akam qo'shadi)

## 8. Ma'lum to'siqlar
- Payme/Click merchant ochish akamning biznes hujjatlari + shartnoma talab qiladi (vaqt oladi).
  Strategiya: bron + admin panel avval quriladi (to'lovsiz rejim), credentials kelganda ulanadi.
