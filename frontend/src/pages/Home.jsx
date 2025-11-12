import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function Home({ defaultType = 'product' }) {
  const [type, setType] = useState(defaultType) // product | category | shop
  const [q, setQ] = useState('')
  const [city, setCity] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchError, setSearchError] = useState('')
  const navigate = useNavigate()
  const [lat, setLat] = useState(null)
  const [lon, setLon] = useState(null)
  const [radiusKm, setRadiusKm] = useState(5)
  const [nearbyShops, setNearbyShops] = useState([])
  const [popularProducts, setPopularProducts] = useState([])

  const FALLBACK_PRODUCTS = [
    { product_id: 10001, product_name: 'iPhone 14', brand: 'Apple' },
    { product_id: 10002, product_name: 'Samsung Galaxy S23', brand: 'Samsung' },
    { product_id: 10003, product_name: 'Dell Inspiron 15', brand: 'Dell' },
    { product_id: 10004, product_name: 'Redmi Note 12', brand: 'Xiaomi' },
    { product_id: 10005, product_name: 'Amul Milk 1L', brand: 'Amul' },
  ]
  const FALLBACK_SHOPS = [
    { shop_id: 20001, shop_name: 'DB Mall Electronics', city: 'Bhopal', area: 'Arera Hills' },
    { shop_id: 20002, shop_name: 'New Market Grocers', city: 'Bhopal', area: 'New Market' },
    { shop_id: 20003, shop_name: 'MP Nagar Tech Hub', city: 'Bhopal', area: 'MP Nagar Zone 1' },
  ]

  const search = async () => {
    setLoading(true)
    setSearchError('')
    try {
      if (type === 'product') {
        if (city.trim()) {
          const res = await axios.get(`${API_BASE}/products/in_city`, { params: { city, q } })
          // For city-filtered product search, do not fallback; show empty state instead
          setResults(res.data || [])
          return
        }
        const userId = localStorage.getItem('user_id')
        if (lat != null && lon != null) {
          const res = await axios.get(`${API_BASE}/search/products_nearby`, { params: { q, lat, lon, radius_km: radiusKm } })
          setResults(res.data?.length ? res.data : FALLBACK_PRODUCTS)
        } else {
          const res = await axios.get(`${API_BASE}/search/products`, { params: { q, user_id: userId || undefined } })
          setResults(res.data?.length ? res.data : FALLBACK_PRODUCTS)
        }
      } else if (type === 'category') {
        const res = await axios.get(`${API_BASE}/search/categories`, { params: { q } })
        setResults(res.data?.length ? res.data : FALLBACK_PRODUCTS)
      } else if (type === 'shop') {
        if (city.trim()) {
          const res = await axios.get(`${API_BASE}/shops/by_city`, { params: { city } })
          setResults(res.data?.length ? res.data : FALLBACK_SHOPS)
        } else {
          const res = await axios.get(`${API_BASE}/search/shops`, { params: { q } })
          setResults(res.data?.length ? res.data : FALLBACK_SHOPS)
        }
      }
    } catch (e) {
      // Show error and fallback for non-city searches
      setSearchError(e?.response?.data?.detail || 'Failed to fetch search results')
      if (type === 'product' && city.trim()) {
        setResults([])
      } else {
        setResults(type === 'shop' ? FALLBACK_SHOPS : FALLBACK_PRODUCTS)
      }
    } finally {
      setLoading(false)
    }
  }

  const useLocation = () => {
    // Reuse stored location if available
    const storedLat = localStorage.getItem('loc_lat')
    const storedLon = localStorage.getItem('loc_lon')
    if (storedLat && storedLon) {
      const latitude = Number(storedLat)
      const longitude = Number(storedLon)
      setLat(latitude)
      setLon(longitude)
      ;(async () => {
        try {
          const res = await axios.get(`${API_BASE}/shops/nearby`, { params: { lat: latitude, lon: longitude, radius_km: radiusKm } })
          setNearbyShops(res.data || [])
          const pop = await axios.get(`${API_BASE}/search/popular`, { params: { lat: latitude, lon: longitude, radius_km: radiusKm } })
          setPopularProducts(pop.data || [])
        } catch {}
      })()
      return
    }
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const { latitude, longitude } = pos.coords
      setLat(latitude)
      setLon(longitude)
      // Persist to localStorage for reuse
      localStorage.setItem('loc_lat', String(latitude))
      localStorage.setItem('loc_lon', String(longitude))
      localStorage.setItem('loc_enabled', 'true')
      try {
        const res = await axios.get(`${API_BASE}/shops/nearby`, { params: { lat: latitude, lon: longitude, radius_km: radiusKm } })
        setNearbyShops(res.data || [])
        const pop = await axios.get(`${API_BASE}/search/popular`, { params: { lat: latitude, lon: longitude, radius_km: radiusKm } })
        setPopularProducts(pop.data || [])
      } catch {}
    })
  }

  // Auto-detect location and load nearby products when visiting the Products page
  useEffect(() => {
    if (defaultType === 'product') {
      useLocation()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // When we obtain location or change radius/type, refresh nearby product results automatically
  useEffect(() => {
    if (type === 'product') {
      if (lat != null && lon != null) {
        search()
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lat, lon, radiusKm, type])

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px]">
        <div className="rounded-2xl bg-white text-black p-8 md:p-12 shadow-sm">
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight">Find Local Products Near You</h1>
          <p className="mt-3 text-gray-800 text-lg">Search and compare prices from nearby shops. Enter a city to browse anywhere.</p>
          <div className="mt-6 flex gap-2 flex-wrap items-center">
            <select className="rounded-lg bg-[#EAF0FF] text-black px-3 py-2 border" value={type} onChange={e=>setType(e.target.value)}>
              <option value="product">Product</option>
              <option value="category">Category</option>
              <option value="shop">Shop</option>
            </select>
            <input className="flex-1 rounded-lg px-4 py-2 bg-[#EAF0FF] text-black placeholder:text-gray-600 border" placeholder={`What are you looking for?`} value={q} onChange={e=>setQ(e.target.value)} />
            <input className="rounded-lg px-4 py-2 bg-[#EAF0FF] text-black placeholder:text-gray-600 border" placeholder="Search by City" value={city} onChange={e=>setCity(e.target.value)} />
            <button className="px-5 py-2 rounded-lg bg-white text-black font-semibold border" onClick={search}>{loading ? 'Searching...' : 'Search'}</button>
            <div className="flex items-center gap-2">
              <label className="text-black font-semibold">Radius: {radiusKm} km</label>
              <input type="range" min="1" max="50" value={radiusKm} onChange={e=>setRadiusKm(Number(e.target.value))} />
            </div>
            <button className="px-4 py-2 rounded-lg bg-[#EAF0FF] text-black border" onClick={useLocation}>Use my location</button>
          </div>
          <div className="mt-4 text-sm text-gray-700">
            For shopkeepers: <button className="underline text-primary" onClick={()=>navigate('/shops/add-product')}>Add your products</button>
          </div>
        </div>
      </section>
        {popularProducts.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold">Popular Near You</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
              {popularProducts.map((item, idx) => (
                <div key={item.product_id || idx} className="relative rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px] overflow-hidden hover:from-primary/20 hover:to-accent/20 transition">
                  <div className="rounded-2xl bg-white shadow-sm hover:shadow-xl">
                    {item.image_url ? (
                      <img src={item.image_url} alt="popular product" className="h-44 w-full object-cover" />
                    ) : (
                      <div className="h-44 w-full bg-gray-100 flex items-center justify-center text-3xl font-bold text-gray-400">
                        {(item.product_name || '?').slice(0,1).toUpperCase()}
                      </div>
                    )}
                    <div className="p-4">
                      <div className="font-semibold">{item.product_name}</div>
                      <div className="text-sm text-gray-600">{item.brand || ''}</div>
                    </div>
                    <div className="p-4 pt-0">
                      <button className="px-3 py-1 rounded-md bg-primary text-white" onClick={()=>navigate(`/products/${item.product_id}`)}>View Prices</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        

      {/* Results */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Search Results</h2>
        {loading && <div className="text-sm text-gray-700">Loading...</div>}
        {searchError && <div className="text-sm text-red-600">{searchError}</div>}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {(results || []).map((item, idx) => (
            <div
              key={item.product_id || item.shop_id || idx}
              className="group relative rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px] overflow-hidden hover:from-primary/20 hover:to-accent/20 transition"
              onClick={() => {
                if (item.shop_id) navigate(`/shops/${item.shop_id}`)
              }}
              role={item.shop_id ? 'button' : undefined}
              tabIndex={item.shop_id ? 0 : undefined}
            >
              <div className="rounded-2xl bg-[#EAF0FF] shadow-sm group-hover:shadow-xl text-gray-900">
                {item.image_url || item.shop_image ? (
                  <img src={item.image_url || item.shop_image} alt="thumbnail" className="h-44 w-full object-cover" />
                ) : (
                  <div className="h-44 w-full bg-gray-100 flex items-center justify-center text-3xl font-bold text-gray-400">
                    {(item.product_name || item.shop_name || '?').slice(0,1).toUpperCase()}
                  </div>
                )}
                <div className="p-4">
                  <div className="font-bold text-black flex items-center gap-2">
                    {item.product_name || item.shop_name}
                    {type === 'product' && city.trim() && item.city && (
                      <span className="text-xs px-2 py-1 rounded-full bg-white border text-black">{item.city}</span>
                    )}
                  </div>
                  <div className="text-sm text-gray-800">{item.brand || `${item.city || ''} ${item.area || ''}`}</div>
                </div>
                <div className="mt-2 flex gap-2 p-4 pt-0">
                  {item.product_id && (
                    <button className="px-3 py-1 rounded-md bg-white text-black border" onClick={(e)=>{e.stopPropagation(); navigate(`/products/${item.product_id}`)}}>View Prices</button>
                  )}
                  {item.shop_id && (
                    <button className="px-3 py-1 rounded-md bg-white text-black border" onClick={(e)=>{e.stopPropagation(); navigate(`/shops/${item.shop_id}`)}}>View Shop</button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        {nearbyShops.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold">Nearby Shops</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
              {nearbyShops.map(s => (
                <div key={s.shop_id} className="relative rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 p-[1px] overflow-hidden hover:from-primary/20 hover:to-accent/20 transition">
                  <div className="rounded-2xl bg-[#EAF0FF] shadow-sm hover:shadow-xl text-gray-900">
                    {s.shop_image ? (
                      <img src={s.shop_image} alt="shop banner" className="h-44 w-full object-cover" />
                    ) : (
                      <div className="h-44 bg-gray-100 flex items-center justify-center text-3xl font-bold text-gray-400">
                        {(s.shop_name || '?').slice(0,1).toUpperCase()}
                      </div>
                    )}
                    <div className="p-4">
                      <div className="font-semibold">{s.shop_name}</div>
                      <div className="text-sm text-gray-800">{s.city || ''} {s.area || ''}</div>
                    </div>
                    <div className="p-4 pt-0">
                      <button className="px-3 py-1 rounded-md border" onClick={()=>navigate(`/shops/${s.shop_id}`)}>View Shop</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {!loading && results.length === 0 && (
          <div className="text-gray-600">
            {type === 'product' && city.trim()
              ? `No products available in ${city}`
              : 'No results found. Try a different keyword.'}
          </div>
        )}
      </section>
    </div>
  )
}