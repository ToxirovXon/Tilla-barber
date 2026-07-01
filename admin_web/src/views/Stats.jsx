import { useEffect, useState } from 'react'
import { api, money } from '../api'

export default function Stats() {
  const [data, setData] = useState(null)
  const [days, setDays] = useState(30)

  useEffect(() => {
    setData(null)
    api.stats(days).then(setData).catch(() => setData(false))
  }, [days])

  return (
    <>
      <h1>Statistika</h1>
      <div className="sub">Oxirgi {days} kun</div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
        {[7, 30, 90].map((d) => (
          <button key={d} className={d === days ? 'btn-primary btn-sm' : 'btn-ghost btn-sm'}
            style={{ flex: 1 }} onClick={() => setDays(d)}>{d} kun</button>
        ))}
      </div>

      {data === null && <div className="center">Yuklanmoqda…</div>}
      {data === false && <div className="center">Xatolik</div>}

      {data && (
        <>
          <div className="stat-grid">
            <div className="stat">
              <div className="num">{money(data.revenue)}</div>
              <div className="lbl">Daromad (so'm)*</div>
            </div>
            <div className="stat">
              <div className="num">{data.total_bookings}</div>
              <div className="lbl">Jami bron</div>
            </div>
            <div className="stat">
              <div className="num">{data.completed || 0}</div>
              <div className="lbl">Keldi (bajarildi)</div>
            </div>
            <div className="stat">
              <div className="num">{data.clients_total}</div>
              <div className="lbl">Mijozlar bazasi</div>
            </div>
          </div>
          <div className="muted" style={{ marginTop: 12, fontSize: 12 }}>
            * Daromad faqat mijoz kelib xizmatdan foydalangan («Keldi») bronlardan hisoblanadi
          </div>
        </>
      )}
    </>
  )
}
