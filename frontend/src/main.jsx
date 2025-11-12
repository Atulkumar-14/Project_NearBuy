import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import axios from 'axios'
import { AuthProvider } from './components/AuthProvider.jsx'

// Send cookies with API requests and auto-refresh on 401
axios.defaults.withCredentials = true
axios.interceptors.response.use(
  (res) => res,
  async (error) => {
    const status = error?.response?.status
    const original = error.config
    if (status === 401 && !original?._retry) {
      original._retry = true
      try {
        await axios.post('http://localhost:8000/api/auth/refresh')
        return axios(original)
      } catch (e) {
        // Refresh failed; notify UI and redirect to login
        window.dispatchEvent(new CustomEvent('auth:logout'))
        if (!window.location.pathname.startsWith('/login')) {
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