import React from 'react';
import { SearchTask } from '../services/asyncNewsService';
import './SearchProgress.css';

interface SearchProgressProps {
  task: SearchTask;
  onCancel?: () => void;
  showDetails?: boolean;
}

const SearchProgress: React.FC<SearchProgressProps> = ({
  task,
  onCancel,
  showDetails = true
}) => {
  const getStatusIcon = () => {
    switch (task.status) {
      case 'started':
        return (
          <svg className="status-icon loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 2v4"/>
            <path d="m16.2 7.8 2.9-2.9"/>
            <path d="M18 12h4"/>
            <path d="m16.2 16.2 2.9 2.9"/>
            <path d="M12 18v4"/>
            <path d="m4.9 19.1 2.9-2.9"/>
            <path d="M2 12h4"/>
            <path d="m4.9 4.9 2.9 2.9"/>
          </svg>
        );
      case 'fetching_articles':
        return (
          <svg className="status-icon loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
        );
      case 'filtering_articles':
        return (
          <svg className="status-icon loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
          </svg>
        );
      case 'fetching_content':
        return (
          <svg className="status-icon loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14,2 14,8 20,8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10,9 9,9 8,9"/>
          </svg>
        );
      case 'generating_summaries':
        return (
          <svg className="status-icon loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
        );
      case 'completed':
        return (
          <svg className="status-icon success" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="20,6 9,17 4,12"/>
          </svg>
        );
      case 'error':
        return (
          <svg className="status-icon error" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
        );
      case 'cancelled':
        return (
          <svg className="status-icon cancelled" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
        );
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (task.status) {
      case 'started':
        return '正在初始化...';
      case 'fetching_articles':
        return '正在搜尋新聞...';
      case 'filtering_articles':
        return '正在過濾文章...';
      case 'fetching_content':
        return '正在抓取內容...';
      case 'generating_summaries':
        return '正在生成摘要...';
      case 'completed':
        return '搜尋完成';
      case 'error':
        return '搜尋失敗';
      case 'cancelled':
        return '已取消';
      default:
        return task.status;
    }
  };

  const getProgressColor = () => {
    if (task.status === 'completed') return '#52c41a';
    if (task.status === 'error') return '#ff4d4f';
    if (task.status === 'cancelled') return '#d9d9d9';
    return '#1890ff';
  };

  return (
    <div className={`search-progress ${task.status}`}>
      <div className="progress-header">
        <div className="progress-status">
          {getStatusIcon()}
          <span className="status-text">{getStatusText()}</span>
        </div>
        
        {task.status !== 'completed' && task.status !== 'error' && task.status !== 'cancelled' && onCancel && (
          <button className="cancel-button" onClick={onCancel} title="取消搜尋">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        )}
      </div>

      <div className="progress-bar-container">
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ 
              width: `${task.progress}%`,
              backgroundColor: getProgressColor()
            }}
          />
        </div>
        <span className="progress-percentage">{task.progress}%</span>
      </div>

      <div className="progress-message">
        {task.message}
      </div>

      {showDetails && (
        <div className="progress-details">
          <div className="detail-item">
            <span className="detail-label">搜尋關鍵字:</span>
            <span className="detail-value">{task.query}</span>
          </div>
          
          {task.total_processed !== undefined && (
            <div className="detail-item">
              <span className="detail-label">已處理:</span>
              <span className="detail-value">{task.total_processed} 篇</span>
            </div>
          )}
          
          {task.total_found !== undefined && (
            <div className="detail-item">
              <span className="detail-label">找到:</span>
              <span className="detail-value">{task.total_found} 篇</span>
            </div>
          )}
          
          {task.status === 'completed' && task.articles && (
            <div className="detail-item">
              <span className="detail-label">新增文章:</span>
              <span className="detail-value">{task.articles.length} 篇</span>
            </div>
          )}
          
          {task.error && (
            <div className="detail-item error">
              <span className="detail-label">錯誤:</span>
              <span className="detail-value">{task.error}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchProgress;