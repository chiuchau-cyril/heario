import React, { useEffect } from 'react';
import { NewsItem } from '../services/api';
import './NewsModal.css';

interface NewsModalProps {
  news: NewsItem | null;
  isOpen: boolean;
  onClose: () => void;
  onAddToPlaylist?: (news: NewsItem) => void;
  isInPlaylist?: boolean;
}

const NewsModal: React.FC<NewsModalProps> = ({ 
  news, 
  isOpen, 
  onClose, 
  onAddToPlaylist, 
  isInPlaylist = false 
}) => {
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscKey);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !news) {
    return null;
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      weekday: 'long',
    });
  };

  const handleBackdropClick = (event: React.MouseEvent) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  // 清理和格式化原始內容
  const handleAddToPlaylist = () => {
    if (onAddToPlaylist && news) {
      onAddToPlaylist(news);
    }
  };

  const formatOriginalContent = (content: string) => {
    if (!content) return '';
    
    // 移除 Jina AI 的元數據標頭
    const lines = content.split('\n');
    let contentStarted = false;
    const cleanLines: string[] = [];
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      
      // 跳過元數據行
      if (trimmedLine.startsWith('Title:') || 
          trimmedLine.startsWith('URL Source:') || 
          trimmedLine.startsWith('Published Time:') || 
          trimmedLine.startsWith('Markdown Content:') ||
          trimmedLine === '===============') {
        continue;
      }
      
      // 開始處理實際內容
      if (!contentStarted && trimmedLine.length > 0) {
        contentStarted = true;
      }
      
      if (contentStarted && trimmedLine.length > 0) {
        cleanLines.push(trimmedLine);
      }
    }
    
    return cleanLines.join('\n').substring(0, 3000) + (cleanLines.join('\n').length > 3000 ? '...' : '');
  };

  return (
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">{news.title}</h2>
          <button className="modal-close-button" onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className="modal-body">
          <div className="modal-meta">
            <span className="modal-date">{formatDate(news.created_at)}</span>
            {news.source && (
              <span className="modal-source">來源：{news.source}</span>
            )}
          </div>
          
          <div className="modal-section">
            <h3>新聞摘要</h3>
            <p className="modal-summary">{news.summary}</p>
          </div>
          
          {news.original_content && (
            <div className="modal-section">
              <h3>完整內容</h3>
              <div className="modal-original-content">
                {formatOriginalContent(news.original_content).split('\n').map((paragraph, index) => (
                  paragraph.trim() && (
                    <p key={index} className="content-paragraph">
                      {paragraph}
                    </p>
                  )
                ))}
              </div>
            </div>
          )}
        </div>
        
        <div className="modal-footer">
          {onAddToPlaylist && (
            <button 
              className={`modal-playlist-button ${isInPlaylist ? 'in-playlist' : ''}`}
              onClick={handleAddToPlaylist}
            >
              {isInPlaylist ? (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="20,6 9,17 4,12"/>
                  </svg>
                  已在播放清單
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <line x1="12" y1="5" x2="12" y2="19"/>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                  加入播放清單
                </>
              )}
            </button>
          )}
          <a 
            href={news.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="modal-link-button"
          >
            閱讀原始新聞
          </a>
          <button className="modal-close-footer-button" onClick={onClose}>
            關閉
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewsModal;