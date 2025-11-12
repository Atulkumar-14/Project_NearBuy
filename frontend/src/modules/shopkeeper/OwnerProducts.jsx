import React, { useEffect, useState } from 'react'
import axios from 'axios'
const API_BASE = 'http://localhost:8000/api'
import { useAuth } from '../../components/AuthProvider.jsx'

export default function OwnerProducts() {
  const { owner } = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const res = await axios.get(`${API_BASE}/shops/owner/products`, { withCredentials: true })
      const arr = Array.isArray(res.data) ? res.data : []
      const unique = [...new Map(arr.map(it => [it.shop_product_id, it])).values()]
      setItems(unique)
    } catch (e) {
      const d = e?.response?.data
      const code = e?.response?.status
      const msg = code === 401 ? 'Login required to view your products' : (typeof d?.detail === 'string' ? d.detail : 'Failed to load products')
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (owner) load() }, [owner])

  async function updateItem(it, price, stock) {
    setError('')
    setSuccess('')
    try {
      await axios.put(`${API_BASE}/shops/manage/${it.shop_id}/products/${it.product_id}`, { price, stock }, { withCredentials: true })
      setSuccess('Updated')
      await load()
    } catch (e) {
      setError(e?.response?.data?.detail || 'Update failed')
    }
  }

  async function deleteItem(it) {
    setError('')
    setSuccess('')
    try {
      await axios.delete(`${API_BASE}/shops/manage/${it.shop_id}/products/${it.product_id}`, { withCredentials: true })
      setSuccess('Deleted')
      await load()
    } catch (e) {
      setError(e?.response?.data?.detail || 'Delete failed')
    }
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="rounded-2xl bg-white text-gray-900 p-6">
        <div className="text-sm uppercase tracking-wide text-accent">Inventory</div>
        <h1 className="text-2xl font-bold">Your Products</h1>
        {error && <div className="mt-3 p-2 rounded border bg-red-50 text-red-700 text-sm">{error}</div>}
        {success && <div className="mt-3 p-2 rounded border bg-green-50 text-green-700 text-sm">{success}</div>}
        {loading ? (
          <div className="mt-4">Loading...</div>
        ) : (
          <table className="mt-4 w-full text-sm">
            <thead>
              <tr className="text-left">
                <th className="p-2">Product</th>
                <th className="p-2">Brand</th>
                <th className="p-2">Price</th>
                <th className="p-2">Stock</th>
                <th className="p-2">Shop</th>
                <th className="p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it) => (
                <tr key={it.shop_product_id} className="border-t">
                  <td className="p-2">{it.product_name}</td>
                  <td className="p-2">{it.brand || '-'}</td>
                  <td className="p-2">{it.price ?? '-'}</td>
                  <td className="p-2">{it.stock ?? '-'}</td>
                  <td className="p-2 font-semibold text-black">{it.shop_name || '-'}</td>
                  <td className="p-2 flex gap-2">
                    <button className="px-2 py-1 rounded border" onClick={() => updateItem(it, prompt('New price', it.price), prompt('New stock', it.stock))}>Modify</button>
                    <button className="px-2 py-1 rounded border" onClick={() => deleteItem(it)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {error && (
          <div className="mt-3">
            <button className="px-3 py-1 rounded border" onClick={load}>Retry</button>
          </div>
        )}
        {!loading && items.length === 0 && (
          <div className="mt-4 text-gray-700">No products yet. Use Shop Register or Add Product to create items.</div>
        )}
      </div>
    </div>
  )
}
