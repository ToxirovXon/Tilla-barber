import { useEffect, useState } from 'react'
import { api } from '../api'

const CFG = [
  {
    key: 'reminder', title: '🔔 Eslatma', param: 'hours', unit: 'soat oldin',
    hint: 'Bron vaqtidan necha soat oldin yuborilsin. Belgilar: {time} {service} {name}',
  },
  {
    key: 'retention', title: '🔁 Qaytarish', param: 'days', unit: 'kundan keyin',
    hint: 'Oxirgi tashrifdan necha kun kelmasa yuborilsin. Belgi: {name}',
  },
  {
    key: 'birthday', title: '🎂 Tug\'ilgan kun', param: 'percent', unit: '% chegirma',
    hint: 'Tug\'ilgan kunida avtomatik tabrik. Belgilar: {name} {percent}',
  },
]

export default function Automations() {
  const [s, setS] = useState(null)
  const [busy, setBusy] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => { api.settings().then(setS).catch(() => setS({})) }, [])

  function upd(key, field, val) {
    setS((p) => ({ ...p, [key]: { ...p[key], [field]: val } }))
    setSaved(false)
  }

  async function save() {
    setBusy(true)
    try {
      await api.saveSettings({ reminder: s.reminder, retention: s.retention, birthday: s.birthday })
      setSaved(true)
    } finally { setBusy(false) }
  }

  if (!s) return <div className="center">Yuklanmoqda…</div>

  return (
    <>
      <h1>Avtomatik xabarlar</h1>
      <div className="sub">Biz tomondan yuboriladigan barcha xabarlar shu yerdan boshqariladi.</div>

      {CFG.map(({ key, title, param, unit, hint }) => {
        const c = s[key] || {}
        return (
          <div className="card" key={key}>
            <div className="row">
              <span className="title">{title}</span>
              <label className="switch">
                <input type="checkbox" checked={!!c.enabled} onChange={(e) => upd(key, 'enabled', e.target.checked)} />
                <span>{c.enabled ? 'Yoniq' : 'O\'chiq'}</span>
              </label>
            </div>

            {c.enabled && (
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10 }}>
                  <input type="number" inputMode="numeric" style={{ width: 90 }}
                    value={c[param] ?? ''} onChange={(e) => upd(key, param, +e.target.value)} />
                  <span className="muted">{unit}</span>
                </div>
                <label>Xabar matni</label>
                <textarea rows={3} value={c.text || ''} onChange={(e) => upd(key, 'text', e.target.value)} />
                <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>{hint}</div>
              </>
            )}
          </div>
        )
      })}

      <button className="btn-primary" style={{ marginTop: 12 }} disabled={busy} onClick={save}>
        {saved ? '✓ Saqlandi' : 'Saqlash'}
      </button>
    </>
  )
}
