import { useEffect, useState } from 'react'
import { api } from '../api'

const DAYS = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba']

const trim = (t) => (t ? t.slice(0, 5) : '')

function emptyWeek() {
  return Array.from({ length: 7 }, (_, wd) => ({
    weekday: wd, is_open: wd !== 6,
    open_time: '09:00', close_time: '20:00', break_start: '', break_end: '',
  }))
}

export default function WorkingHours() {
  const [days, setDays] = useState(null)
  const [busy, setBusy] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.workingHours().then((r) => {
      const map = {}
      for (const d of r.items) map[d.weekday] = d
      setDays(emptyWeek().map((def) => {
        const d = map[def.weekday]
        return d ? {
          weekday: def.weekday,
          is_open: d.is_open,
          open_time: trim(d.open_time) || '09:00',
          close_time: trim(d.close_time) || '20:00',
          break_start: trim(d.break_start),
          break_end: trim(d.break_end),
        } : def
      }))
    }).catch(() => setDays(emptyWeek()))
  }, [])

  function set(wd, field, val) {
    setDays((ds) => ds.map((d) => (d.weekday === wd ? { ...d, [field]: val } : d)))
    setSaved(false)
  }

  async function save() {
    setBusy(true)
    try {
      await api.saveWorkingHours(days.map((d) => ({
        weekday: d.weekday,
        is_open: d.is_open,
        open_time: d.is_open ? d.open_time : null,
        close_time: d.is_open ? d.close_time : null,
        break_start: d.is_open ? (d.break_start || null) : null,
        break_end: d.is_open ? (d.break_end || null) : null,
      })))
      setSaved(true)
    } finally {
      setBusy(false)
    }
  }

  if (!days) return <div className="center">Yuklanmoqda…</div>

  return (
    <>
      <h1>Ish vaqti</h1>
      <div className="sub">Kun, soat va tushlik. Yopiq vaqtga mijoz bron qila olmaydi.</div>

      {days.map((d) => (
        <div className="card" key={d.weekday}>
          <div className="row">
            <span className="title">{DAYS[d.weekday]}</span>
            <label className="switch">
              <input type="checkbox" checked={d.is_open} onChange={(e) => set(d.weekday, 'is_open', e.target.checked)} />
              <span>{d.is_open ? 'Ish kuni' : 'Dam'}</span>
            </label>
          </div>

          {d.is_open && (
            <>
              <div className="two-col" style={{ marginTop: 8 }}>
                <div>
                  <label>Ochilish</label>
                  <input type="time" value={d.open_time} onChange={(e) => set(d.weekday, 'open_time', e.target.value)} />
                </div>
                <div>
                  <label>Yopilish</label>
                  <input type="time" value={d.close_time} onChange={(e) => set(d.weekday, 'close_time', e.target.value)} />
                </div>
              </div>
              <div className="two-col">
                <div>
                  <label>Tushlik (dan)</label>
                  <input type="time" value={d.break_start} onChange={(e) => set(d.weekday, 'break_start', e.target.value)} />
                </div>
                <div>
                  <label>Tushlik (gacha)</label>
                  <input type="time" value={d.break_end} onChange={(e) => set(d.weekday, 'break_end', e.target.value)} />
                </div>
              </div>
            </>
          )}
        </div>
      ))}

      <button className="btn-primary" style={{ marginTop: 12 }} disabled={busy} onClick={save}>
        {saved ? '✓ Saqlandi' : 'Saqlash'}
      </button>
    </>
  )
}
