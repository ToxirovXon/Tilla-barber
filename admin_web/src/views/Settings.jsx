import { useState } from 'react'
import WorkingHours from './WorkingHours.jsx'
import Automations from './Automations.jsx'

export default function Settings() {
  const [sub, setSub] = useState('hours')
  return (
    <>
      <div className="seg" style={{ marginBottom: 14 }}>
        <button className={sub === 'hours' ? 'on' : ''} onClick={() => setSub('hours')}>Ish vaqti</button>
        <button className={sub === 'auto' ? 'on' : ''} onClick={() => setSub('auto')}>Avtomatik xabarlar</button>
      </div>
      {sub === 'hours' ? <WorkingHours /> : <Automations />}
    </>
  )
}
