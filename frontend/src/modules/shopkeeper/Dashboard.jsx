import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
const API_BASE = 'http://localhost:8000/api'
import { useAuth } from '../../components/AuthProvider.jsx'

export default function ShopkeeperDashboard() {
  const navigate = useNavigate()
  const { owner, loading } = useAuth()
  const [shops, setShops] = useState([])
  useEffect(() => {
    if (owner) {
      axios.get(`${API_BASE}/owners/me`, { withCredentials: true }).then((res) => {
        const arr = Array.isArray(res.data?.shops) ? res.data.shops : []
        const unique = [...new Map(arr.map(s => [s.shop_id, s])).values()]
        setShops(unique)
      }).catch(() => {})
    }
  }, [owner])
  const quickActions = [
    { label: 'Add Product', to: '/shops/add-product' },
    { label: 'Manage Products', to: '/shopkeeper/products' },
    { label: 'Register Shop', to: '/shops/register' },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="rounded-2xl bg-white text-gray-900 p-6">
        <div className="text-sm uppercase tracking-wide text-accent">Shop Management</div>
        <h1 className="text-3xl font-bold mt-1">Shopkeeper Dashboard</h1>
        <p className="mt-2 text-gray-700">Access inventory, products, and orders. Only authenticated shopkeepers can access these tools.</p>

        {!owner && !loading && (
          <div className="mt-4 p-3 border rounded bg-[#FFF6F6] text-[#8B0000]">
            You are not logged in as a shopkeeper. <Link to="/owner/login" className="text-primary underline">Login</Link>
          </div>
        )}
        {loading && (
          <div className="mt-4 p-3 border rounded bg-[#F8FAFF] text-black">Loading session…</div>
        )}

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-3">
          {quickActions.map((a) => (
            <button key={a.label} onClick={() => navigate(a.to)} className="p-4 rounded-xl border bg-[#F8FAFF] text-black hover:bg-[#F3F6FF]">
              <div className="font-semibold">{a.label}</div>
              <div className="text-sm text-gray-600">Go to {a.label.toLowerCase()} page</div>
            </button>
          ))}
        </div>

        {owner && shops.length > 0 && (
          <div className="mt-8">
            <div className="text-sm uppercase tracking-wide text-accent">Your Shops</div>
            <ul className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
              {shops.map((s) => (
                <li key={s.shop_id} className="p-3 rounded-xl border bg-[#F8FAFF] text-black">
                  <div className="font-semibold">{s.shop_name}</div>
                  <div className="text-sm text-gray-600">{s.city || 'Unknown city'}</div>
                  <div className="mt-2 flex gap-2">
                    <button className="px-3 py-1 rounded-lg border" onClick={() => navigate(`/shops/${s.shop_id}/add-product`)}>Add Product</button>
                    <button className="px-3 py-1 rounded-lg border" onClick={() => navigate('/shopkeeper/products')}>Manage Products</button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
