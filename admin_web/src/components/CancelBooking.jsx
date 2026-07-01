import { useState } from 'react'
import { api, fmtDate, fmtTime } from '../api'

export default function CancelBooking({ booking, onClose, onDone }) {
  const svc = booking.services?.name || 'navbat'
  const when = `${fmtDate(booking.start_at)}, ${fmtTime(booking.start_at)}`
  const hasTg = !!booking.clients?.username || booking.clients?.telegram_id
  const [msg, setMsg] = useState(
    `❌ Hurmatli mijoz, ${when} dagi "${svc}" navbatingiz bekor qilindi. Uzr so'raymiz.`
  )
  const [busy, setBusy] = useState(false)

  async function doCancel() {
    setBusy(true)
    try {
      await api.cancel(booking.id, msg.trim() || null)
      onDone?.()
      onClose()
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="sheet-overlay" onClick={onClose}>
      <div className="sheet" onClick={(e) => e.stopPropagation()}>
        <div className="sheet-handle" />
        <h2>Bronni bekor qilish</h2>
        <div className="muted" style={{ marginBottom: 10 }}>
          {booking.clients?.full_name} · {when}
        </div>

        <label>Mijozga yuboriladigan xabar {hasTg ? '' : '(Telegram\'i yo\'q — yuborilmaydi)'}</label>
        <textarea rows={4} value={msg} onChange={(e) => setMsg(e.target.value)} />

        <div className="modal-actions">
          <button className="btn-ghost" onClick={onClose}>Yopish</button>
          <button className="btn-red" disabled={busy} onClick={doCancel}>Bekor qilish</button>
        </div>
      </div>
    </div>
  )
}
