import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function ShopkeeperProfile() {
  const [owner, setOwner] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const run = async () => {
      try {
        const res = await axios.get(`${API_BASE}/owners/me`)
        setOwner(res.data)
      } catch (e) {
        console.error('Failed to load owner profile', e)
      } finally { setLoading(false) }
    }
    run()
  }, [])

  return (
    <div className="max-w-3xl mx-auto">
      <div className="rounded-2xl bg-white text-gray-900 p-6">
        <div className="text-sm uppercase tracking-wide text-accent">Business Profile</div>
        <h1 className="text-2xl font-bold">Shopkeeper Profile</h1>
        {loading ? (
          <div className="mt-3 p-3 border rounded bg-[#F8FAFF]">Loading profile…</div>
        ) : !owner ? (
          <div className="mt-3 p-3 border rounded bg-[#FFF6F6] text-[#8B0000]">Login required to view business profile.</div>
        ) : (
          <div className="mt-4 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <div className="text-sm text-gray-600">Owner Name</div>
                <div className="font-semibold">{owner?.owner_name || '-'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Email</div>
                <div className="font-semibold">{owner?.email || '-'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Phone</div>
                <div className="font-semibold">{owner?.phone || '-'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Account Created</div>
                <div className="font-semibold">{owner?.created_at ? new Date(owner.created_at).toLocaleString() : '-'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Last Login</div>
                <div className="font-semibold">{owner?.last_login_at ? new Date(owner.last_login_at).toLocaleString() : '-'}</div>
              </div>
            </div>
          <div className="mt-4">
              <div className="text-sm text-gray-600">My Shops</div>
              {owner?.shops?.length ? (
                <ul className="mt-2 space-y-2">
                  {owner.shops.map((s) => (
                    <li key={s.shop_id} className="p-3 border rounded bg-[#F8FAFF] flex items-center justify-between">
                      <div>
                        <div className="font-semibold">{s.shop_name}</div>
                        <div className="text-xs text-gray-600">Shop ID: {s.shop_id}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Link to={`/shops/${s.shop_id}`} className="px-3 py-1 rounded border bg-white text-black">View</Link>
                        <Link to={`/shops/${s.shop_id}/manage`} className="px-3 py-1 rounded border bg-white text-black font-semibold">Manage</Link>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="p-3 border rounded bg-[#F8FAFF]">No shops linked to your account yet.</div>
              )}
          </div>
          </div>
        )}
      </div>
    </div>
  )
}