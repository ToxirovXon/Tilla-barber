import { useEffect, useState } from 'react'
import { api, fmtTime, money } from '../api'

const STATUS_UZ = {
  pending: 'kutilmoqda', confirmed: 'tasdiqlangan',
  cancelled: 'bekor', completed: 'bajarildi', no_show: 'kelmadi',
}

function isoDay(date) {
  // Toshkent kuni (YYYY-MM-DD)
  return date.toLocaleDateString('en-CA', { timeZone: 'Asia/Tashkent' })
}

export default function Bookings() {
  const [offset, setOffset] = useState(0) // 0=bugun, 1=ertaga ...
  const [items, setItems] = useState(null)
  const [busy, setBusy] = useState(false)

  const date = new Date()
  date.setDate(date.getDate() + offset)
  const day = isoDay(date)
  const label = offset === 0 ? 'Bugun' : offset === 1 ? 'Ertaga'
    : date.toLocaleDateString('uz-UZ', { day: 'numeric', month: 'long', weekday: 'long', timeZone: 'Asia/Tashkent' })

  async function load() {
    setItems(null)
    try {
      const r = await api.bookingsForDay(day)
      setItems(r.items)
    } catch { setItems([]) }
  }
  useEffect(() => { load() }, [offset])

  async function act(id, kind) {
    setBusy(true)
    try {
      kind === 'confirm' ? await api.confirm(id) : await api.cancel(id)
      await load()
    } finally { setBusy(false) }
  }

  return (
    <>
      <h1>Bronlar</h1>
      <div className="day-nav">
        <button className="btn-ghost" onClick={() => setOffset(offset - 1)} disabled={offset <= 0}>‹</button>
        <span className="d">{label}</span>
        <button className="btn-ghost" onClick={() => setOffset(offset + 1)}>›</button>
      </div>

      {items === null && <div className="center">Yuklanmoqda…</div>}
      {items?.length === 0 && <div className="center">Bu kunda bron yo'q</div>}

      {items?.map((b) => {
        const c = b.clients || {}
        const s = b.services || {}
        return (
          <div className="card" key={b.id}>
            <div className="row">
              <span className="title">{fmtTime(b.start_at)} · {s.name || '—'}</span>
              <span className={'badge ' + b.status}>{STATUS_UZ[b.status] || b.status}</span>
            </div>
            <div className="muted" style={{ marginTop: 4 }}>
              {c.full_name || '—'} · {c.phone || ''}{c.username ? ' · @' + c.username : ''}
            </div>
            <div className="muted">{money(b.price)} so'm{b.source === 'manual' ? ' · qo\'lda' : ''}</div>
            {b.status === 'pending' && (
              <div className="actions">
                <button className="btn-green btn-sm" disabled={busy} onClick={() => act(b.id, 'confirm')}>✅ Tasdiqlash</button>
                <button className="btn-red btn-sm" disabled={busy} onClick={() => act(b.id, 'cancel')}>❌ Bekor</button>
              </div>
            )}
          </div>
        )
      })}
    </>
  )
}
