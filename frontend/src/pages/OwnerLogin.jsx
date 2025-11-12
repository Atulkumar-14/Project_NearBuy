import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../components/AuthProvider.jsx'

const API_BASE = 'http://localhost:8000/api'

export default function OwnerLogin() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const { refresh } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const redirectTo = params.get('redirect') || '/shopkeeper/dashboard'

  function isValidEmail(v) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)
  }

  async function submit() {
    setError('')
    setLoading(true)
    try {
      if (!email || !password) {
        setError('Email and password are required')
        setLoading(false)
        return
      }
      if (!isValidEmail(email)) {
        setError('Please enter a valid email address')
        setLoading(false)
        return
      }
      const payload = { email, password }
      const res = await axios.post(`${API_BASE}/auth/owner/login`, payload, {
        headers: { 'Content-Type': 'application/json' },
        withCredentials: true,
      })
      const token = res?.data?.access_token
      if (token) {
        localStorage.setItem('owner_token', token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      }
      await refresh()
      navigate(redirectTo)
    } catch (e) {
      let message = 'Login failed'
      const status = e?.response?.status
      if (status === 401) message = 'Invalid email or password'
      else if (status === 422) message = 'Invalid input. Please check your email and password.'
      else if (typeof e?.response?.data?.detail === 'string') message = e.response.data.detail
      setError(typeof message === 'string' ? message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px]">
        <div className="rounded-2xl bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-black">Owner Login</h1>
          <p className="mt-2 text-gray-800">Login with your email and password.</p>
          {error && <div className="mt-2 text-red-600">{error}</div>}
          <div className="mt-4 space-y-2">
            <input className="w-full rounded-lg px-4 py-2 bg-[#EAF0FF] text-black border" type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
            <input className="w-full rounded-lg px-4 py-2 bg-[#EAF0FF] text-black border" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
          </div>
          <div className="mt-4 flex gap-2">
            <button className="px-4 py-2 rounded-lg bg-white text-black border font-semibold hover:bg-[#F3F6FF]" onClick={submit} disabled={loading}>{loading ? 'Logging in...' : 'Login'}</button>
            <a href="/shops/register" className="px-4 py-2 rounded-lg border bg-[#EAF0FF] text-black hover:bg-[#DDE8FF]">Register Shop</a>
          </div>
          <div className="mt-3 text-sm text-gray-700">Default demo password is <span className="font-mono">Owner@123</span>.</div>
        </div>
      </div>
    </div>
  )
}
