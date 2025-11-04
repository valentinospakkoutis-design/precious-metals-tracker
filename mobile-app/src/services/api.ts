import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

// Get API URL from app.json config
const API_URL = Constants.expoConfig?.extra?.apiUrl || 'http://192.168.1.100:8000';
const API_BASE = `${API_URL}/api/v1`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const accessToken = await SecureStore.getItemAsync('access_token');
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }

      // Add CSRF token if available
      const csrfToken = await AsyncStorage.getItem('csrf_token');
      if (csrfToken && ['POST', 'PUT', 'DELETE'].includes(config.method?.toUpperCase() || '')) {
        config.headers['X-CSRF-Token'] = csrfToken;
      }
    } catch (error) {
      console.error('Error adding auth token:', error);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  (response) => {
    // Store CSRF token if present
    const csrfToken = response.headers['x-csrf-token'];
    if (csrfToken) {
      AsyncStorage.setItem('csrf_token', csrfToken);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await SecureStore.getItemAsync('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;

          // Store new tokens
          await SecureStore.setItemAsync('access_token', access_token);
          if (newRefreshToken) {
            await SecureStore.setItemAsync('refresh_token', newRefreshToken);
          }

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        await clearTokens();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Token management
export const storeTokens = async (accessToken: string, refreshToken: string) => {
  await SecureStore.setItemAsync('access_token', accessToken);
  await SecureStore.setItemAsync('refresh_token', refreshToken);
};

export const clearTokens = async () => {
  await SecureStore.deleteItemAsync('access_token');
  await SecureStore.deleteItemAsync('refresh_token');
  await AsyncStorage.removeItem('csrf_token');
  await AsyncStorage.removeItem('user');
};

export const getStoredUser = async () => {
  const userStr = await AsyncStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const storeUser = async (user: any) => {
  await AsyncStorage.setItem('user', JSON.stringify(user));
};

// Auth API
export const authAPI = {
  register: async (email: string, password: string, fullName?: string) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  loginWith2FA: async (email: string, password: string, totpCode: string) => {
    const response = await api.post('/auth/login/2fa', {
      email,
      password,
      totp_code: totpCode,
    });
    return response.data;
  },

  logout: async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      await clearTokens();
    }
  },

  refreshToken: async (refreshToken: string) => {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },
};

// 2FA API
export const twoFactorAPI = {
  enable2FA: async () => {
    const response = await api.post('/auth/2fa/enable');
    return response.data;
  },

  verify2FA: async (secret: string, totpCode: string) => {
    const response = await api.post('/auth/2fa/verify', {
      secret,
      totp_code: totpCode,
    });
    return response.data;
  },

  disable2FA: async (totpCode: string) => {
    const response = await api.post('/auth/2fa/disable', {
      totp_code: totpCode,
    });
    return response.data;
  },
};

// Portfolio API
export const portfolioAPI = {
  getPortfolio: async () => {
    const response = await api.get('/portfolio');
    return response.data;
  },

  buyAsset: async (symbol: string, quantity: number, price: number) => {
    const response = await api.post('/portfolio/buy', {
      symbol,
      quantity,
      price,
    });
    return response.data;
  },

  sellAsset: async (symbol: string, quantity: number, price: number) => {
    const response = await api.post('/portfolio/sell', {
      symbol,
      quantity,
      price,
    });
    return response.data;
  },
};

// Prices API
export const priceAPI = {
  getPrice: async (symbol: string) => {
    const response = await api.get(`/price/${symbol}`);
    return response.data;
  },

  getHistoricalPrices: async (symbol: string, period: string) => {
    const response = await api.get(`/prices/${symbol}/historical`, {
      params: { period },
    });
    return response.data;
  },
};

// Predictions API
export const predictionAPI = {
  predict: async (symbol: string) => {
    const response = await api.post(`/predict/${symbol}`);
    return response.data;
  },
};

// News API
export const newsAPI = {
  getNews: async () => {
    const response = await api.get('/news');
    return response.data;
  },
};

// Health API
export const healthAPI = {
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
