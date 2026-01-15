import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002/api';
const AUTH_BASE_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost:5000/api/auth';
const COLLECTOR_BASE_URL = import.meta.env.VITE_COLLECTOR_URL || 'http://localhost:5001/api/collect';

class ApiService {
  private api: AxiosInstance;
  private authApi: AxiosInstance;
  private collectorApi: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
    });

    this.authApi = axios.create({
      baseURL: AUTH_BASE_URL,
    });

    this.collectorApi = axios.create({
      baseURL: COLLECTOR_BASE_URL,
    });

    // Interceptor для добавления токена
    const addTokenInterceptor = (config: any) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    };

    this.api.interceptors.request.use(addTokenInterceptor, (error) => Promise.reject(error));
    this.authApi.interceptors.request.use(addTokenInterceptor, (error) => Promise.reject(error));
    this.collectorApi.interceptors.request.use(addTokenInterceptor, (error) => Promise.reject(error));

    // Interceptor для обработки ошибок
    const errorInterceptor = (error: any) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    };

    this.api.interceptors.response.use((response) => response, errorInterceptor);
    this.authApi.interceptors.response.use((response) => response, errorInterceptor);
    this.collectorApi.interceptors.response.use((response) => response, errorInterceptor);
  }

  // Auth methods
  async login(email: string, password: string) {
    const response = await this.authApi.post('/login', { email, password });
    return response.data;
  }

  async register(username: string, email: string, password: string) {
    const response = await this.authApi.post('/register', { username, email, password });
    return response.data;
  }

  async logout() {
    const response = await this.authApi.post('/logout');
    return response.data;
  }

  // Analytics methods
  async getSentimentStatistics(query?: string, source?: string) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (source) params.append('source', source);
    const response = await this.api.get(`/statistics/sentiment?${params}`);
    return response.data;
  }

  async getProcessedPosts(filters: {
    query?: string;
    sentiment?: string;
    source?: string;
    limit?: number;
    skip?: number;
  }) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) params.append(key, String(value));
    });
    const response = await this.api.get(`/posts/processed?${params}`);
    return response.data;
  }

  async getAnalyticsOverview(query?: string) {
    const params = query ? `?query=${query}` : '';
    const response = await this.api.get(`/analytics/overview${params}`);
    return response.data;
  }

  async getKeywordAnalysis(query?: string, sentiment?: string, limit?: number) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (sentiment) params.append('sentiment', sentiment);
    if (limit) params.append('limit', String(limit));
    const response = await this.api.get(`/analytics/keywords?${params}`);
    return response.data;
  }

  async getEntityAnalysis(query?: string, limit?: number) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (limit) params.append('limit', String(limit));
    const response = await this.api.get(`/analytics/entities?${params}`);
    return response.data;
  }

  async exportToCSV(query?: string, sentiment?: string) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (sentiment) params.append('sentiment', sentiment);
    const response = await this.api.get(`/export/csv?${params}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Collection methods
  async startCollection(keywords: string[], sources: string[]) {
    const response = await this.collectorApi.post('/start', { keywords, sources });
    return response.data;
  }

  async getCollectionStatus(taskId: string) {
    const response = await this.collectorApi.get(`/status/${taskId}`);
    return response.data;
  }
}

export default new ApiService();