import React, { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export default function ShopAddProductLanding() {
  const navigate = useNavigate()
  const [shopId, setShopId] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('owner_token')
    if (!token) {
      navigate('/owner/login?redirect=/shops/add-product')
    }
  }, [navigate])

  const go = () => {
    const id = String(shopId || '').trim()
    if (!id) return
    navigate(`/shops/${id}/add-product`)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px]">
        <div className="rounded-2xl bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-black">Add Products to Your Shop</h1>
          <p className="mt-2 text-gray-800">Enter your Shop ID to go to the product addition page. If you don’t have a shop yet, register it first.</p>
          <div className="mt-2 text-sm text-gray-700">You are required to be logged in as the shop owner.</div>
          <div className="mt-4 flex gap-2">
            <input className="flex-1 rounded-lg px-4 py-2 bg-[#EAF0FF] text-black placeholder:text-gray-600 border" placeholder="Enter Shop ID" value={shopId} onChange={e=>setShopId(e.target.value)} />
            <button className="px-4 py-2 rounded-lg bg-white text-black border font-semibold" onClick={go}>Go</button>
          </div>
          <div className="mt-3 text-sm text-gray-700">
            Don’t know your Shop ID? Visit your shop page or register here: <Link className="text-primary hover:underline" to="/shops/register">Shop Registration</Link>
          </div>
        </div>
      </div>
    </div>
  )
}