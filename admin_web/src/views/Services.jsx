import { useEffect, useState } from 'react'
import { api, money } from '../api'

const EMPTY = { name: '', price: '', duration: '' }

export default function Services() {
  const [items, setItems] = useState(null)
  const [form, setForm] = useState(null) // null | {id?, name, price, duration}
  const [busy, setBusy] = useState(false)

  async function load() {
    setItems(null)
    try { setItems((await api.services()).items) } catch { setItems([]) }
  }
  useEffect(() => { load() }, [])

  async function save() {
    if (!form.name || !form.price || !form.duration) return
    setBusy(true)
    try {
      const body = { name: form.name, price: +form.price, duration: +form.duration }
      if (form.id) await api.updateService(form.id, body)
      else await api.createService(body)
      setForm(null)
      await load()
    } finally { setBusy(false) }
  }

  async function remove(id) {
    if (!confirm("Bu xizmatni o'chirasizmi?")) return
    await api.deleteService(id)
    await load()
  }

  if (form) {
    return (
      <>
        <h1>{form.id ? 'Xizmatni tahrirlash' : 'Yangi xizmat'}</h1>
        <label>Nomi</label>
        <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Soch olish" />
        <label>Narxi (so'm)</label>
        <input type="number" inputMode="numeric" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} placeholder="50000" />
        <label>Davomiyligi (daqiqa)</label>
        <input type="number" inputMode="numeric" value={form.duration} onChange={(e) => setForm({ ...form, duration: e.target.value })} placeholder="40" />
        <div className="modal-actions">
          <button className="btn-ghost" onClick={() => setForm(null)}>Bekor</button>
          <button className="btn-primary" disabled={busy} onClick={save}>Saqlash</button>
        </div>
      </>
    )
  }

  return (
    <>
      <h1>Xizmatlar</h1>
      <div className="sub">Akam o'zgartira oladi: narx, nom, davomiylik</div>

      {items === null && <div className="center">Yuklanmoqda…</div>}
      {items?.map((s) => (
        <div className="card" key={s.id}>
          <div className="row">
            <span className="title" style={{ opacity: s.is_active ? 1 : 0.45 }}>
              {s.name} {!s.is_active && '(nofaol)'}
            </span>
            <span className="muted">{s.duration} daq</span>
          </div>
          <div className="row" style={{ marginTop: 6 }}>
            <span className="muted">{money(s.price)} so'm</span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn-ghost btn-sm" onClick={() => setForm({ id: s.id, name: s.name, price: s.price, duration: s.duration })}>✏️</button>
              {s.is_active && <button className="btn-ghost btn-sm" style={{ color: 'var(--red)' }} onClick={() => remove(s.id)}>🗑</button>}
            </div>
          </div>
        </div>
      ))}

      <button className="btn-primary" style={{ marginTop: 12 }} onClick={() => setForm({ ...EMPTY })}>+ Yangi xizmat</button>
    </>
  )
}
