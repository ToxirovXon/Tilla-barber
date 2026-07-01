import { useEffect, useState } from 'react'
import { api, money } from '../api'

function tashDate(iso) {
  return new Date(iso).toLocaleDateString('en-CA', { timeZone: 'Asia/Tashkent' })
}
function tashTime(iso) {
  return new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Tashkent' })
}

export default function EditBooking({ booking, onClose, onSaved }) {
  const [services, setServices] = useState([])
  const [serviceId, setServiceId] = useState(String(booking.service_id))
  const [date, setDate] = useState(tashDate(booking.start_at))
  const [tm, setTm] = useState(tashTime(booking.start_at))
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  useEffect(() => {
    api.services().then((r) => setServices(r.items.filter((s) => s.is_active)))
  }, [])

  async function save() {
    setBusy(true)
    setErr('')
    try {
      await api.editBooking(booking.id, {
        service_id: +serviceId,
        start_at: `${date}T${tm}:00+05:00`,
      })
      onSaved?.()
      onClose()
    } catch (e) {
      setErr(String(e.message || e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="sheet-overlay" onClick={onClose}>
      <div className="sheet" onClick={(e) => e.stopPropagation()}>
        <div className="sheet-handle" />
        <h2>Bronni tahrirlash</h2>
        <div className="muted" style={{ marginBottom: 10 }}>{booking.clients?.full_name}</div>

        <label>Xizmat</label>
        <select value={serviceId} onChange={(e) => setServiceId(e.target.value)}>
          {services.map((s) => (
            <option key={s.id} value={s.id}>{s.name} — {money(s.price)} so'm</option>
          ))}
        </select>

        <div className="two-col">
          <div>
            <label>Sana</label>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div>
            <label>Vaqt</label>
            <input type="time" value={tm} onChange={(e) => setTm(e.target.value)} />
          </div>
        </div>

        {err && <div className="err">{err}</div>}
        <div className="modal-actions">
          <button className="btn-ghost" onClick={onClose}>Bekor</button>
          <button className="btn-primary" disabled={busy} onClick={save}>Saqlash</button>
        </div>
      </div>
    </div>
  )
}
