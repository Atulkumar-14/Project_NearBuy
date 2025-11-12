import React, { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export default function Admin() {
  const [stats, setStats] = useState(null)
  useEffect(() => {
    const load = async () => {
      const res = await axios.get(`${API_BASE}/admin/stats`)
      setStats(res.data)
    }
    load()
  }, [])

  return (
    <div className="p-4">
      {!stats ? 'Loading...' : (
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