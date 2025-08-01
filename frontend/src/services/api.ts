import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  created_at: string;
}

export const newsService = {
  getNews: async (limit: number = 10): Promise<NewsItem[]> => {
    const response = await api.get(`/news?limit=${limit}`);
    return response.data;
  },

  getNewsById: async (id: string): Promise<NewsItem> => {
    const response = await api.get(`/news/${id}`);
    return response.data;
  },

  fetchNews: async (query: string = '台灣') => {
    const response = await api.post('/news/fetch', { query });
    return response.data;
  },

  fetchHeadlines: async (useSearch: boolean = true, category?: string) => {
    const response = await api.post('/news/headlines', { 
      use_search: useSearch,
      category 
    });
    return response.data;
  },
};

export default api;