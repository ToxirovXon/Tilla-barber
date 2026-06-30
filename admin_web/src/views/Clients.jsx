import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Clients() {
  const [items, setItems] = useState(null)
  const [q, setQ] = useState('')

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
      <input placeholder="Qidirish…" value={q} onChange={(e) => setQ(e.target.value)} style={{ marginBottom: 12 }} />

      {items === null && <div className="center">Yuklanmoqda…</div>}
      {filtered?.length === 0 && <div className="center">Mijoz topilmadi</div>}

      {filtered?.map((c) => (
        <div className="card" key={c.id}>
          <div className="row">
            <span className="title">{c.full_name}</span>
            {c.username && <span className="muted">@{c.username}</span>}
          </div>
          <div className="muted" style={{ marginTop: 4 }}>
            📞 {c.phone}{c.birthday ? ` · 🎂 ${c.birthday}` : ''}
          </div>
        </div>
      ))}
    </>
  )
}
