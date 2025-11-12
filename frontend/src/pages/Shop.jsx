import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useParams, useNavigate } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function Shop() {
  const { shopId } = useParams()
  const [shop, setShop] = useState(null)
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const isOwner = !!localStorage.getItem('owner_token')

  useEffect(() => {
    const run = async () => {
      setLoading(true)
      try {
        const shopRes = await axios.get(`${API_BASE}/shops/${shopId}`)
        setShop(shopRes.data)
        const res = await axios.get(`${API_BASE}/shops/${shopId}/products`)
        setItems(res.data || [])
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [shopId])

  return (
    <div className="space-y-6">
      {/* Banner */}
      {shop?.shop_image ? (
        <img src={shop.shop_image} alt={shop.shop_name} className="h-56 w-full object-cover rounded-2xl" />
      ) : (
        <div className="h-56 w-full rounded-2xl bg-gradient-to-r from-primary to-accent text-white flex items-center justify-center text-3xl font-bold">
          {shop?.shop_name || 'Shop'}
        </div>
      )}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">{shop?.shop_name || 'Shop Products'}</h1>
        {isOwner && (
          <div className="flex gap-2">
            <button className="px-3 py-2 rounded-lg border" onClick={()=>navigate(`/shops/${shopId}/manage`)}>Manage Shop</button>
            <button className="px-3 py-2 rounded-lg bg-white text-black border" onClick={()=>navigate(`/shops/${shopId}/add-product`)}>Add Product</button>
          </div>
        )}
      </div>
      {shop && (
        <div className="mt-2 text-sm text-gray-900">
          <div><span className="font-semibold">Address:</span> {shop.area || ''}{shop.city ? `, ${shop.city}` : ''}{shop.pincode ? ` - ${shop.pincode}` : ''}</div>
          {shop.landmark && (<div><span className="font-semibold">Landmark:</span> {shop.landmark}</div>)}
          {Array.isArray(shop.timings) && shop.timings.length > 0 && (
            <div className="mt-2">
              <div className="font-semibold">Timings</div>
              <div className="grid grid-cols-2 gap-2 mt-1">
                {shop.timings.map((t, idx)=> (
                  <div key={idx} className="flex justify-between border rounded-md px-3 py-1 bg-white">
                    <span>{t.day}</span>
                    <span>{t.opens_at || t.open_time} - {t.closes_at || t.close_time}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      {loading && <div>Loading products...</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map(item => (
          <div key={`${item.product_id}-${item.shop_id || shopId}`} className="rounded-2xl overflow-hidden bg-white border shadow-sm">
            {item.image_url ? (
              <img src={item.image_url} alt={item.product_name} className="h-40 w-full object-cover" />
            ) : (
              <div className="h-40 bg-gray-100 flex items-center justify-center text-3xl font-bold text-gray-400">
                {(item.product_name || '?').slice(0,1).toUpperCase()}
              </div>
            )}
            <div className="p-4">
              <div className="font-semibold text-lg">{item.product_name}</div>
              <div className="text-sm text-gray-600">{item.brand}</div>
              <div className="mt-2">
                <span className="text-xl font-bold">₹{item.price}</span>
                {item.stock != null && (
                  <span className={`ml-2 text-xs px-2 py-1 rounded ${item.stock>0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{item.stock>0 ? 'In stock' : 'Out of stock'}</span>
                )}
              </div>
              <div className="mt-4 flex gap-2">
                <button className="px-3 py-2 rounded-lg bg-primary text-white" onClick={()=>navigate(`/products/${item.product_id}`)}>Compare Prices</button>
              </div>
            </div>
          </div>
        ))}
        {!loading && items.length === 0 && (
          <div className="text-gray-600">No products listed for this shop.</div>
        )}
      </div>
    </div>
  )
}