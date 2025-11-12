import React, { useState } from 'react'
import axios from 'axios'
import { useParams } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function ShopAddProduct() {
  const { shopId } = useParams()
  const [form, setForm] = useState({ product_name: '', brand: '', description: '', color: '', category_id: '' })
  const [price, setPrice] = useState('')
  const [stock, setStock] = useState('')
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('')
  const [progress, setProgress] = useState(0)
  const MAX_IMAGE_SIZE = 3 * 1024 * 1024
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

  const submit = async (e) => {
    e.preventDefault()
    setStatus('Submitting...')
    setProgress(0)
    try {
      const res = await axios.post(`${API_BASE}/shops/manage/${shopId}/products/create`, {
        product_name: form.product_name,
        category_id: form.category_id || null,
        brand: form.brand || null,
        description: form.description || null,
        color: form.color || null,
        price: price ? Number(price) : null,
        stock: stock ? Number(stock) : null,
      }, { withCredentials: true })
      setStatus(`Added product ${res.data.product_name} (ID ${res.data.product_id})`)
      setForm({ product_name: '', brand: '', description: '', color: '', category_id: '' })
      setPrice('')
      setStock('')
      setFile(null)
    } catch (e) {
      setStatus(e?.response?.data?.detail || 'Failed to add product')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-black">Add Product to Shop</h1>
      <form onSubmit={submit} className="rounded-2xl bg-white text-black p-6 shadow-sm grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold mb-1">Product Name</label>
          <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" value={form.product_name} onChange={e=>setForm({...form, product_name: e.target.value})} required />
        </div>
        <div>
          <label className="block text-sm font-semibold mb-1">Brand</label>
          <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" value={form.brand} onChange={e=>setForm({...form, brand: e.target.value})} />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-semibold mb-1">Description</label>
          <textarea className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" value={form.description} onChange={e=>setForm({...form, description: e.target.value})} />
        </div>
        <div>
          <label className="block text-sm font-semibold mb-1">Color</label>
          <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" value={form.color} onChange={e=>setForm({...form, color: e.target.value})} />
        </div>
        <div>
          <label className="block text-sm font-semibold mb-1">Category ID (string)</label>
          <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" placeholder="e.g., mobiles, laptops" value={form.category_id} onChange={e=>setForm({...form, category_id: e.target.value})} />
        </div>
        <div>
          <label className="block text-sm font-semibold mb-1">Price</label>
          <input type="number" step="0.01" className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" value={price} onChange={e=>setPrice(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-semibold mb-1">Stock</label>
          <input type="number" className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" value={stock} onChange={e=>setStock(e.target.value)} />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-semibold mb-1">Image (JPEG/PNG/WebP, ≤ 3MB)</label>
          <input type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>setFile(e.target.files?.[0] || null)} />
          {progress > 0 && (
            <div className="mt-2 h-2 bg-gray-200 rounded">
              <div className="h-2 bg-primary rounded" style={{ width: `${progress}%` }} />
            </div>
          )}
        </div>
        <div className="md:col-span-2">
          <button type="submit" className="px-4 py-2 rounded-lg bg-white text-black border font-semibold">Add Product</button>
        </div>
      </form>
      {status && (
        <div className={`text-sm ${status.startsWith('Added product') ? 'p-2 rounded border bg-green-50 text-green-700' : 'p-2 rounded border bg-red-50 text-red-700'}`}>{status}</div>
      )}
    </div>
  )
}
