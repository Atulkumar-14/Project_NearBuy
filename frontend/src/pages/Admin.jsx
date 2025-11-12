import React, { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export default function Admin() {
  const [stats, setStats] = useState(null)
  const [showLogin, setShowLogin] = useState(false)
  const [userId, setUserId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API_BASE}/admin/stats`)
        setStats(res.data)
      } catch (e) {
        setShowLogin(true)
      }
    }
    load()
  }, [])

  return (
    <div className="p-4">
      {showLogin && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center">
          <div className="bg-white text-black rounded-2xl p-6 w-full max-w-sm shadow-lg">
            <div className="text-xl font-bold">Admin Login</div>
            {error && <div className="mt-2 text-sm text-red-600">{error}</div>}
            <div className="mt-3 space-y-2">
              <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" placeholder="Admin Username" value={userId} onChange={e=>setUserId(e.target.value)} />
              <input type="password" className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
            </div>
            <div className="mt-4 flex gap-2">
              <button className="px-4 py-2 rounded-lg bg-primary text-white" onClick={async()=>{
                setError('')
                try {
                  const res = await axios.post(`${API_BASE}/auth/admin/login`, { userId, password })
                  const tok = res?.data?.access_token
                  if (tok) {
                    axios.defaults.headers.common['Authorization'] = `Bearer ${tok}`
                    setShowLogin(false)
                    const s = await axios.get(`${API_BASE}/admin/stats`)
                    setStats(s.data)
                  }
                } catch (e) {
                  const status = e?.response?.status
                  if (status === 429) setError('Account locked for 30 minutes due to failed attempts')
                  else setError('Invalid credentials')
                }
              }}>Login</button>
              <button className="px-4 py-2 rounded-lg border" onClick={()=>setShowLogin(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
      {!stats ? (!showLogin ? 'Loading...' : null) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {Object.entries(stats).map(([k,v]) => (
            <div key={k} className="p-4 border rounded">
              <div className="text-sm uppercase text-gray-600">{k}</div>
              <div className="text-2xl font-bold">{v}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
