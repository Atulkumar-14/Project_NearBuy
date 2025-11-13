import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [owner, setOwner] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    let attempts = 0;
    const maxAttempts = 3;
    while (attempts < maxAttempts) {
      try {
        const [userRes, ownerRes] = await Promise.allSettled([
          axios.get('http://localhost:8000/api/users/me', { withCredentials: true }),
          axios.get('http://localhost:8000/api/owners/me', { withCredentials: true }),
        ]);
        if (userRes.status === 'fulfilled') {
          setUser(userRes.value.data);
        } else {
          setUser(null);
        }
        if (ownerRes.status === 'fulfilled') {
          setOwner(ownerRes.value.data);
        } else {
          setOwner(null);
        }
        break; // success or settled
      } catch (e) {
        attempts += 1;
        if (attempts >= maxAttempts) {
          setError(e);
        } else {
          await new Promise(r => setTimeout(r, 500 * attempts));
        }
      }
    }
    setLoading(false);
  }, []);

  const logout = useCallback(async () => {
    try {
      await axios.post('http://localhost:8000/api/auth/logout', {}, { withCredentials: true });
    } catch (_) {
      // ignore
    }
    setUser(null);
    setOwner(null);
    window.localStorage.removeItem('access_token');
    window.localStorage.removeItem('owner_token');
    try { delete axios.defaults.headers.common['Authorization']; } catch {}
    window.dispatchEvent(new CustomEvent('auth:logout'));
  }, []);

  useEffect(() => {
    fetchSession();
    const onLogoutEvent = () => {
      setUser(null);
      setOwner(null);
    };
    window.addEventListener('auth:logout', onLogoutEvent);
    return () => window.removeEventListener('auth:logout', onLogoutEvent);
  }, [fetchSession]);

  const value = {
    user,
    owner,
    loading,
    error,
    refresh: fetchSession,
    logout,
    isAuthenticated: !!user || !!owner,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
