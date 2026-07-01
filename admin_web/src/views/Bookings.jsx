import { useEffect, useMemo, useState } from 'react'
import { api, fmtTime, openTelegram } from '../api'
import EditBooking from '../components/EditBooking'
import CancelBooking from '../components/CancelBooking'

const WD = ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sha', 'Ya']
const MONTHS = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun', 'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr']
const STATUS = { pending: 'kutilmoqda', confirmed: 'tasdiqlangan', cancelled: 'bekor', completed: 'keldi ✅', no_show: 'kelmadi' }

function statusLabel(b) {
  if (b.status === 'cancelled') {
    const who = b.cancelled_by === 'client' ? 'mijoz' : b.cancelled_by === 'admin' ? 'admin' : ''
    return who ? `bekor · ${who}` : 'bekor'
  }
  return STATUS[b.status] || b.status
}

const iso = (y, m, d) => `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
const todayIso = () => new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Tashkent' })
const tashDay = (dt) => new Date(dt).toLocaleDateString('en-CA', { timeZone: 'Asia/Tashkent' })

export default function Bookings({ reloadKey }) {
  const [year, setYear] = useState(() => +todayIso().slice(0, 4))
  const [month, setMonth] = useState(() => +todayIso().slice(5, 7) - 1)
  const [selected, setSelected] = useState(todayIso())
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [edit, setEdit] = useState(null)
  const [cancel, setCancel] = useState(null)

  async function load() {
    setLoading(true)
    const start = iso(year, month, 1)
    const next = month === 11 ? iso(year + 1, 0, 1) : iso(year, month + 1, 1)
    try {
      setItems((await api.bookingsRange(start, next)).items)
    } catch {
      setItems([])
    }
    setLoading(false)
  }
  useEffect(() => { load() }, [year, month, reloadKey])

  const counts = useMemo(() => {
    const m = {}
    for (const b of items) {
      if (b.status === 'cancelled') continue
      const d = tashDay(b.start_at)
      m[d] = (m[d] || 0) + 1
    }
    return m
  }, [items])

  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstWd = (new Date(year, month, 1).getDay() + 6) % 7
  const cells = [...Array(firstWd).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)]

  const dayItems = items
    .filter((b) => tashDay(b.start_at) === selected)
    .sort((a, b) => a.start_at.localeCompare(b.start_at))

  const prev = () => (month === 0 ? (setYear(year - 1), setMonth(11)) : setMonth(month - 1))
  const next = () => (month === 11 ? (setYear(year + 1), setMonth(0)) : setMonth(month + 1))
  const mark = (id, status) => api.editBooking(id, { status }).then(load)

  return (
    <>
      <h1>Bronlar</h1>
      <div className="cal-head">
        <button className="btn-ghost" onClick={prev}>‹</button>
        <span className="cal-title">{MONTHS[month]} {year}</span>
        <button className="btn-ghost" onClick={next}>›</button>
      </div>

      <div className="cal-grid">
        {WD.map((w) => <div key={w} className="cal-wd">{w}</div>)}
        {cells.map((d, i) => {
          if (d === null) return <div key={i} />
          const dIso = iso(year, month, d)
          const cnt = counts[dIso] || 0
          return (
            <button
              key={i}
              className={'cal-cell' + (dIso === selected ? ' sel' : '') + (dIso === todayIso() ? ' today' : '')}
              onClick={() => setSelected(dIso)}
            >
              <span>{d}</span>
              {cnt > 0 && <span className="cal-dot">{cnt}</span>}
            </button>
          )
        })}
      </div>

      <div className="day-title">{selected === todayIso() ? 'Bugun' : selected}</div>
      {loading && <div className="center">Yuklanmoqda…</div>}
      {!loading && dayItems.length === 0 && <div className="center">Bu kunda bron yo'q</div>}

      {dayItems.map((b) => {
        const c = b.clients || {}
        const s = b.services || {}
        return (
          <div className="card" key={b.id}>
            <div className="row">
              <span className="title">{fmtTime(b.start_at)} · {s.name || '—'}</span>
              <span className={'badge ' + b.status}>{statusLabel(b)}</span>
            </div>
            <div className="muted" style={{ marginTop: 4 }}>
              {c.full_name || '—'}{c.phone ? ' · ' + c.phone : ''}
              {c.username && <> · <a className="tg-link" onClick={() => openTelegram(c.username)}>@{c.username}</a></>}
              {b.source === 'manual' ? ' · qo\'lda' : ''}
            </div>
            {(b.status === 'pending' || b.status === 'confirmed') && (
              <div className="actions">
                {b.status === 'pending' && (
                  <button className="btn-green btn-sm" onClick={() => api.confirm(b.id).then(load)}>✅ Tasdiq</button>
                )}
                {b.status === 'confirmed' && (
                  <>
                    <button className="btn-green btn-sm" onClick={() => mark(b.id, 'completed')}>✅ Keldi</button>
                    <button className="btn-ghost btn-sm" onClick={() => mark(b.id, 'no_show')}>🚫 Kelmadi</button>
                  </>
                )}
                <button className="btn-ghost btn-sm" onClick={() => setEdit(b)}>✏️</button>
                <button className="btn-ghost btn-sm" style={{ color: 'var(--red)' }} onClick={() => setCancel(b)}>❌</button>
              </div>
            )}
          </div>
        )
      })}

      {edit && <EditBooking booking={edit} onClose={() => setEdit(null)} onSaved={load} />}
      {cancel && <CancelBooking booking={cancel} onClose={() => setCancel(null)} onDone={load} />}
    </>
  )
}
