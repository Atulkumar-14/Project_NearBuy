import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { IKContext, IKUpload } from 'imagekitio-react'

const API_BASE = 'http://localhost:8000/api'

function Nav({ active, setActive, dark, setDark }) {
  const tabs = ['Login/Register', 'Search', 'Nearby', 'Prices', 'Shop', 'Reviews', 'Upload', 'Admin']
  return (
    <div className="flex flex-wrap items-center gap-2 p-4 bg-gradient-to-r from-primary/80 to-primary text-white">
      <div className="mr-3 font-semibold">Nearbuy · Bhopal</div>
      {tabs.map(t => (
        <button key={t} onClick={() => setActive(t)}
          className={`px-3 py-1 rounded border border-white/30 ${active === t ? 'bg-white text-primary' : 'bg-white/10 text-white'}`}>{t}</button>
      ))}
      <div className="ml-auto flex items-center gap-2">
        <button onClick={() => setDark(!dark)} className="px-3 py-1 rounded border border-white/30 bg-white/10">
          {dark ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>
    </div>
  )
}

function LoginRegister({ onAuth }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ name: '', email: '', password: '', phone: '' })
  const [loading, setLoading] = useState(false)
  const submit = async () => {
    setLoading(true)
    try {
      if (mode === 'register') {
        await axios.post(`${API_BASE}/auth/register`, form)
      }
      const res = await axios.post(`${API_BASE}/auth/login`, { email: form.email, password: form.password })
      const { access_token, user_id } = res.data
      localStorage.setItem('token', access_token)
      localStorage.setItem('user_id', String(user_id))
      onAuth({ token: access_token, userId: user_id })
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed')
    } finally {
      setLoading(false)
    }
  }
  return (
    <div className="p-4 max-w-md space-y-3">
      <div className="flex gap-2">
        <button className={`px-3 py-1 border ${mode==='login'?'bg-primary text-white':''}`} onClick={()=>setMode('login')}>Login</button>
        <button className={`px-3 py-1 border ${mode==='register'?'bg-primary text-white':''}`} onClick={()=>setMode('register')}>Register</button>
      </div>
      {mode==='register' && (
        <input className="w-full border p-2" placeholder="Name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} />
      )}
      <input className="w-full border p-2" placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} />
      <input className="w-full border p-2" placeholder="Password" type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} />
      {mode==='register' && (
        <input className="w-full border p-2" placeholder="Phone" value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})} />
      )}
      <button onClick={submit} disabled={loading} className="px-4 py-2 bg-primary text-white rounded">{loading?'Loading...':'Submit'}</button>
    </div>
  )
}

function Search({ onProductSelect }) {
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const search = async () => {
    const userId = localStorage.getItem('user_id')
    const res = await axios.get(`${API_BASE}/search/products`, { params: { q, user_id: userId || undefined } })
    setResults(res.data)
  }
  return (
    <div className="p-4 space-y-3">
      <div className="flex gap-2">
        <input className="flex-1 border p-2" placeholder="Search products" value={q} onChange={e=>setQ(e.target.value)} />
        <button className="px-3 py-2 bg-primary text-white rounded" onClick={search}>Search</button>
      </div>
      <ul className="space-y-2">
        {results.map(p => (
          <li key={p.product_id} className="p-2 border rounded flex justify-between items-center">
            <div>
              <div className="font-semibold">{p.product_name}</div>
              <div className="text-sm text-gray-600">{p.brand || ''} {p.color || ''}</div>
            </div>
            <button className="px-2 py-1 border rounded" onClick={()=>onProductSelect(p)}>Compare Prices</button>
          </li>
        ))}
      </ul>
    </div>
  )
}

function Nearby() {
  const [lat, setLat] = useState('')
  const [lon, setLon] = useState('')
  const [radius, setRadius] = useState('5')
  const [items, setItems] = useState([])
  const run = async () => {
    const res = await axios.get(`${API_BASE}/shops/nearby`, { params: { lat: Number(lat), lon: Number(lon), radius_km: Number(radius) } })
    setItems(res.data)
  }
  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        <input className="border p-2" placeholder="Latitude" value={lat} onChange={e=>setLat(e.target.value)} />
        <input className="border p-2" placeholder="Longitude" value={lon} onChange={e=>setLon(e.target.value)} />
        <input className="border p-2" placeholder="Radius (km)" value={radius} onChange={e=>setRadius(e.target.value)} />
        <button className="px-3 py-2 bg-primary text-white rounded" onClick={run}>Find Nearby</button>
      </div>
      <ul className="space-y-2">
        {items.map(s => (
          <li key={s.shop_id} className="p-2 border rounded flex justify-between">
            <div>
              <div className="font-semibold">{s.shop_name}</div>
              <div className="text-sm">{s.city || ''} {s.area || ''}</div>
            </div>
            <div className="text-sm">{s.distance_km} km</div>
          </li>
        ))}
      </ul>
    </div>
  )
}

function Prices({ product }) {
  const [items, setItems] = useState([])
  useEffect(() => {
    const load = async () => {
      if (!product) return
      const res = await axios.get(`${API_BASE}/products/${product.product_id}/prices`)
      setItems(res.data)
    }
    load()
  }, [product])
  if (!product) return <div className="p-4">Select a product from Search.</div>
  return (
    <div className="p-4 space-y-2">
      <div className="font-semibold">Prices for {product.product_name}</div>
      <ul className="space-y-2">
        {items.map((i, idx) => (
          <li key={idx} className="p-2 border rounded flex justify-between">
            <div>{i.shop_name}</div>
            <div>{i.price != null ? `₹${i.price}` : 'N/A'} · Stock: {i.stock ?? 'N/A'}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}

function ShopDetails() {
  const [shopId, setShopId] = useState('')
  const [data, setData] = useState(null)
  const load = async () => {
    const res = await axios.get(`${API_BASE}/shops/${Number(shopId)}/availability`)
    setData(res.data)
  }
  return (
    <div className="p-4 space-y-3">
      <div className="flex gap-2">
        <input className="border p-2" placeholder="Shop ID" value={shopId} onChange={e=>setShopId(e.target.value)} />
        <button className="px-3 py-2 bg-primary text-white rounded" onClick={load}>Check</button>
      </div>
      {data && <div className="p-2 border rounded">{data.shop_name} is {data.is_open ? 'Open' : 'Closed'}</div>}
    </div>
  )
}

function Reviews({ product }) {
  const [items, setItems] = useState([])
  const [rating, setRating] = useState('5')
  const [text, setText] = useState('')
  useEffect(() => {
    const load = async () => {
      if (!product) return
      const res = await axios.get(`${API_BASE}/reviews/product/${product.product_id}`)
      setItems(res.data)
    }
    load()
  }, [product])
  const add = async () => {
    const userId = localStorage.getItem('user_id')
    if (!userId) return alert('Login required')
    await axios.post(`${API_BASE}/reviews`, { product_id: product.product_id, rating: Number(rating), review_text: text }, { params: { user_id: Number(userId) } })
    const res = await axios.get(`${API_BASE}/reviews/product/${product.product_id}`)
    setItems(res.data)
  }
  return (
    <div className="p-4 space-y-3">
      {!product ? <div>Select a product from Search.</div> : (
        <>
          <div className="grid grid-cols-3 gap-2">
            <input className="border p-2" value={rating} onChange={e=>setRating(e.target.value)} placeholder="Rating 1-5" />
            <input className="border p-2 col-span-2" value={text} onChange={e=>setText(e.target.value)} placeholder="Review text" />
            <button className="px-3 py-2 bg-primary text-white rounded" onClick={add}>Add Review</button>
          </div>
          <ul className="space-y-2">
            {items.map(r => (
              <li key={r.review_id} className="p-2 border rounded">
                <div className="font-semibold">Rating: {r.rating}</div>
                <div className="text-sm">{r.review_text || ''}</div>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

function Upload() {
  const authEndpoint = `${API_BASE}/uploads/imagekit/auth`
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)
  const [urlEndpoint, setUrlEndpoint] = useState('')
  const [publicKey, setPublicKey] = useState('')

  const ctxProps = useMemo(() => ({
    urlEndpoint: urlEndpoint || 'https://ik.imagekit.io/your_endpoint',
    publicKey: publicKey || 'public_key_placeholder',
    authenticationEndpoint: authEndpoint,
  }), [urlEndpoint, publicKey])

  useEffect(() => {
    // fetch config to initialize automatically
    axios.get(authEndpoint).then(() => {
      // The component will use server-provided auth on demand.
    }).catch(() => {})
  }, [])

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <input className="border p-2" placeholder="ImageKit URL Endpoint" value={urlEndpoint} onChange={e=>setUrlEndpoint(e.target.value)} />
        <input className="border p-2" placeholder="Public Key" value={publicKey} onChange={e=>setPublicKey(e.target.value)} />
      </div>
      <IKContext {...ctxProps}>
        <div className="p-4 border-dashed border-2 rounded">
          <IKUpload
            fileName="nearbuy-upload"
            useUniqueFileName
            validateFile={(file) => {
              const allowed = ['image/jpeg','image/png','image/webp']
              const maxSize = 2 * 1024 * 1024
              if (!allowed.includes(file.type)) { setError('Only JPEG/PNG/WebP allowed'); return false }
              if (file.size > maxSize) { setError('Max size 2MB'); return false }
              setError(null)
              return true
            }}
            onError={(err) => setError(err?.message || 'Upload failed')}
            onSuccess={() => { setError(null); setProgress(100) }}
            onUploadProgress={(evt) => setProgress(Math.round((evt.loaded / evt.total) * 100))}
            folder="/nearbuy"
            className="w-full"
          />
          <div className="mt-2 text-sm">Progress: {progress}%</div>
          {error && <div className="mt-2 text-red-600">{error}</div>}
        </div>
      </IKContext>
    </div>
  )
}

function Admin() {
  const [stats, setStats] = useState(null)
  const load = async () => {
    const res = await axios.get(`${API_BASE}/admin/stats`)
    setStats(res.data)
  }
  useEffect(() => { load() }, [])
  return (
    <div className="p-4">
      {!stats ? 'Loading...' : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {Object.entries(stats).map(([k,v]) => (
            <div key={k} className="p-4 border rounded">
              <div className="text-sm uppercase text-gray-600">{k}</div>
              <div className="text-2xl font-bold">{v}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [active, setActive] = useState('Login/Register')
  const [product, setProduct] = useState(null)
  const [auth, setAuth] = useState({ token: localStorage.getItem('token'), userId: localStorage.getItem('user_id') })
  const [dark, setDark] = useState(false)
  useEffect(() => {
    const root = document.documentElement
    if (dark) root.classList.add('dark')
    else root.classList.remove('dark')
  }, [dark])
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 dark:text-gray-100">
      <Nav active={active} setActive={setActive} dark={dark} setDark={setDark} />
      {active === 'Login/Register' && <LoginRegister onAuth={setAuth} />}
      {active === 'Search' && <Search onProductSelect={(p)=>{setProduct(p); setActive('Prices')}} />}
      {active === 'Nearby' && <Nearby />}
      {active === 'Prices' && <Prices product={product} />}
      {active === 'Shop' && <ShopDetails />}
      {active === 'Reviews' && <Reviews product={product} />}
      {active === 'Upload' && <Upload />}
      {active === 'Admin' && <Admin />}
    </div>
  )
}
