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
  confirm: (id) => req(`/api/bookings/${id}/confirm`, { method: 'POST' }),
  cancel: (id) => req(`/api/bookings/${id}/cancel`, { method: 'POST' }),
  services: () => req('/api/services'),
  createService: (b) => req('/api/services', { method: 'POST', body: JSON.stringify(b) }),
  updateService: (id, b) => req(`/api/services/${id}`, { method: 'PATCH', body: JSON.stringify(b) }),
  deleteService: (id) => req(`/api/services/${id}`, { method: 'DELETE' }),
  clients: () => req('/api/clients'),
  stats: (days = 30) => req(`/api/stats?days=${days}`),
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
