import { useEffect, useMemo, useState } from 'react';
import { ACCESS_TOKEN_KEY, apiGet, apiPost } from '../services/Api';
import AuthContext from './authContext';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem(ACCESS_TOKEN_KEY)));
  const [sessionError, setSessionError] = useState('');

  useEffect(() => {
    let active = true;
    if (!localStorage.getItem(ACCESS_TOKEN_KEY)) return () => { active = false; };

    apiGet('/me')
      .then((response) => {
        if (active) {
          setUser(response.data);
          setSessionError('');
        }
      })
      .catch((error) => {
        const invalidToken = error.status === 401 || error.status === 422;
        if (invalidToken) {
          localStorage.removeItem(ACCESS_TOKEN_KEY);
        }
        if (active) {
          setUser(null);
          setSessionError(invalidToken ? '' : error.message);
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const value = useMemo(() => ({
    user,
    loading,
    sessionError,
    async login(email, password) {
      const response = await apiPost('/login', { email, password });
      localStorage.setItem(ACCESS_TOKEN_KEY, response.data.access_token);
      setUser(response.data.user);
      setSessionError('');
      return response.data.user;
    },
    async register(account) {
      return apiPost('/register', account);
    },
    async logout() {
      try {
        if (localStorage.getItem(ACCESS_TOKEN_KEY)) await apiPost('/logout', {});
      } finally {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        setUser(null);
      }
    },
  }), [user, loading, sessionError]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
