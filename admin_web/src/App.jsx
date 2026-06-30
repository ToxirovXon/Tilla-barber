import { useEffect, useState } from 'react'
import { api } from './api'
import Bookings from './views/Bookings.jsx'
import Services from './views/Services.jsx'
import Clients from './views/Clients.jsx'
import Stats from './views/Stats.jsx'

const TABS = [
  { key: 'bookings', label: 'Bronlar', ico: '📅', view: Bookings },
  { key: 'services', label: 'Xizmatlar', ico: '✂️', view: Services },
  { key: 'clients', label: 'Mijozlar', ico: '👥', view: Clients },
  { key: 'stats', label: 'Statistika', ico: '📊', view: Stats },
]

export default function App() {
  const [tab, setTab] = useState('bookings')
  const [auth, setAuth] = useState('loading') // loading | ok | error
  const [err, setErr] = useState('')

  useEffect(() => {
    api.me()
      .then(() => setAuth('ok'))
      .catch((e) => { setAuth('error'); setErr(String(e.message || e)) })
  }, [])

  if (auth === 'loading') return <div className="app"><div className="center">Yuklanmoqda…</div></div>
  if (auth === 'error') {
    return (
      <div className="app">
        <div className="center">
          🔒 Kirish rad etildi<br />
          <span className="muted">{err}</span>
        </div>
      </div>
    )
  }

  const Active = TABS.find((t) => t.key === tab).view

  return (
    <>
      <div className="app">
        <Active />
      </div>
      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={'tab' + (tab === t.key ? ' active' : '')}
            onClick={() => setTab(t.key)}
          >
            <span className="ico">{t.ico}</span>
            {t.label}
          </button>
        ))}
      </nav>
    </>
  )
}
