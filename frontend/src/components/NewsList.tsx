import React, { useState, useEffect } from 'react';
import NewsCard from './NewsCard';
import { newsService, NewsItem } from '../services/api';
import './NewsList.css';

const NewsList: React.FC = () => {
  const [newsList, setNewsList] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fetchingNew, setFetchingNew] = useState(false);

  useEffect(() => {
    loadNews();
  }, []);

  const loadNews = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await newsService.getNews(20);
      setNewsList(data);
    } catch (err) {
      setError('無法載入新聞，請稍後再試');
      console.error('Error loading news:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchNewNews = async () => {
    try {
      setFetchingNew(true);
      setError(null);
      await newsService.fetchNews('台灣');
      await loadNews();
    } catch (err) {
      setError('無法抓取新聞，請檢查 API 設定');
      console.error('Error fetching news:', err);
    } finally {
      setFetchingNew(false);
    }
  };

  const fetchHeadlines = async () => {
    try {
      setFetchingNew(true);
      setError(null);
      await newsService.fetchHeadlines(true);
      await loadNews();
    } catch (err) {
      setError('無法抓取頭條新聞，請檢查 API 設定');
      console.error('Error fetching headlines:', err);
    } finally {
      setFetchingNew(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>載入中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-message">{error}</p>
        <button onClick={loadNews} className="retry-button">
          重試
        </button>
      </div>
    );
  }

  return (
    <div className="news-list-container">
      <div className="news-list-header">
        <h2>最新新聞摘要</h2>
        <div className="header-actions">
          <button 
            onClick={fetchHeadlines} 
            disabled={fetchingNew}
            className="fetch-button"
          >
            {fetchingNew ? '抓取中...' : '台灣頭條'}
          </button>
          <button 
            onClick={fetchNewNews} 
            disabled={fetchingNew}
            className="fetch-button secondary"
          >
            {fetchingNew ? '抓取中...' : '搜尋新聞'}
          </button>
          <button 
            onClick={loadNews} 
            className="refresh-button"
          >
            重新整理
          </button>
        </div>
      </div>
      
      {newsList.length === 0 ? (
        <div className="empty-state">
          <p>目前沒有新聞</p>
          <button onClick={fetchHeadlines} className="fetch-button">
            抓取台灣頭條新聞
          </button>
        </div>
      ) : (
        <div className="news-list">
          {newsList.map((news) => (
            <NewsCard key={news.id} news={news} />
          ))}
        </div>
      )}
    </div>
  );
};

export default NewsList;