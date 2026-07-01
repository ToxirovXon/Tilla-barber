import { useState } from 'react'
import { api } from '../api'

export default function Broadcast({ onClose }) {
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)

  async function send() {
    if (!msg.trim()) return
    setBusy(true)
    try {
      const r = await api.broadcast(msg.trim())
      setResult(r)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="sheet-overlay" onClick={onClose}>
      <div className="sheet" onClick={(e) => e.stopPropagation()}>
        <div className="sheet-handle" />
        <h2>📢 Hammaga xabar</h2>

        {result ? (
          <>
            <div className="center">
              ✅ Yuborildi<br />
              <span className="muted">{result.sent} / {result.total} mijozga yetkazildi</span>
            </div>
            <button className="btn-primary" onClick={onClose}>Yopish</button>
          </>
        ) : (
          <>
            <div className="sub">Telegram'i bor barcha mijozlarga yuboriladi.</div>
            <textarea rows={5} value={msg} onChange={(e) => setMsg(e.target.value)}
              placeholder="Masalan: Assalomu alaykum! Bu hafta soqol olishga 20% chegirma 🎉" />
            <div className="modal-actions">
              <button className="btn-ghost" onClick={onClose}>Bekor</button>
              <button className="btn-primary" disabled={busy || !msg.trim()} onClick={send}>
                {busy ? 'Yuborilmoqda…' : 'Yuborish'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
