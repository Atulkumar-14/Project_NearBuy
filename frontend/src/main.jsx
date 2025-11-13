import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import axios from 'axios'
import { AuthProvider } from './components/AuthProvider.jsx'

// Global axios defaults: base URL and credentials
axios.defaults.baseURL = 'http://localhost:8000'
axios.defaults.withCredentials = true
// Persist Authorization across reloads using stored owner/user tokens
try {
  const ownerTok = window.localStorage.getItem('owner_token')
  const userTok = window.localStorage.getItem('access_token')
  const tok = ownerTok || userTok
  if (tok) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${tok}`
  }
} catch {}
let __refreshing = null
axios.interceptors.response.use(
  (res) => res,
  async (error) => {
    const status = error?.response?.status
    const original = error.config || {}
    const url = original.url || ''
    const isProbe = url.endsWith('/api/users/me') || url.endsWith('/api/owners/me')
    const isAuthEndpoint = url.includes('/api/auth/refresh') || url.includes('/api/auth/login') || url.includes('/api/auth/owner/login')
    if (status === 401 && !original._retry && !isProbe && !isAuthEndpoint) {
      original._retry = true
      try {
        __refreshing = __refreshing || axios.post('/api/auth/refresh', {}, { withCredentials: true }).finally(() => { __refreshing = null })
        await __refreshing
        return axios(original)
      } catch (e) {
        window.dispatchEvent(new CustomEvent('auth:logout'))
        const p = window.location.pathname
        if (!p.startsWith('/login') && !p.startsWith('/owner/login')) {
          window.location.assign('/login')
        }
      }
    }
    return Promise.reject(error)
  }
)

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
)
