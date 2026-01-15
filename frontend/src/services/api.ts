import axios from 'axios';

// Получаем URL из переменных окружения или используем дефолтные
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002';
const AUTH_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost:5000';
const COLLECTOR_URL = import.meta.env.VITE_COLLECTOR_URL || 'http://localhost:5001';

// Создаём экземпляры axios для каждого сервиса
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const authClient = axios.create({
  baseURL: AUTH_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const collectorClient = axios.create({
  baseURL: COLLECTOR_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем токен к каждому запросу
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

authClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

collectorClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API методы
export const api = {
  // Auth Service
  auth: {
    login: (username: string, password: string) =>
      authClient.post('/login', { username, password }),
    register: (username: string, email: string, password: string) =>
      authClient.post('/register', { username, email, password }),
    logout: () => authClient.post('/logout'),
  },

  // API Service
  reviews: {
    getAll: () => apiClient.get('/reviews'),
    getById: (id: string) => apiClient.get(`/reviews/${id}`),
    getStats: () => apiClient.get('/reviews/stats'),
  },

  analytics: {
    getSentiment: () => apiClient.get('/analytics/sentiment'),
    getTrends: () => apiClient.get('/analytics/trends'),
  },

  // Collector Service
  collector: {
    startCollection: (data: any) => collectorClient.post('/collect', data),
    getStatus: () => collectorClient.get('/status'),
    getTasks: () => collectorClient.get('/tasks'),
  },
};

export default api;