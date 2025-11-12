import React, { useEffect, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import axios from 'axios'

export function RequireUserAuth({ children }) {
  const location = useLocation()
  const [ok, setOk] = useState(null)
  useEffect(() => {
    let active = true
    const check = async () => {
      try {
        await axios.get('/api/users/me')
        if (active) setOk(true)
      } catch {
        if (active) setOk(false)
      }
    }
    check()
    return () => { active = false }
  }, [location.pathname])
  if (ok === null) return <div className="p-4">Checking authentication…</div>
  if (!ok) return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace />
  return children
}

export function RequireOwnerAuth({ children }) {
  const location = useLocation()
  const [ok, setOk] = useState(null)
  useEffect(() => {
    let active = true
    const check = async () => {
      try {
        await axios.get('/api/owners/me')
        if (active) setOk(true)
      } catch {
        if (active) setOk(false)
      }
    }
    check()
    return () => { active = false }
  }, [location.pathname])
  if (ok === null) return <div className="p-4">Checking authentication…</div>
  if (!ok) return <Navigate to={`/owner/login?redirect=${encodeURIComponent(location.pathname)}`} replace />
  return children
}
