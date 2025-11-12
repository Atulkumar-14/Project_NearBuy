import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useParams } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function ShopProduct() {
  const { shopId, productId } = useParams()
  const [items, setItems] = useState([])

  useEffect(() => {
    const load = async () => {
      if (!productId) return
      const res = await axios.get(`${API_BASE}/products/${productId}/prices`)
      const filtered = (res.data || []).filter(p => String(p.shop_id) === String(shopId))
      setItems(filtered)
    }
    load()
  }, [shopId, productId])

  return (
    <div className="space-y-2">
      <div className="font-semibold">Shop #{shopId} · Product #{productId}</div>
      <ul className="space-y-2">
        {items.length === 0 ? <div>No entries.</div> : items.map((i, idx) => (
          <li key={idx} className="p-2 border rounded flex justify-between">
            <div>{i.shop_name}</div>
            <div>{i.price != null ? `₹${i.price}` : 'N/A'} · Stock: {i.stock ?? 'N/A'}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}