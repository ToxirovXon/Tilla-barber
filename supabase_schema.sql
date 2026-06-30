-- ============================================
-- Tilla Barber — baza sxemasi
-- Supabase → SQL Editor → bu kodni qo'yib "Run" bosing
-- ============================================

-- Mijozlar jadvali
create table if not exists clients (
    id          bigint generated always as identity primary key,
    telegram_id bigint unique not null,
    username    text,                       -- Telegram @username (avtomatik olinadi, o'zgarishi mumkin)
    full_name   text   not null,
    phone       text   not null,
    birthday    date,                       -- ixtiyoriy (tug'ilgan kun tabriklari uchun)
    created_at  timestamptz default now()
);

-- Telegram ID bo'yicha tez qidirish uchun indeks
create index if not exists idx_clients_telegram_id on clients (telegram_id);
