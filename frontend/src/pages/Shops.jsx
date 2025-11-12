import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const API_BASE = 'http://localhost:8000/api'

export default function Shops() {
  const [shops, setShops] = useState([])
  const [city, setCity] = useState('')
  const [area, setArea] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const loadNearby = async (lat, lon) => {
    setLoading(true)
    try {
      const res = await axios.get(`${API_BASE}/shops/nearby`, { params: { lat, lon, radius_km: 25 } })
      const data = res.data || []
      if (!data.length) {
        setShops([
          { shop_id: 20001, shop_name: 'DB Mall Electronics', city: 'Bhopal', area: 'Arera Hills', distance_km: 2.1 },
          { shop_id: 20002, shop_name: 'New Market Grocers', city: 'Bhopal', area: 'New Market', distance_km: 3.4 },
          { shop_id: 20003, shop_name: 'MP Nagar Tech Hub', city: 'Bhopal', area: 'MP Nagar Zone 1', distance_km: 1.7 },
        ])
      } else {
        setShops(data)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const storedLat = localStorage.getItem('loc_lat')
    const storedLon = localStorage.getItem('loc_lon')
    if (storedLat && storedLon) {
      loadNearby(Number(storedLat), Number(storedLon))
      return
    }
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          localStorage.setItem('loc_lat', String(pos.coords.latitude))
          localStorage.setItem('loc_lon', String(pos.coords.longitude))
          localStorage.setItem('loc_enabled', 'true')
          loadNearby(pos.coords.latitude, pos.coords.longitude)
        },
        () => {
          const bhopal = { lat: 23.2599, lon: 77.4126 }
          loadNearby(bhopal.lat, bhopal.lon)
        },
        { enableHighAccuracy: true, timeout: 5000 }
      )
    } else {
      const bhopal = { lat: 23.2599, lon: 77.4126 }
      loadNearby(bhopal.lat, bhopal.lon)
    }
  }, [])

  const filtered = useMemo(() => {
    return (shops || []).filter(s => {
      const okCity = city ? (s.city || '').toLowerCase().includes(city.toLowerCase()) : true
      const okArea = area ? (s.area || '').toLowerCase().includes(area.toLowerCase()) : true
      return okCity && okArea
    })
  }, [shops, city, area])

  const clearFilters = () => { setCity(''); setArea('') }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Shops Near You</h1>

      {/* Filters */}
      <div className="rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
          <div>
            <label className="block text-sm font-medium mb-1">City</label>
            <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Filter by city" value={city} onChange={e=>setCity(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Area</label>
            <input className="w-full rounded-lg border p-2 bg-[#EAF0FF] text-black placeholder:text-gray-600" placeholder="Filter by area" value={area} onChange={e=>setArea(e.target.value)} />
          </div>
          <div className="flex gap-2">
            <button className="px-4 py-2 rounded-lg bg-primary text-white" onClick={clearFilters}>Clear Filters</button>
            <button className="px-4 py-2 rounded-lg border" onClick={() => {
              if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(p => loadNearby(p.coords.latitude, p.coords.longitude))
              }
            }}>Use my location</button>
          </div>
        </div>
      </div>

      {/* Cards */}
      {loading && <div>Loading nearby shops...</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map(s => (
          <button key={s.shop_id} onClick={() => navigate(`/shops/${s.shop_id}`)} className="text-left rounded-2xl overflow-hidden bg-white border shadow-sm hover:shadow-md transition">
            {s.shop_image ? (
              <img src={s.shop_image} alt="shop banner" className="h-48 w-full object-cover" />
            ) : (
              <div className="h-48 bg-gray-100 flex items-center justify-center text-4xl font-bold text-gray-400">
                {(s.shop_name || '?').slice(0,1).toUpperCase()}
              </div>
            )}
            <div className="p-4">
              <div className="text-lg font-semibold">{s.shop_name}</div>
              <div className="text-sm text-gray-600">{s.city || ''} {s.area || ''}</div>
              {s.distance_km != null && <div className="mt-1 text-xs text-gray-500">{s.distance_km} km away</div>}
            </div>
          </button>
        ))}
        {filtered.length === 0 && !loading && (
          <div className="text-gray-600">No shops found for selected filters.</div>
        )}
      </div>
    </div>
  )
}