import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function Signup() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [phone, setPhone] = useState('')
  const [errors, setErrors] = useState({})
  const [alertError, setAlertError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    // Client-side validation
    const nextErrors = {}
    if (!name.trim()) nextErrors.name = 'Name is required'
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailPattern.test(email)) nextErrors.email = 'Enter a valid email'
    const pwd = password || ''
    const pwErrors = []
    if (pwd.length < 12) pwErrors.push('Password must be at least 12 characters')
    if (!/[A-Z]/.test(pwd)) pwErrors.push('Include at least one uppercase letter')
    if (!/[a-z]/.test(pwd)) pwErrors.push('Include at least one lowercase letter')
    if (!/[0-9]/.test(pwd)) pwErrors.push('Include at least one number')
    if (!/[^A-Za-z0-9]/.test(pwd)) pwErrors.push('Include at least one special character')
    if (pwErrors.length) nextErrors.password = pwErrors.join('; ')
    const phoneDigits = (phone || '').replace(/\D/g, '')
    if (phoneDigits.length < 10 || phoneDigits.length > 15) nextErrors.phone = 'Enter a valid phone number'
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return
    setLoading(true)
    try {
      await axios.post(`${API_BASE}/auth/register`, { name, email, password, phone })
      alert('Registered! You can login now.')
      navigate('/login?next=/user/profile')
    } catch (e) {
      const detail = e.response?.data?.detail
      let message = 'Unknown error'
      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail)) {
        const msgs = detail.map(d => (typeof d === 'string' ? d : d?.msg || JSON.stringify(d))).filter(Boolean)
        if (msgs.length) message = msgs.join('; ')
      } else if (detail && typeof detail === 'object') {
        message = detail.msg || JSON.stringify(detail)
      }
      const status = e?.response?.status
      if (status === 409 && !message) message = 'Email or phone already exists'
      console.error('Registration failed:', e?.response || e)
      setAlertError(`Registration failed: ${message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px] shadow-lg">
        <div className="rounded-2xl bg-white text-black p-6">
          <h1 className="text-3xl font-bold mb-2">Create Account</h1>
          <p className="text-sm text-gray-700 mb-4">Sign up to explore products near you.</p>
          {alertError && (
            <div className="mb-4 rounded-lg border border-red-300 bg-red-50 text-red-700 px-3 py-2 text-sm">
              {alertError}
            </div>
          )}
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-1">Name</label>
              <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" value={name} onChange={e=>setName(e.target.value)} required placeholder="John Doe" />
              {errors.name && <div className="text-xs text-red-600 mt-1">{errors.name}</div>}
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Email</label>
              <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" type="email" value={email} onChange={e=>setEmail(e.target.value)} required placeholder="you@example.com" />
              {errors.email && <div className="text-xs text-red-600 mt-1">{errors.email}</div>}
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Password</label>
              <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" type="password" value={password} onChange={e=>setPassword(e.target.value)} required placeholder="••••••••" />
              {errors.password && <div className="text-xs text-red-600 mt-1">{errors.password}</div>}
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Phone</label>
              <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" value={phone} onChange={e=>setPhone(e.target.value)} required placeholder="e.g., +91 9876543210" />
              {errors.phone && <div className="text-xs text-red-600 mt-1">{errors.phone}</div>}
            </div>
            <button className="w-full px-4 py-2 rounded-lg bg-white text-black border font-semibold" type="submit">{loading ? 'Creating...' : 'Sign up'}</button>
            <div className="text-sm text-gray-700">Already have an account? <a className="text-primary" href="/login">Login</a></div>
          </form>
        </div>
      </div>
    </div>
  )
}
