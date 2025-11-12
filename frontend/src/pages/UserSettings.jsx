import React from 'react'

export default function UserSettings() {
  return (
    <div className="max-w-2xl mx-auto bg-white text-black rounded-lg shadow p-4">
      <h1 className="text-xl font-semibold mb-3">Settings & Preferences</h1>
      <p className="text-sm text-gray-700 mb-4">Manage your account and application preferences.</p>
      <div className="space-y-4">
        <div className="border rounded-lg p-3">
          <h2 className="font-medium">Appearance</h2>
          <p className="text-sm text-gray-600">Theme, fonts, and accessibility settings.</p>
        </div>
        <div className="border rounded-lg p-3">
          <h2 className="font-medium">Notifications</h2>
          <p className="text-sm text-gray-600">Email and push notification preferences.</p>
        </div>
        <div className="border rounded-lg p-3">
          <h2 className="font-medium">Security</h2>
          <p className="text-sm text-gray-600">Password, sessions, and devices.</p>
        </div>
      </div>
    </div>
  )
}