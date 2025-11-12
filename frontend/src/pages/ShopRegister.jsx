import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function ShopRegister() {
  const navigate = useNavigate()
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({
    shop_name: '',
    gstin: '',
    shop_image: '',
    owner_name: '',
    owner_email: '',
    owner_phone: '',
    owner_password: '',
    owner_password_confirm: '',
    city: '',
    country: '',
    pincode: '',
    landmark: '',
    area: '',
    latitude: '',
    longitude: '',
  })
  const [errors, setErrors] = useState({})
  const [alertError, setAlertError] = useState('')
  const [alertSuccess, setAlertSuccess] = useState('')

  const onChange = (e) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: value }))
  }

  const submit = async () => {
    setAlertError('')
    setAlertSuccess('')
    const nextErrors = {}
    if (!form.shop_name.trim()) nextErrors.shop_name = 'Shop name is required'
    const emailOk = form.owner_email ? /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.owner_email) : true
    if (!emailOk) nextErrors.owner_email = 'Enter a valid email'
    const phoneDigits = (form.owner_phone || '').replace(/\D/g, '')
    if (form.owner_phone && (phoneDigits.length < 10 || phoneDigits.length > 15)) nextErrors.owner_phone = 'Enter a valid phone number'
    const pw = form.owner_password || ''
    const pwc = form.owner_password_confirm || ''
    const strongPw = pw.length >= 8 && /[A-Z]/.test(pw) && /\d/.test(pw) && /[^A-Za-z0-9]/.test(pw)
    if (!strongPw) nextErrors.owner_password = 'Password must be 8+ chars with uppercase, number, and special character'
    if (pw !== pwc) nextErrors.owner_password_confirm = 'Passwords do not match'
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return
    setSaving(true)
    try {
      const payload = {
        shop_name: form.shop_name,
        gstin: form.gstin,
        shop_image: form.shop_image || undefined,
        owner_name: form.owner_name || undefined,
        owner_email: form.owner_email || undefined,
        owner_phone: form.owner_phone || undefined,
        owner_password: form.owner_password,
        owner_password_confirm: form.owner_password_confirm,
        city: form.city || undefined,
        country: form.country || undefined,
        pincode: form.pincode || undefined,
        landmark: form.landmark || undefined,
        area: form.area || undefined,
        latitude: form.latitude ? Number(form.latitude) : undefined,
        longitude: form.longitude ? Number(form.longitude) : undefined,
      }
      const res = await axios.post(`${API_BASE}/shops/register`, payload)
      const shop = res.data
      setAlertSuccess('Shop registered successfully!')
      navigate(`/shops/${shop.shop_id}`)
    } catch (e) {
      const detail = e?.response?.data?.detail
      let message = 'Failed to register shop'
      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail)) {
        const msgs = detail.map(d => (typeof d === 'string' ? d : (d?.msg || JSON.stringify(d)))).filter(Boolean)
        if (msgs.length) message = msgs.join('; ')
      } else if (detail && typeof detail === 'object') {
        message = detail.msg || JSON.stringify(detail)
      }
      console.error('Shop registration failed:', e?.response || e)
      setAlertError(message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px] shadow-lg">
        <div className="rounded-2xl bg-white text-gray-900 p-6 md:p-8">
          <h1 className="text-2xl font-bold">Register Your Shop</h1>
          <p className="mt-1 text-sm text-gray-600">Provide GSTIN and shop details to get listed.</p>
          {alertError && (
            <div className="mt-3 rounded-lg border border-red-300 bg-red-50 text-red-700 px-3 py-2 text-sm">{alertError}</div>
          )}
          {alertSuccess && (
            <div className="mt-3 rounded-lg border border-green-300 bg-green-50 text-green-700 px-3 py-2 text-sm">{alertSuccess}</div>
          )}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Shop Name</label>
              <input name="shop_name" className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="e.g., DB Mall Electronics" value={form.shop_name} onChange={onChange} />
              {errors.shop_name && <div className="text-xs text-red-600 mt-1">{errors.shop_name}</div>}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">GSTIN</label>
              <input name="gstin" className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="15-digit GSTIN" value={form.gstin} onChange={onChange} />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-1">Shop Image URL</label>
              <input name="shop_image" className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="https://..." value={form.shop_image} onChange={onChange} />
            </div>
          </div>

          <h2 className="mt-8 text-lg font-semibold">Owner Details</h2>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4">
            <input name="owner_name" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Owner name" value={form.owner_name} onChange={onChange} />
            <input name="owner_phone" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Phone" value={form.owner_phone} onChange={onChange} />
            <input name="owner_email" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Email" value={form.owner_email} onChange={onChange} />
            {errors.owner_phone && <div className="text-xs text-red-600 mt-1 md:col-span-3">{errors.owner_phone}</div>}
            {errors.owner_email && <div className="text-xs text-red-600 mt-1 md:col-span-3">{errors.owner_email}</div>}
          </div>

          <h2 className="mt-8 text-lg font-semibold">Account Security</h2>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input name="owner_password" type="password" className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Strong password" value={form.owner_password} onChange={onChange} />
              {errors.owner_password && <div className="text-xs text-red-600 mt-1">{errors.owner_password}</div>}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Confirm Password</label>
              <input name="owner_password_confirm" type="password" className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Repeat password" value={form.owner_password_confirm} onChange={onChange} />
              {errors.owner_password_confirm && <div className="text-xs text-red-600 mt-1">{errors.owner_password_confirm}</div>}
            </div>
          </div>

          <h2 className="mt-8 text-lg font-semibold">Address</h2>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4">
            <input name="city" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="City" value={form.city} onChange={onChange} />
            <input name="area" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Area" value={form.area} onChange={onChange} />
            <input name="landmark" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Landmark" value={form.landmark} onChange={onChange} />
            <input name="country" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Country" value={form.country} onChange={onChange} />
            <input name="pincode" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Pincode" value={form.pincode} onChange={onChange} />
            <input name="latitude" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Latitude" value={form.latitude} onChange={onChange} />
            <input name="longitude" className="rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Longitude" value={form.longitude} onChange={onChange} />
          </div>

          <div className="mt-8 flex gap-3">
            <button className="px-4 py-2 rounded-lg bg-primary text-black border" onClick={submit} disabled={saving}>{saving ? 'Registering...' : 'Register Shop'}</button>
            <button className="px-4 py-2 rounded-lg border" onClick={()=>navigate('/shops')}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  )
}
