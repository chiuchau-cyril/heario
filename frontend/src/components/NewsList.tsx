import React, { useState, useEffect, useMemo, useCallback } from 'react';
import NewsCard from './NewsCard';
import NewsModal from './NewsModal';
import SearchBar from './SearchBar';
import SmartSearchBar from './SmartSearchBar';
import SearchProgress from './SearchProgress';
import { newsService, NewsItem } from '../services/api';
import { asyncNewsService, SearchTask, PaginatedSearchResult } from '../services/asyncNewsService';
import { Playlist, PlaylistManager } from '../utils/playlistManager';
import { useMasonryLayout } from '../hooks/useMasonryLayout';
import './NewsList.css';

interface NewsListProps {
  searchQuery?: string;
  onSearch?: (query: string) => void;
  onSearchComplete?: (newsCount: number) => void;
  playlist?: Playlist;
  onPlaylistUpdate?: (playlist: Playlist) => void;
  isNewSearchClearing?: boolean;
}

const NewsList: React.FC<NewsListProps> = ({ 
  searchQuery, 
  onSearch, 
  onSearchComplete,
  playlist,
  onPlaylistUpdate,
  isNewSearchClearing = false
}) => {
  const [newsList, setNewsList] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fetchingNew, setFetchingNew] = useState(false);
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  
  // 智能搜尋相關狀態
  const [useSmartSearch, setUseSmartSearch] = useState(true);
  const [currentSearchTask, setCurrentSearchTask] = useState<SearchTask | null>(null);
  const [paginatedResults, setPaginatedResults] = useState<PaginatedSearchResult | null>(null);
  const [backgroundTaskId, setBackgroundTaskId] = useState<string | null>(null);
  const [currentSearchQuery, setCurrentSearchQuery] = useState<string>('');

  // Masonry layout hook
  const useMasonry = true;
  const { containerRef, addItemRef } = useMasonryLayout(newsList, {
    gap: 20,
    minColumnWidth: 200
  });

  useEffect(() => {
    if (searchQuery) {
      performSearch(searchQuery);
    } else if (isNewSearchClearing) {
      // 如果是新搜尋清除，只清空結果，不載入預設新聞
      clearSearchResults();
    }
  }, [searchQuery, isNewSearchClearing]);

  useEffect(() => {
    loadNews();
  }, []);

  const clearSearchResults = () => {
    // 清除搜尋相關狀態但不載入新聞
    setNewsList([]);
    setCurrentSearchQuery('');
    setCurrentSearchTask(null);
    setPaginatedResults(null);
    setBackgroundTaskId(null);
    setError(null);
    setLoading(false);
    setIsSearching(false);
    
    if (onSearchComplete) {
      onSearchComplete(0);
    }
  };

  const loadNews = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // 清除搜尋相關狀態
      setCurrentSearchQuery('');
      setCurrentSearchTask(null);
      setPaginatedResults(null);
      setBackgroundTaskId(null);
      
      const data = await newsService.getNews(20);
      setNewsList(data);
      if (onSearchComplete) {
        onSearchComplete(data.length);
      }
    } catch (err) {
      setError('無法載入新聞，請稍後再試');
      console.error('Error loading news:', err);
    } finally {
      setLoading(false);
    }
  };

  const performSearch = async (query: string) => {
    try {
      setIsSearching(true);
      setError(null);
      
      // 清除舊的搜尋結果和狀態
      setNewsList([]);
      setCurrentSearchTask(null);
      setPaginatedResults(null);
      setBackgroundTaskId(null);
      setCurrentSearchQuery(query);
      
      await newsService.fetchNews(query);
      const data = await newsService.getNews(20);
      setNewsList(data);
      if (onSearchComplete) {
        onSearchComplete(data.length);
      }
    } catch (err) {
      setError(`無法搜尋「${query}」相關新聞`);
      console.error('Error searching news:', err);
    } finally {
      setIsSearching(false);
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
      
      // 清除搜尋相關狀態
      setCurrentSearchQuery('');
      setCurrentSearchTask(null);
      setPaginatedResults(null);
      setBackgroundTaskId(null);
      
      await newsService.fetchHeadlines(true);
      await loadNews();
    } catch (err) {
      setError('無法抓取頭條新聞，請檢查 API 設定');
      console.error('Error fetching headlines:', err);
    } finally {
      setFetchingNew(false);
    }
  };

  const handleNewsClick = (news: NewsItem) => {
    setSelectedNews(news);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedNews(null);
  };

  const handleSearch = async (query: string) => {
    if (onSearch) {
      onSearch(query);
    } else {
      await performSearch(query);
    }
  };

  const handleSmartSearch = async (query: string) => {
    try {
      // 如果有正在進行的背景搜尋，先取消它
      if (backgroundTaskId) {
        try {
          await asyncNewsService.cancelSearchTask(backgroundTaskId);
          console.log('取消了舊的搜尋任務:', backgroundTaskId);
        } catch (err) {
          console.error('取消舊搜尋失敗:', err);
        }
      }
      
      setIsSearching(true);
      setError(null);
      setCurrentSearchTask(null);
      setPaginatedResults(null);
      setBackgroundTaskId(null);
      
      // 清除舊的搜尋結果
      setNewsList([]);
      setCurrentSearchQuery(query);

      console.log('開始智能搜尋:', query);
      
      const result = await asyncNewsService.smartSearch(
        query,
        // 立即結果回調
        (immediateResults) => {
          console.log('收到立即結果:', immediateResults);
          setPaginatedResults(immediateResults);
          setNewsList(immediateResults.articles);
          setBackgroundTaskId(immediateResults.background_task_id || null);
          
          if (onSearchComplete) {
            onSearchComplete(immediateResults.articles.length);
          }
        },
        // 進度回調
        (task) => {
          console.log('搜尋進度更新:', task);
          setCurrentSearchTask(task);
        },
        // 最終結果回調
        (finalTask) => {
          console.log('收到最終結果:', finalTask);
          setCurrentSearchTask(finalTask);
          
          if (finalTask.articles && finalTask.articles.length > 0) {
            // 合併新的文章到現有列表，避免重複
            setNewsList(prevList => {
              const existingIds = new Set(prevList.map(item => item.id));
              const newArticles = finalTask.articles.filter(article => !existingIds.has(article.id));
              return [...prevList, ...newArticles];
            });
            
            if (onSearchComplete) {
              onSearchComplete(finalTask.articles.length);
            }
          }
        }
      );

      console.log('智能搜尋完成:', result);
      
    } catch (err) {
      console.error('智能搜尋失敗:', err);
      setError(`智能搜尋「${query}」失敗`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleCancelSearch = async () => {
    if (backgroundTaskId) {
      try {
        await asyncNewsService.cancelSearchTask(backgroundTaskId);
        setCurrentSearchTask(null);
        setBackgroundTaskId(null);
      } catch (err) {
        console.error('取消搜尋失敗:', err);
      }
    }
  };

  // 建立一個快速查找的 Map 來改善效能
  const playlistNewsIds = useMemo(() => {
    if (!playlist) return new Set<string>();
    return new Set(playlist.items.map(item => item.newsItem.id));
  }, [playlist]);

  const handleAddToPlaylist = useCallback((news: NewsItem) => {
    if (playlist && onPlaylistUpdate) {
      // 直接使用播放清單檢查，避免依賴 playlistNewsIds
      const isInPlaylist = playlist.items.some(item => item.newsItem.id === news.id);
      
      if (isInPlaylist) {
        // 如果已在播放清單中，則移除
        const item = playlist.items.find(item => item.newsItem.id === news.id);
        if (item) {
          const updatedPlaylist = PlaylistManager.removeFromPlaylist(item.id, playlist);
          onPlaylistUpdate(updatedPlaylist);
        }
      } else {
        // 否則添加到播放清單
        const updatedPlaylist = PlaylistManager.addToPlaylist(news, playlist);
        onPlaylistUpdate(updatedPlaylist);
      }
    }
  }, [playlist, onPlaylistUpdate]);

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
      <SmartSearchBar 
        onSearch={handleSearch}
        onSmartSearch={handleSmartSearch}
        loading={isSearching}
        showAdvancedOptions={true}
      />
      
      {/* 搜尋進度顯示 */}
      {currentSearchTask && (
        <SearchProgress 
          task={currentSearchTask}
          onCancel={handleCancelSearch}
          showDetails={true}
        />
      )}

      {/* 分頁結果信息 */}
      {paginatedResults && (
        <div className="paginated-info">
          <div className="info-content">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/>
              <circle cx="12" cy="17" r="1"/>
            </svg>
            {paginatedResults.message}
            {paginatedResults.background_task_id && !currentSearchTask?.status.includes('completed') && (
              <span className="background-notice"> - 正在背景搜尋更多內容</span>
            )}
          </div>
        </div>
      )}

      <div className="news-list-header">
        <h2>{currentSearchQuery ? `「${currentSearchQuery}」搜尋結果` : '最新新聞摘要'}</h2>
        <div className="header-actions">
          <button 
            onClick={fetchHeadlines} 
            disabled={fetchingNew || isSearching}
            className="fetch-button"
          >
            {fetchingNew ? '抓取中...' : '台灣頭條'}
          </button>
          <button 
            onClick={loadNews} 
            className="refresh-button"
          >
            重新整理
          </button>
        </div>
      </div>
      
      {isSearching ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>搜尋中...</p>
        </div>
      ) : newsList.length === 0 ? (
        <div className="empty-state">
          {currentSearchQuery ? (
            <>
              <p>沒有找到「{currentSearchQuery}」相關的新聞</p>
              <button onClick={fetchHeadlines} className="fetch-button">
                抓取台灣頭條新聞
              </button>
            </>
          ) : (
            <>
              <div className="empty-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="M21 21l-4.35-4.35"/>
                </svg>
              </div>
              <p>準備開始搜尋新聞</p>
              <p className="empty-hint">在上方輸入關鍵字開始搜尋，或</p>
              <button onClick={fetchHeadlines} className="fetch-button">
                抓取台灣頭條新聞
              </button>
            </>
          )}
        </div>
      ) : (
        <div className={useMasonry ? "news-list" : "news-list-grid"} ref={useMasonry ? containerRef : undefined}>
          {newsList.map((news, index) => (
            useMasonry ? (
              <div
                key={news.id}
                ref={(el) => addItemRef(el, index)}
              >
                <NewsCard 
                  news={news} 
                  onClick={handleNewsClick}
                  onAddToPlaylist={handleAddToPlaylist}
                  isInPlaylist={playlistNewsIds.has(news.id)}
                />
              </div>
            ) : (
              <NewsCard 
                key={news.id}
                news={news} 
                onClick={handleNewsClick}
                onAddToPlaylist={handleAddToPlaylist}
                isInPlaylist={playlistNewsIds.has(news.id)}
              />
            )
          ))}
        </div>
      )}
      
      <NewsModal
        news={selectedNews}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onAddToPlaylist={handleAddToPlaylist}
        isInPlaylist={selectedNews ? playlistNewsIds.has(selectedNews.id) : false}
      />
    </div>
  );
};

export default NewsList;