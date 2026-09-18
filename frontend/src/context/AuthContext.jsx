import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { loginUser, registerUser, logoutUser, getMe } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);   // { name, email }
  const [loading, setLoading] = useState(true);   // hydrating from localStorage

  // ── Hydrate on mount ────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem('admission_token');
    if (!token) { setLoading(false); return; }
    getMe(token)
      .then((u) => setUser(u))
      .catch(() => localStorage.removeItem('admission_token'))
      .finally(() => setLoading(false));
  }, []);

  // ── Actions ─────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    const data = await loginUser(email, password);   // throws on error
    localStorage.setItem('admission_token', data.token);
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (name, email, password) => {
    await registerUser(name, email, password);       // throws on error
    // auto-login after register
    return login(email, password);
  }, [login]);

  const logout = useCallback(async () => {
    const token = localStorage.getItem('admission_token');
    if (token) {
      await logoutUser(token).catch(() => {});
      localStorage.removeItem('admission_token');
    }
    setUser(null);
  }, []);

  const getToken = useCallback(() => localStorage.getItem('admission_token'), []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
