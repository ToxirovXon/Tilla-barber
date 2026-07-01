import { useEffect, useState } from 'react'
import { api } from './api'
import Bookings from './views/Bookings.jsx'
import Services from './views/Services.jsx'
import Clients from './views/Clients.jsx'
import Stats from './views/Stats.jsx'
import Settings from './views/Settings.jsx'
import AddBooking from './components/AddBooking.jsx'

const TABS = [
  { key: 'bookings', label: 'Bronlar', ico: '📅' },
  { key: 'services', label: 'Xizmatlar', ico: '✂️' },
  { key: 'clients', label: 'Mijozlar', ico: '👥' },
  { key: 'settings', label: 'Sozlama', ico: '⚙️' },
  { key: 'stats', label: 'Statistika', ico: '📊' },
]

export default function App() {
  const [tab, setTab] = useState('bookings')
  const [auth, setAuth] = useState('loading')
  const [err, setErr] = useState('')
  const [addOpen, setAddOpen] = useState(false)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    api.me()
      .then(() => setAuth('ok'))
      .catch((e) => { setAuth('error'); setErr(String(e.message || e)) })
  }, [])

  if (auth === 'loading') return <div className="app"><div className="center">Yuklanmoqda…</div></div>
  if (auth === 'error') {
    return (
      <div className="app">
        <div className="center">🔒 Kirish rad etildi<br /><span className="muted">{err}</span></div>
      </div>
    )
  }

  return (
    <>
      <div className="app">
        {tab === 'bookings' && <Bookings reloadKey={reloadKey} />}
        {tab === 'services' && <Services />}
        {tab === 'clients' && <Clients />}
        {tab === 'settings' && <Settings />}
        {tab === 'stats' && <Stats />}
      </div>

      {/* Har sahifada ko'rinadigan "Bron qo'shish" tugmasi */}
      <button className="fab" onClick={() => setAddOpen(true)} aria-label="Bron qo'shish">+</button>

      {addOpen && (
        <AddBooking
          onClose={() => setAddOpen(false)}
          onCreated={() => { setReloadKey((k) => k + 1); setTab('bookings') }}
        />
      )}

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
