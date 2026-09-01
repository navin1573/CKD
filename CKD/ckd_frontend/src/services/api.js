import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });
        
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/token/', data),
  getProfile: () => api.get('/users/profile/'),
};

export const predictionAPI = {
  create: (data) => api.post('/predictions/', data),
  list: () => api.get('/predictions/'),
  get: (id) => api.get(`/predictions/${id}/`),
  downloadPDF: (id) => api.get(`/predictions/${id}/download_pdf/`, {
    responseType: 'blob',
  }),
  batchPredict: (formData) => api.post('/predictions/batch_predict/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
};

export const patientAPI = {
  list: () => api.get('/patients/'),
  get: (id) => api.get(`/patients/${id}/`),
};

export const doctorAPI = {
  list: () => api.get('/doctors/'),
  get: (id) => api.get(`/doctors/${id}/`),
};

export default api;
