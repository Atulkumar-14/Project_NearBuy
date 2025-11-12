import React from 'react'
import { useAuth } from '../../components/AuthProvider.jsx'

export default function UserDashboard() {
  const { user, loading } = useAuth()

  return (
    <div className="max-w-4xl mx-auto">
      <div className="rounded-2xl bg-white text-gray-900 p-6">
        <div className="text-sm uppercase tracking-wide text-primary">User Management</div>
        <h1 className="text-3xl font-bold mt-1">User Dashboard</h1>
        <p className="mt-2 text-gray-700">Personalized content and actions for authenticated users.</p>
        {loading ? (
          <div className="mt-4 p-3 border rounded bg-[#F8FAFF]">Loading your dashboard…</div>
        ) : !user ? (
          <div className="mt-4 p-3 border rounded bg-[#FFF6F6] text-[#8B0000]">Login required. Please sign in to continue.</div>
        ) : (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-4 rounded-xl border bg-[#F8FAFF]">
              <div className="text-sm text-gray-600">Welcome</div>
              <div className="font-semibold">{user?.name || user?.full_name || user?.email || 'User'}</div>
            </div>
            <div className="p-4 rounded-xl border bg-[#F8FAFF]">
              <div className="text-sm text-gray-600">Recent Activity</div>
              <div className="text-sm">Purchase history and preferences (coming soon)</div>
            </div>
            <div className="p-4 rounded-xl border bg-[#F8FAFF]">
              <div className="text-sm text-gray-600">Nearby Offers</div>
              <div className="text-sm">Tailored recommendations (coming soon)</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}