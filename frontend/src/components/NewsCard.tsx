import React, { memo } from 'react';
import { NewsItem } from '../services/api';
import './NewsCard.css';

interface NewsCardProps {
  news: NewsItem;
  onClick?: (news: NewsItem) => void;
  onAddToPlaylist?: (news: NewsItem) => void;
  isInPlaylist?: boolean;
}

const NewsCard: React.FC<NewsCardProps> = ({ 
  news, 
  onClick, 
  onAddToPlaylist, 
  isInPlaylist = false 
}) => {
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

  const handleCardClick = () => {
    if (onClick) {
      onClick(news);
    }
  };

  const handleLinkClick = (event: React.MouseEvent) => {
    event.stopPropagation(); // 防止觸發卡片點擊事件
  };

  const handleAddToPlaylist = (event: React.MouseEvent) => {
    event.stopPropagation(); // 防止觸發卡片點擊事件
    if (onAddToPlaylist) {
      onAddToPlaylist(news);
    }
  };

  return (
    <div className="news-card" onClick={handleCardClick}>
      <h3 className="news-title">{news.title}</h3>
      <p className="news-summary">{news.summary}</p>
      <div className="news-footer">
        <span className="news-date">{formatDate(news.created_at)}</span>
        <div className="news-actions">
          {onAddToPlaylist && (
            <button
              className={`playlist-btn ${isInPlaylist ? 'in-playlist' : ''}`}
              onClick={handleAddToPlaylist}
              title={isInPlaylist ? '已在播放清單' : '加入播放清單'}
            >
              {isInPlaylist ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="20,6 9,17 4,12"/>
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              )}
            </button>
          )}
          <a 
            href={news.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="news-link"
            onClick={handleLinkClick}
          >
            閱讀原文
          </a>
        </div>
      </div>
      {onClick && (
        <div className="card-overlay">
          <span className="click-hint">點擊查看完整內容</span>
        </div>
      )}
    </div>
  );
};

export default memo(NewsCard);