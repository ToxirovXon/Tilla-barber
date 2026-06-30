-- ============================================
-- Tilla Barber — Bron tizimi jadvallari
-- Supabase → SQL Editor → qo'yib "Run" bosing
-- ============================================

-- Xizmatlar (admin paneldan boshqariladi)
create table if not exists services (
    id          bigint generated always as identity primary key,
    name        text    not null,
    price       integer not null,          -- so'mda
    duration    integer not null,          -- daqiqada
    is_active   boolean default true,      -- admin o'chirib/yoqib qo'yishi uchun
    sort_order  integer default 0,
    created_at  timestamptz default now()
);

-- Ish vaqti (har hafta kuni uchun). weekday: 0=Dushanba ... 6=Yakshanba
create table if not exists working_hours (
    weekday    smallint primary key check (weekday between 0 and 6),
    is_open    boolean default true,
    open_time  time,
    close_time time
);

-- Bronlar
create table if not exists bookings (
    id          bigint generated always as identity primary key,
    client_id   bigint references clients(id),
    service_id  bigint references services(id),
    start_at    timestamptz not null,       -- bron boshlanishi
    end_at      timestamptz not null,        -- bron tugashi
    status      text default 'pending',      -- pending/confirmed/cancelled/completed/no_show
    source      text default 'bot',          -- bot / manual (% hisobi uchun muhim)
    price       integer,                     -- bron paytidagi narx (keyin o'zgarsa ham saqlanadi)
    note        text,
    created_at  timestamptz default now()
);

create index if not exists idx_bookings_start_at on bookings (start_at);
create index if not exists idx_bookings_client   on bookings (client_id);

-- RLS yoqamiz (faqat secret kalit kira oladi)
alter table services      enable row level security;
alter table working_hours enable row level security;
alter table bookings      enable row level security;
