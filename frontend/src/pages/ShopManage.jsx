import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useParams, useNavigate } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function ShopManage() {
  const { shopId } = useParams()
  const navigate = useNavigate()
  const [products, setProducts] = useState([])
  const [shopInventory, setShopInventory] = useState([])
  const [selected, setSelected] = useState('')
  const [price, setPrice] = useState('')
  const [stock, setStock] = useState('')
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      setSuccess('')
    try {
      const [allProducts, inventory] = await Promise.all([
        axios.get(`${API_BASE}/products`, { withCredentials: true }),
        axios.get(`${API_BASE}/shops/${shopId}/products`, { withCredentials: true }),
      ])
      setProducts(allProducts.data || [])
      setShopInventory(inventory.data || [])
    } catch (e) {
      // Fallback: attempt to load via owner aggregate and filter by shopId
      try {
        const ownerList = await axios.get(`${API_BASE}/shops/owner/products`, { withCredentials: true })
        const arr = Array.isArray(ownerList.data) ? ownerList.data : []
        const filtered = arr.filter(it => String(it.shop_id) === String(shopId))
        setShopInventory(filtered)
        setProducts([])
        setError('')
      } catch (e2) {
        const d = e2?.response?.data
        const msg = (typeof d?.detail === 'string' ? d.detail : 'Failed to load shop inventory')
        setError(msg)
      }
    } finally {
      setLoading(false)
    }
    }
    load()
  }, [])

  useEffect(() => {
    // When product selection changes, prefill current price/stock if available
    if (!selected) { setPrice(''); setStock(''); return }
    const existing = shopInventory.find(i => String(i.product_id) === String(selected))
    if (existing) {
      setPrice(existing.price != null ? String(existing.price) : '')
      setStock(existing.stock != null ? String(existing.stock) : '')
    } else {
      setPrice('')
      setStock('')
    }
  }, [selected, shopInventory])

  const submit = async () => {
    if (!selected) { alert('Select a product'); return }
    setSaving(true)
    setError('')
    setSuccess('')
    try {
      await axios.post(`${API_BASE}/shops/${shopId}/products`, {
        product_id: selected,
        price: price ? Number(price) : null,
        stock: stock ? Number(stock) : null,
      }, { withCredentials: true })
      setSuccess('Product added/updated for shop')
      const inventory = await axios.get(`${API_BASE}/shops/${shopId}/products`, { withCredentials: true })
      setShopInventory(inventory.data || [])
    } catch (e) {
      const d = e?.response?.data
      const msg = (typeof d?.detail === 'string' ? d.detail : 'Failed to add product')
      setError(msg)
    } finally {
      setSaving(false)
    }
  }

  const remove = async () => {
    if (!selected) { alert('Select a product'); return }
    if (!confirm('Remove this product from your shop?')) return
    setDeleting(true)
    setError('')
    setSuccess('')
    try {
      await axios.delete(`${API_BASE}/shops/${shopId}/products/${selected}`, { withCredentials: true })
      setSuccess('Product removed from shop')
      const inventory = await axios.get(`${API_BASE}/shops/${shopId}/products`, { withCredentials: true })
      setShopInventory(inventory.data || [])
    } catch (e) {
      const d = e?.response?.data
      const msg = (typeof d?.detail === 'string' ? d.detail : 'Failed to remove product')
      setError(msg)
    } finally {
      setDeleting(false)
    }
  }

  const removeItem = async (productId) => {
    if (!confirm('Remove this product from your shop?')) return
    try {
      await axios.delete(`${API_BASE}/shops/${shopId}/products/${productId}`, { withCredentials: true })
      setShopInventory(prev => prev.filter(i => String(i.product_id) !== String(productId)))
    } catch (e) {
      alert(e?.response?.data?.detail || 'Failed to remove product')
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px] shadow-lg">
        <div className="rounded-2xl bg-white text-gray-900 p-6">
          <h1 className="text-2xl font-bold">Manage Shop Products</h1>
          <p className="mt-1 text-sm text-gray-600">Add or update price and stock for products.</p>
          {loading && <div className="mt-2 text-sm">Loading inventory…</div>}
          {error && <div className="mt-2 p-2 rounded border bg-red-50 text-red-700 text-sm">{error}</div>}
          {success && <div className="mt-2 p-2 rounded border bg-green-50 text-green-700 text-sm">{success}</div>}
          <div className="mt-4">
            <button className="px-4 py-2 rounded-lg bg-white text-black border font-semibold" onClick={()=>navigate(`/shops/${shopId}/add-product`)}>+ Add New Product</button>
          </div>
          {/* Current shop products */}
          <div className="mt-6">
            <h2 className="text-lg font-semibold">Current Products</h2>
            <div className="mt-2 space-y-2">
              {shopInventory.map((i) => {
                const name = products.find(p => String(p.product_id) === String(i.product_id))?.product_name || 'Product'
                return (
                  <div key={i.product_id} className="p-3 rounded-xl border flex items-center justify-between">
                    <div>
                      <div className="font-bold text-black">{name}</div>
                      <div className="text-sm text-gray-600">₹{i.price ?? 'N/A'} · Stock: {i.stock ?? 'N/A'}</div>
                    </div>
                    <div className="flex gap-2">
                      <button className="px-3 py-1 rounded-md border" onClick={()=>setSelected(i.product_id)}>Edit</button>
                      <button className="px-3 py-1 rounded-md bg-red-600 text-white" onClick={()=>removeItem(i.product_id)}>Delete</button>
                    </div>
                  </div>
                )
              })}
              {shopInventory.length === 0 && !loading && (
                <div className="text-sm text-gray-700">No products added to this shop yet.</div>
              )}
            </div>
          </div>
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <label className="block text-sm font-medium mb-1">Product</label>
              <select className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" value={selected} onChange={e=>setSelected(e.target.value)}>
                <option value="">Select a product</option>
                {products.map(p => (
                  <option key={p.product_id} value={p.product_id}>{p.product_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Price (₹)</label>
              <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" placeholder="e.g., 499.00" value={price} onChange={e=>setPrice(e.target.value)} />
              {selected && (
                <div className="text-xs text-gray-600 mt-1">Current: {(() => {
                  const ex = shopInventory.find(i => String(i.product_id) === String(selected))
                  const p = ex?.price != null ? `₹${ex.price}` : 'N/A'
                  const s = ex?.stock != null ? ex.stock : 'N/A'
                  return `${p} · Stock: ${s}`
                })()}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Stock</label>
              <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black" placeholder="e.g., 10" value={stock} onChange={e=>setStock(e.target.value)} />
            </div>
          </div>
          <div className="mt-6 flex gap-3">
            <button className="px-4 py-2 rounded-lg bg-primary text-white" onClick={submit} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
            <button className="px-4 py-2 rounded-lg bg-red-600 text-white" onClick={remove} disabled={deleting || !selected}>{deleting ? 'Removing...' : 'Remove from shop'}</button>
            <button className="px-4 py-2 rounded-lg border" onClick={()=>navigate(`/shops/${shopId}`)}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  )
}
