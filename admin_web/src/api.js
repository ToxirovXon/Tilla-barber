// Backend bilan ishlash. Telegram initData'ni Authorization sarlavhasida yuboramiz.
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Telegram ichida — haqiqiy initData; brauzerda dev uchun — .env.local dagi qiymat
const initData =
  window.Telegram?.WebApp?.initData || import.meta.env.VITE_DEV_INIT_DATA || ''

async function req(path, options = {}) {
  const res = await fetch(API + path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'tma ' + initData,
      ...(options.headers || {}),
    },
  })
  if (!res.ok) {
    let detail = res.status
    try {
      detail = (await res.json()).detail || detail
    } catch {}
    throw new Error(detail)
  }
  return res.json()
}

export const api = {
  me: () => req('/api/me'),
  bookingsForDay: (day) => req('/api/bookings' + (day ? `?day=${day}` : '')),
  bookingsRange: (start, end) => req(`/api/bookings/range?start=${start}&end=${end}`),
  createBooking: (b) => req('/api/bookings', { method: 'POST', body: JSON.stringify(b) }),
  editBooking: (id, b) => req(`/api/bookings/${id}`, { method: 'PATCH', body: JSON.stringify(b) }),
  confirm: (id) => req(`/api/bookings/${id}/confirm`, { method: 'POST' }),
  cancel: (id, message) =>
    req(`/api/bookings/${id}/cancel`, { method: 'POST', body: JSON.stringify({ message: message || null }) }),
  services: () => req('/api/services'),
  createService: (b) => req('/api/services', { method: 'POST', body: JSON.stringify(b) }),
  updateService: (id, b) => req(`/api/services/${id}`, { method: 'PATCH', body: JSON.stringify(b) }),
  deleteService: (id) => req(`/api/services/${id}`, { method: 'DELETE' }),
  clients: () => req('/api/clients'),
  searchClients: (q) => req(`/api/clients?q=${encodeURIComponent(q)}`),
  createClient: (b) => req('/api/clients', { method: 'POST', body: JSON.stringify(b) }),
  stats: (days = 30) => req(`/api/stats?days=${days}`),
  workingHours: () => req('/api/working-hours'),
  saveWorkingHours: (days) => req('/api/working-hours', { method: 'PUT', body: JSON.stringify({ days }) }),
}

// Mijozning Telegram chatini ochish (username bo'yicha)
export function openTelegram(username) {
  if (!username) return
  const url = `https://t.me/${username}`
  const tg = window.Telegram?.WebApp
  if (tg?.openTelegramLink) tg.openTelegramLink(url)
  else window.open(url, '_blank')
}

// --- Vaqt/sana formatlash (Toshkent) ---
export function fmtTime(iso) {
  return new Date(iso).toLocaleTimeString('en-GB', {
    hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Tashkent',
  })
}

export function fmtDate(iso) {
  return new Date(iso).toLocaleDateString('uz-UZ', {
    day: 'numeric', month: 'long', weekday: 'short', timeZone: 'Asia/Tashkent',
  })
}

export function money(v) {
  return (v || 0).toLocaleString('ru-RU').replace(/,/g, ' ')
}
