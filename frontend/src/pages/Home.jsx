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
  const [filters, setFilters] = useState({ minPrice: '', maxPrice: '', brand: '', sortBy: 'relevance' })
  const [locationEnabled, setLocationEnabled] = useState(false)

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
          const res = await axios.get('/api/products/in_city', { params: { city, q } })
          // For city-filtered product search, do not fallback; show empty state instead
          setResults(processResults(res.data || []))
          return
        }
        const userId = localStorage.getItem('user_id')
        if (locationEnabled && lat != null && lon != null) {
          const res = await axios.get('/api/search/products_nearby', { params: { q, lat, lon, radius_km: radiusKm } })
          let items = res.data || []
          if (!items.length) {
            const resGlobal = await axios.get('/api/search/products', { params: { q } })
            items = resGlobal.data || []
          }
          setResults(processResults(items.length ? items : FALLBACK_PRODUCTS))
        } else {
          const res = await axios.get('/api/search/products', { params: { q, user_id: userId || undefined } })
          const items = res.data?.length ? res.data : FALLBACK_PRODUCTS
          setResults(processResults(items))
        }
      } else if (type === 'category') {
        const res = await axios.get('/api/search/categories', { params: { q } })
        const items = res.data?.length ? res.data : FALLBACK_PRODUCTS
        setResults(processResults(items))
      } else if (type === 'shop') {
        if (city.trim()) {
          const res = await axios.get('/api/shops/by_city', { params: { city } })
          setResults(processResults(res.data || []))
        } else {
          const res = await axios.get('/api/search/shops', { params: { q } })
          const items = res.data?.length ? res.data : FALLBACK_SHOPS
          setResults(processResults(items))
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

  function processResults(items) {
    const query = (q || '').trim().toLowerCase()
    const brandFilter = (filters.brand || '').trim().toLowerCase()
    const minP = filters.minPrice ? Number(filters.minPrice) : null
    const maxP = filters.maxPrice ? Number(filters.maxPrice) : null
    const withScores = items.map((item) => {
      let name = (item.product_name || item.shop_name || '').toLowerCase()
      let brand = (item.brand || '').toLowerCase()
      let score = 0
      if (query) {
        if (name === query) score += 5
        else if (name.startsWith(query)) score += 3
        else if (name.includes(query)) score += 1
        if (brand && brand === query) score += 2
      }
      if (city.trim() && (item.city || '').toLowerCase() === city.trim().toLowerCase()) {
        score += 1
      }
      return { ...item, _score: score }
    })
    // Filters: brand and price if present
    const filtered = withScores.filter((i) => {
      if (brandFilter && !((i.brand || '').toLowerCase().includes(brandFilter))) return false
      const price = i.price
      if (minP != null && price != null && price < minP) return false
      if (maxP != null && price != null && price > maxP) return false
      return true
    })
    // Sorting
    const sortBy = filters.sortBy
    const sorted = [...filtered].sort((a, b) => {
      if (sortBy === 'price_asc') {
        const pa = a.price != null ? a.price : Number.POSITIVE_INFINITY
        const pb = b.price != null ? b.price : Number.POSITIVE_INFINITY
        return pa - pb
      } else if (sortBy === 'price_desc') {
        const pa = a.price != null ? a.price : Number.NEGATIVE_INFINITY
        const pb = b.price != null ? b.price : Number.NEGATIVE_INFINITY
        return pb - pa
      } else if (sortBy === 'name') {
        const na = (a.product_name || a.shop_name || '').toLowerCase()
        const nb = (b.product_name || b.shop_name || '').toLowerCase()
        return na.localeCompare(nb)
      }
      // relevance
      return (b._score || 0) - (a._score || 0)
    })
    return sorted
  }

  const useLocation = () => {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const { latitude, longitude } = pos.coords
      setLat(latitude)
      setLon(longitude)
      setLocationEnabled(true)
      try {
        const res = await axios.get('/api/shops/nearby', { params: { lat: latitude, lon: longitude, radius_km: radiusKm } })
        setNearbyShops(res.data || [])
      } catch {}
    })
  }

  // Do not auto-detect location; only use when user explicitly enables via browser

  // When we obtain location or change radius/type, refresh nearby product results automatically
  useEffect(() => {
    if (type === 'product' && locationEnabled) {
      if (lat != null && lon != null) {
        search()
      }
    }
  }, [lat, lon, radiusKm, type, locationEnabled])

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="rounded-2xl bg-black p-[1px]">
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
            <select className="rounded-lg bg-[#EAF0FF] text-black px-3 py-2 border" value={filters.sortBy} onChange={e=>setFilters({...filters, sortBy: e.target.value})}>
              <option value="relevance">Sort: Relevance</option>
              <option value="price_asc">Sort: Price ↑</option>
              <option value="price_desc">Sort: Price ↓</option>
              <option value="name">Sort: Name</option>
            </select>
            <input className="rounded-lg px-4 py-2 bg-[#EAF0FF] text-black placeholder:text-gray-600 border" placeholder="Filter by brand" value={filters.brand} onChange={e=>setFilters({...filters, brand: e.target.value})} />
            <input className="w-28 rounded-lg px-3 py-2 bg-[#EAF0FF] text-black border" placeholder="Min ₹" value={filters.minPrice} onChange={e=>setFilters({...filters, minPrice: e.target.value})} />
            <input className="w-28 rounded-lg px-3 py-2 bg-[#EAF0FF] text-black border" placeholder="Max ₹" value={filters.maxPrice} onChange={e=>setFilters({...filters, maxPrice: e.target.value})} />
          </div>
          <div className="mt-4 text-sm text-gray-700">
            For shopkeepers: <button className="underline text-primary" onClick={()=>navigate('/shops/add-product')}>Add your products</button>
          </div>
        </div>
      </section>
        {/* Popular products section removed per requirements */}
        

      {/* Results */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Search Results</h2>
        {loading && <div className="text-sm text-gray-700">Loading...</div>}
        {searchError && <div className="text-sm text-red-600">{searchError}</div>}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {([...new Map((results || []).map(r => [r.product_id || r.shop_id || `${Math.random()}`, r])).values()]).map((item, idx) => (
            <div
              key={item.product_id || item.shop_id || idx}
              className="group relative rounded-2xl bg-black p-[1px] overflow-hidden transition"
              onClick={() => {
                if (item.shop_id) navigate(`/shops/${item.shop_id}`)
              }}
              role={item.shop_id ? 'button' : undefined}
              tabIndex={item.shop_id ? 0 : undefined}
            >
              <div className="rounded-2xl bg-[#EAF0FF] shadow-sm group-hover:shadow-xl text-gray-900">
                {item.image_url || item.shop_image ? (
                  <img src={item.image_url || item.shop_image} alt="thumbnail" className="h-44 w-full object-cover" loading="lazy" decoding="async" />
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
                  <div className="text-sm text-black font-semibold">{item.brand || `${item.city || ''} ${item.area || ''}`}</div>
                  {type === 'product' && (
                    <div className="text-sm font-bold text-black">Color: {item.color || '—'}</div>
                  )}
                  {item.price != null && (
                    <div className="mt-1 text-[18px] leading-6 font-bold text-black transition-all duration-200 group-hover:bg-yellow-200 group-hover:scale-[1.03] inline-block rounded px-2">₹{item.price}</div>
                  )}
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
        {locationEnabled && nearbyShops.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold">Nearby Shops</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
              {[...new Map(nearbyShops.map(s => [s.shop_id || `${Math.random()}`, s])).values()].map(s => (
                <div key={s.shop_id} className="relative rounded-2xl bg-black p-[1px] overflow-hidden transition">
                  <div className="rounded-2xl bg-[#EAF0FF] shadow-sm hover:shadow-xl text-gray-900">
                    {s.shop_image ? (
                      <img src={s.shop_image} alt="shop banner" className="h-44 w-full object-cover" loading="lazy" decoding="async" />
                    ) : (
                      <div className="h-44 bg-gray-100 flex items-center justify-center text-3xl font-bold text-gray-400">
                        {(s.shop_name || '?').slice(0,1).toUpperCase()}
                      </div>
                    )}
                    <div className="p-4">
                      <div className="font-bold text-black">{s.shop_name}</div>
                      <div className="text-sm text-black font-semibold">{s.city || ''} {s.area || ''}</div>
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
              : (type === 'shop' && city.trim() ? `No shops available in ${city}` : 'No results found. Try a different keyword.')}
          </div>
        )}
      </section>
    </div>
  )
}
