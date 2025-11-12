import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useParams, useNavigate } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function Product() {
  const { productId } = useParams()
  const navigate = useNavigate()
  const [items, setItems] = useState([])
  const [meta, setMeta] = useState(null)

  useEffect(() => {
    const load = async () => {
      if (!productId) return
      const [detail, prices] = await Promise.all([
        axios.get(`${API_BASE}/products/${productId}`),
        axios.get(`${API_BASE}/products/${productId}/prices`)
      ])
      setMeta(detail.data)
      setItems(prices.data)
    }
    load()
  }, [productId])


  return (
    <div className="space-y-8">
      {/* Product header */}
      <div className="rounded-2xl bg-[#EAF0FF] p-6 shadow text-gray-900">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="w-full md:w-64">
            {meta?.image_url ? (
              <img src={meta.image_url} alt={meta?.product_name} className="w-full h-64 object-cover rounded-xl" />
            ) : (
              <div className="w-full h-64 bg-gray-100 rounded-xl flex items-center justify-center text-5xl font-bold text-gray-400">
                {(meta?.product_name || '?').slice(0,1).toUpperCase()}
              </div>
            )}
          </div>
          <div className="flex-1 space-y-2">
            <div className="text-2xl font-bold">{meta?.product_name || `Product #${productId}`}</div>
            <div className="text-sm text-gray-700">Brand: {meta?.brand || '—'} · Color: {meta?.color || '—'}</div>
            <div className="mt-2 text-gray-900">{meta?.description || 'No description available.'}</div>
            <div className="mt-4">
              <button className="px-3 py-1 rounded-md bg-primary text-white" onClick={() => navigate('/products')}>Back to Products</button>
            </div>
          </div>
        </div>
      </div>

      {/* Price comparison */}
      <div>
        <h3 className="text-xl font-semibold">Price Comparison Across Shops</h3>
        <div className="mt-3 space-y-2">
          {items.map((i, idx) => (
            <div key={idx} className="p-4 rounded-2xl bg-white shadow flex items-center justify-between text-gray-900">
              <div className="font-medium">{i.shop_name}</div>
              <div className="text-sm">{i.price != null ? `₹${i.price}` : 'N/A'} · Stock: {i.stock ?? 'N/A'}</div>
            </div>
          ))}
          {items.length === 0 && (
            <div className="text-gray-700">No shop prices available for this product.</div>
          )}
        </div>
      </div>


      {/* Reviews placeholder */}
      <div>
        <h3 className="text-xl font-semibold">Reviews</h3>
        <div className="mt-2 text-gray-700">Reviews are not available yet. We can integrate ratings later.</div>
      </div>
    </div>
  )
}
