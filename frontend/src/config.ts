export const config = {
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:5002',
  AUTH_URL: import.meta.env.VITE_AUTH_URL || 'http://localhost:5003',
  COLLECTOR_URL: import.meta.env.VITE_COLLECTOR_URL || 'http://localhost:5001',

  APP_NAME: import.meta.env.VITE_APP_NAME || 'Social Media Analytics',
  APP_VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',

  DEFAULT_PAGE_SIZE: 50,
  MAX_SEARCH_RESULTS: 1000,

  endpoints: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    logout: '/api/auth/logout',

    searchCreate: '/api/search/create',
    searchQueries: '/api/search/queries',
    searchHistory: '/api/search/history',

    posts: '/api/posts/processed',
    postsBySearch: '/api/posts/by-search',

    analytics: '/api/analytics/overview',
    keywords: '/api/analytics/keywords',
    entities: '/api/analytics/entities',
    sentiment: '/api/statistics/sentiment',

    exportCSV: '/api/export/csv',

    collect: '/api/collect',
    collectStatus: '/api/collect/status',
    health: '/health'
  }
};

export default config;