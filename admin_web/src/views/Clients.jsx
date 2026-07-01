import { useEffect, useState } from 'react'
import { api, openTelegram } from '../api'
import Broadcast from '../components/Broadcast'

export default function Clients() {
  const [items, setItems] = useState(null)
  const [q, setQ] = useState('')
  const [bcast, setBcast] = useState(false)

  useEffect(() => {
    api.clients().then((r) => setItems(r.items)).catch(() => setItems([]))
  }, [])

  const filtered = items?.filter((c) => {
    if (!q) return true
    const s = (c.full_name + ' ' + (c.phone || '') + ' ' + (c.username || '')).toLowerCase()
    return s.includes(q.toLowerCase())
  })

  return (
    <>
      <h1>Mijozlar {items && <span className="muted">({items.length})</span>}</h1>
      <button className="btn-primary" style={{ marginBottom: 12 }} onClick={() => setBcast(true)}>📢 Hammaga xabar yuborish</button>
      <input placeholder="Qidirish…" value={q} onChange={(e) => setQ(e.target.value)} style={{ marginBottom: 12 }} />
      {bcast && <Broadcast onClose={() => setBcast(false)} />}

      {items === null && <div className="center">Yuklanmoqda…</div>}
      {filtered?.length === 0 && <div className="center">Mijoz topilmadi</div>}

      {filtered?.map((c) => (
        <div className="card" key={c.id}>
          <div className="row">
            <span className="title">{c.full_name}</span>
            {c.username && <a className="tg-link" onClick={() => openTelegram(c.username)}>@{c.username} ↗</a>}
          </div>
          <div className="muted" style={{ marginTop: 4 }}>
            📞 {c.phone}{c.birthday ? ` · 🎂 ${c.birthday}` : ''}
          </div>
        </div>
      ))}
    </>
  )
}
