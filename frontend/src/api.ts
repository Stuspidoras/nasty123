import axios, { AxiosInstance } from 'axios';

const API_URL = import.meta.env.VITE_API_URL;
const API_URL = import.meta.env.VITE_API_URL;

class ApiService {
  private api: AxiosInstance;
  private authApi: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
    });

    this.authApi = axios.create({
      baseURL: AUTH_BASE_URL,
    });

    // Interceptor для добавления токена
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor для обработки ошибок
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
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
    const response = await axios.post(
      'http://localhost:5001/api/collect/start',
      { keywords, sources },
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    return response.data;
  }

  async getCollectionStatus(taskId: string) {
    const response = await axios.get(
      `http://localhost:5001/api/collect/status/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    return response.data;
  }
}

export default new ApiService();