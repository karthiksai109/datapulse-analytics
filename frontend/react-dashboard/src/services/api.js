import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';
const FASTAPI_URL = process.env.REACT_APP_FASTAPI_URL || '/api/v1';
const FLASK_AI_URL = process.env.REACT_APP_FLASK_AI_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/users/token/refresh/`, {
          refresh: refreshToken,
        });
        localStorage.setItem('access_token', response.data.access);
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const fastApi = axios.create({
  baseURL: FASTAPI_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

export const aiApi = axios.create({
  baseURL: FLASK_AI_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

export default api;
