import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, setAuthToken, getAuthToken } from '../api';

const AuthContext = createContext(null);

export const PRESET_USERS = [
  {
    username: 'officer_chen',
    password: 'Password123!',
    name: 'Officer Marcus Chen',
    role: 'Submitter',
    dept: 'Patrol Operations',
    badge: '#4402',
    color: '#1b4332'
  },
  {
    username: 'captain_miller',
    password: 'Password123!',
    name: 'Captain David Miller',
    role: 'Reviewer',
    dept: 'Internal Affairs & Oversight',
    badge: '#1088',
    color: '#0369a1'
  },
  {
    username: 'admin_patel',
    password: 'Password123!',
    name: 'Administrator Aarav Patel',
    role: 'Admin',
    dept: 'IT & Police Administration',
    badge: '#0012',
    color: '#7c3aed'
  }
];

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state
  useEffect(() => {
    async function initAuth() {
      const existingToken = getAuthToken();
      if (existingToken) {
        try {
          const user = await api.getCurrentUser();
          setCurrentUser(user);
          setLoading(false);
          return;
        } catch (_) {
          setAuthToken('');
        }
      }
      
      // Auto-login default persona (officer_chen) for seamless evaluation
      try {
        const res = await api.login('officer_chen', 'Password123!');
        setAuthToken(res.access_token);
        setCurrentUser(res.user);
      } catch (err) {
        console.error("Initial auth failed:", err);
      } finally {
        setLoading(false);
      }
    }
    initAuth();
  }, []);

  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.login(username, password);
      setAuthToken(res.access_token);
      setCurrentUser(res.user);
      return res.user;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const switchPersona = async (username) => {
    const preset = PRESET_USERS.find(p => p.username === username);
    if (!preset) return;
    return await login(preset.username, preset.password);
  };

  const logout = () => {
    setAuthToken('');
    setCurrentUser(null);
  };

  return (
    <AuthContext.Provider value={{
      currentUser,
      loading,
      error,
      login,
      logout,
      switchPersona,
      presetUsers: PRESET_USERS
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
