import React from 'react';
import { NewsItem } from '../services/api';
import './NewsCard.css';

interface NewsCardProps {
  news: NewsItem;
}

const NewsCard: React.FC<NewsCardProps> = ({ news }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="news-card">
      <h3 className="news-title">{news.title}</h3>
      <p className="news-summary">{news.summary}</p>
      <div className="news-footer">
        <span className="news-date">{formatDate(news.created_at)}</span>
        <a 
          href={news.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="news-link"
        >
          閱讀原文
        </a>
      </div>
    </div>
  );
};

export default NewsCard;