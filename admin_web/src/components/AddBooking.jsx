import { useEffect, useState } from 'react'
import { api, money } from '../api'

// Toshkent "bugun" YYYY-MM-DD
function todayIso() {
  return new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Tashkent' })
}

export default function AddBooking({ onClose, onCreated }) {
  const [services, setServices] = useState([])
  const [serviceId, setServiceId] = useState('')
  const [date, setDate] = useState(todayIso())
  const [tm, setTm] = useState('10:00')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  // mijoz: mavjud (search) yoki yangi
  const [mode, setMode] = useState('search') // search | new
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [picked, setPicked] = useState(null)
  const [newName, setNewName] = useState('')
  const [newPhone, setNewPhone] = useState('')

  useEffect(() => {
    api.services().then((r) => {
      const active = r.items.filter((s) => s.is_active)
      setServices(active)
      if (active[0]) setServiceId(String(active[0].id))
    })
  }, [])

  useEffect(() => {
    if (mode !== 'search' || q.trim().length < 2) { setResults([]); return }
    const t = setTimeout(() => {
      api.searchClients(q.trim()).then((r) => setResults(r.items)).catch(() => setResults([]))
    }, 300)
    return () => clearTimeout(t)
  }, [q, mode])

  async function save() {
    setErr('')
    if (!serviceId) return setErr('Xizmat tanlang')
    const body = {
      service_id: +serviceId,
      start_at: `${date}T${tm}:00+05:00`,
    }
    if (mode === 'search') {
      if (!picked) return setErr('Mijozni tanlang yoki yangi qo\'shing')
      body.client_id = picked.id
    } else {
      if (!newName.trim() || !newPhone.trim()) return setErr('Ism va telefon kiriting')
      body.new_client = { full_name: newName.trim(), phone: newPhone.trim() }
    }
    setBusy(true)
    try {
      await api.createBooking(body)
      onCreated?.()
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
        <h2>Yangi bron</h2>

        {/* Mijoz */}
        <div className="seg">
          <button className={mode === 'search' ? 'on' : ''} onClick={() => setMode('search')}>Mavjud mijoz</button>
          <button className={mode === 'new' ? 'on' : ''} onClick={() => setMode('new')}>Yangi mijoz</button>
        </div>

        {mode === 'search' ? (
          picked ? (
            <div className="card row">
              <span className="title">{picked.full_name} <span className="muted">{picked.phone}</span></span>
              <button className="btn-ghost btn-sm" onClick={() => setPicked(null)}>o'zgartir</button>
            </div>
          ) : (
            <>
              <input placeholder="Ism yoki telefon bo'yicha qidiring…" value={q} onChange={(e) => setQ(e.target.value)} />
              {results.map((r) => (
                <div className="card row" key={r.id} onClick={() => { setPicked(r); setResults([]); setQ('') }} style={{ cursor: 'pointer' }}>
                  <span className="title">{r.full_name}</span>
                  <span className="muted">{r.phone}</span>
                </div>
              ))}
            </>
          )
        ) : (
          <>
            <label>Ism familiya</label>
            <input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Ism familiya" />
            <label>Telefon</label>
            <input value={newPhone} onChange={(e) => setNewPhone(e.target.value)} placeholder="+998..." />
          </>
        )}

        {/* Xizmat */}
        <label>Xizmat</label>
        <select value={serviceId} onChange={(e) => setServiceId(e.target.value)}>
          {services.map((s) => (
            <option key={s.id} value={s.id}>{s.name} — {money(s.price)} so'm ({s.duration} daq)</option>
          ))}
        </select>

        {/* Sana / vaqt */}
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
          <button className="btn-primary" disabled={busy} onClick={save}>Bron qo'shish</button>
        </div>
      </div>
    </div>
  )
}
