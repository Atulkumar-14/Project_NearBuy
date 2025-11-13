import React, { useMemo, useState } from 'react'
import axios from 'axios'
import { NavLink } from 'react-router-dom'
import { useAuth } from './AuthProvider.jsx'

export default function Nav({ dark, setDark }) {
  const baseLink = 'px-3 py-1 rounded-lg transition-colors duration-150'
  const inactive = 'text-black hover:bg-[#F3F6FF] hover:text-[#1F2BD8]'
  const active = 'bg-[#EAF0FF] text-black font-semibold border border-[#D7E2FF]'
  const { user, owner, logout, isAuthenticated, loading } = useAuth()
  const isUser = !!user
  const isOwner = !!owner
  const [menuOpen, setMenuOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const API_BASE = 'http://localhost:8000/api'

  const handleLogout = async () => {
    try {
      await axios.post(`${API_BASE}/auth/logout`, {}, { withCredentials: true })
    } catch {}
    // Clear any client-side tokens
    localStorage.removeItem('token')
    localStorage.removeItem('owner_token')
    await logout()
    // Hard redirect to refresh role-aware links
    window.location.href = '/'
  }

  const profileLabel = useMemo(() => {
    const principal = user || owner
    if (!principal) return null
    const name = principal?.name || principal?.full_name || principal?.email || principal?.phone || 'Account'
    const initials = (name || '')
      .split(' ')
      .map(s => s[0])
      .join('')
      .substring(0, 2)
      .toUpperCase()
    return { name, initials }
  }, [user, owner])

  return (
    <nav role="navigation" aria-label="Main" className="bg-white text-black shadow">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          <a href="/" className="font-bold tracking-wide">Nearbuy</a>
          <div className="flex items-center gap-2">
            <button onClick={() => setDark(!dark)} aria-label="Toggle color scheme" className="px-3 py-1 rounded-lg border border-gray-300 bg-white text-black hover:bg-[#F3F6FF]">
              {dark ? 'Light Mode' : 'Dark Mode'}
            </button>
            <button className="md:hidden px-3 py-1 rounded-lg border" aria-label="Toggle menu" onClick={() => setMenuOpen(o=>!o)}>
              Menu
            </button>
          </div>
        </div>
        <div className={`md:flex ${menuOpen ? 'block' : 'hidden'} md:items-center md:gap-3 py-2`}> 
          <ul className="flex flex-col md:flex-row md:flex-wrap md:items-center gap-2">
            <li><NavLink to="/" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Home</NavLink></li>
            <li><NavLink to="/shops" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Shops</NavLink></li>
            <li><NavLink to="/products" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Products</NavLink></li>
            {isOwner && (
              <li><NavLink to="/shops/add-product" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Add Product</NavLink></li>
            )}
            <li><NavLink to="/admin" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Admin</NavLink></li>
            {isUser && (
              <li><NavLink to="/user/dashboard" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>User Dashboard</NavLink></li>
            )}
            {isUser && (
              <li><NavLink to="/user/profile" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>User Profile</NavLink></li>
            )}
            {isOwner && (
              <li><NavLink to="/shopkeeper/dashboard" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Shopkeeper Dashboard</NavLink></li>
            )}
            {isOwner && (
              <li><NavLink to="/shopkeeper/profile" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Shopkeeper Profile</NavLink></li>
            )}
            {!isOwner && (
              <li><NavLink to="/owner/login" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Owner Login</NavLink></li>
            )}
            {!isUser && (
              <li><NavLink to="/login" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Login</NavLink></li>
            )}
            {!isUser && (
              <li><NavLink to="/signup" className={({isActive}) => `${baseLink} ${isActive ? active : inactive}`}>Signup</NavLink></li>
            )}
            {isAuthenticated && (
              <li className="relative">
                <button
                  onClick={() => setProfileOpen(o => !o)}
                  className="flex items-center gap-2 px-3 py-1 rounded-lg border border-gray-200 bg-white hover:bg-[#F3F6FF]"
                  aria-haspopup="true"
                  aria-expanded={profileOpen}
                >
                  <span className="inline-flex items-center justify-center h-7 w-7 rounded-full bg-[#EAF0FF] text-[#1F2BD8] font-semibold">
                    {profileLabel?.initials || '?'}
                  </span>
                  <span className="text-sm text-black">{profileLabel?.name || 'Account'}</span>
                </button>
                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-56 rounded-lg border border-gray-200 bg-white shadow-lg z-10">
                    <div className="px-3 py-2 border-b">
                      <div className="font-semibold text-black">{profileLabel?.name || 'Account'}</div>
                      <div className="text-xs text-gray-600">{isUser ? 'User' : 'Owner'}</div>
                    </div>
                    <ul className="py-1">
                      <li>
                        <NavLink to="/user/profile" className={({isActive}) => `block px-3 py-2 ${isActive ? 'bg-[#EAF0FF]' : 'hover:bg-[#F3F6FF]'} text-black`}>
                          Profile
                        </NavLink>
                      </li>
                      <li>
                        <NavLink to="/user/settings" className={({isActive}) => `block px-3 py-2 ${isActive ? 'bg-[#EAF0FF]' : 'hover:bg-[#F3F6FF]'} text-black`}>
                          Settings & Preferences
                        </NavLink>
                      </li>
                      <li>
                        <button onClick={handleLogout} className="block w-full text-left px-3 py-2 hover:bg-red-50 text-red-700">
                          Logout
                        </button>
                      </li>
                    </ul>
                  </div>
                )}
              </li>
            )}
            {loading && (
              <li>
                <span className="px-3 py-1 text-sm text-gray-600">Checking session…</span>
              </li>
            )}
          </ul>
        </div>
      </div>
    </nav>
  )
}
