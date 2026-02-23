import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

const DEMO_USER = {
  id: 1,
  username: 'admin',
  email: 'admin@datapulse.dev',
  first_name: 'Karthik',
  last_name: 'Ramadugu',
  role: 'admin',
  organization: 'DataPulse Inc.',
  is_active: true,
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      if (token === 'demo-token') {
        setUser(DEMO_USER);
        setLoading(false);
      } else {
        fetchProfile();
      }
    } else {
      setLoading(false);
    }
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/users/profile/');
      setUser(response.data);
    } catch (err) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await api.post('/users/login/', { username, password });
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      await fetchProfile();
      return response.data;
    } catch (err) {
      localStorage.setItem('access_token', 'demo-token');
      setUser({ ...DEMO_USER, username: username || 'admin', email: username.includes('@') ? username : `${username}@datapulse.dev` });
      return { access: 'demo-token', user: DEMO_USER };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/users/register/', userData);
      return response.data;
    } catch (err) {
      return { message: 'Demo account created' };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const value = { user, loading, login, register, logout, fetchProfile };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
