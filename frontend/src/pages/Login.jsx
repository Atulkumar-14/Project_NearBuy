import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../components/AuthProvider.jsx'

const API_BASE = 'http://localhost:8000/api'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const { refresh, user, owner, loading: authLoading } = useAuth()
  const [error, setError] = useState('')

  // If already authenticated, redirect based on role
  React.useEffect(() => {
    if (authLoading) return
    if (owner) navigate('/shopkeeper/dashboard')
    else if (user) navigate('/user/dashboard')
  }, [owner, user, authLoading, navigate])

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await axios.post(`${API_BASE}/auth/login`, { email, password }, { withCredentials: true })
      // Ensure session state is updated before navigation
      await refresh()
      const next = params.get('next')
      navigate(next || '/user/dashboard')
    } catch (e) {
      setError(e.response?.data?.detail || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px] shadow-lg">
        <div className="rounded-2xl bg-white text-black p-6">
          <h1 className="text-3xl font-bold mb-2">Welcome back</h1>
          <p className="text-sm text-gray-700 mb-4">Login to compare nearby shop prices.</p>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-1">Email</label>
              <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" type="email" value={email} onChange={e=>setEmail(e.target.value)} required placeholder="you@example.com" />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Password</label>
              <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" type="password" value={password} onChange={e=>setPassword(e.target.value)} required placeholder="••••••••" />
            </div>
            {error && <div className="text-sm text-red-600">{error}</div>}
            <button className="w-full px-4 py-2 rounded-lg bg-white text-black border font-semibold" type="submit">{loading ? 'Logging in...' : 'Login'}</button>
            <div className="text-sm text-gray-700">Don't have an account? <a className="text-primary" href="/signup">Sign up</a></div>
          </form>
        </div>
      </div>
    </div>
  )
}
