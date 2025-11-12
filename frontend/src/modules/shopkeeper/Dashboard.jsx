import React from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function ShopkeeperDashboard() {
  const navigate = useNavigate()
  const ownerToken = localStorage.getItem('owner_token')
  const quickActions = [
    { label: 'Add Product', to: '/shops/add-product' },
    { label: 'Manage Shop', to: '/shops/10001/manage' }, // Replace with actual shop selection flow
    { label: 'Register Shop', to: '/shops/register' },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="rounded-2xl bg-white text-gray-900 p-6">
        <div className="text-sm uppercase tracking-wide text-accent">Shop Management</div>
        <h1 className="text-3xl font-bold mt-1">Shopkeeper Dashboard</h1>
        <p className="mt-2 text-gray-700">Access inventory, products, and orders. Only authenticated shopkeepers can access these tools.</p>

        {!ownerToken && (
          <div className="mt-4 p-3 border rounded bg-[#FFF6F6] text-[#8B0000]">
            You are not logged in as a shopkeeper. <Link to="/owner/login" className="text-primary underline">Login</Link>
          </div>
        )}

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-3">
          {quickActions.map((a) => (
            <button key={a.label} onClick={() => navigate(a.to)} className="p-4 rounded-xl border bg-[#F8FAFF] text-black hover:bg-[#F3F6FF]">
              <div className="font-semibold">{a.label}</div>
              <div className="text-sm text-gray-600">Go to {a.label.toLowerCase()} page</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}