import React, { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export default function UserProfile() {
  const [me, setMe] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API_BASE}/users/me`, { withCredentials: true })
        setMe(res.data)
      } catch {}
      finally { setLoading(false) }
    }
    load()
  }, [])

  return (
    <div className="max-w-3xl mx-auto">
      <div className="rounded-2xl bg-white text-gray-900 p-6">
        <div className="text-sm uppercase tracking-wide text-primary">Profile</div>
        <h1 className="text-2xl font-bold">My Profile</h1>
        {loading ? (
          <div className="mt-3 p-3 border rounded bg-[#F8FAFF]">Loading profile…</div>
        ) : !me ? (
          <div className="mt-3 p-3 border rounded bg-[#FFF6F6] text-[#8B0000]">Login required to view your profile.</div>
        ) : (
          <div className="mt-4 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <div className="text-sm text-gray-600">Name</div>
                <div className="font-semibold">{me?.name || '-'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Email</div>
                <div className="font-semibold">{me?.email || '-'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Phone</div>
                <div className="font-semibold">{me?.phone || '-'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Account Created</div>
                <div className="font-semibold">{me?.created_at ? new Date(me.created_at).toLocaleString() : '-'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Last Login</div>
                <div className="font-semibold">{me?.last_login_at ? new Date(me.last_login_at).toLocaleString() : '-'}</div>
              </div>
            </div>
            <div className="mt-4">
              <div className="text-sm text-gray-600">Account Settings</div>
              <div className="p-3 border rounded bg-[#F8FAFF]">Customize preferences and privacy (coming soon)</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}