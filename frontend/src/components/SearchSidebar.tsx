import React, { useState, useRef, useEffect } from 'react';
import { SearchSession, SearchHistoryManager } from '../utils/searchHistory';
import './SearchSidebar.css';

interface SearchSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  currentSessionId?: string;
  onSessionSelect: (session: SearchSession) => void;
  onNewSearch: () => void;
}

const SearchSidebar: React.FC<SearchSidebarProps> = ({
  isOpen,
  onToggle,
  currentSessionId,
  onSessionSelect,
  onNewSearch
}) => {
  const [sessions, setSessions] = useState<SearchSession[]>([]);
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [isSearchListCollapsed, setIsSearchListCollapsed] = useState(false);
  const editInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (editingSessionId && editInputRef.current) {
      editInputRef.current.focus();
      editInputRef.current.select();
    }
  }, [editingSessionId]);

  const loadSessions = () => {
    setSessions(SearchHistoryManager.getSessions());
  };

  const handleDeleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    SearchHistoryManager.deleteSession(sessionId);
    loadSessions();
  };

  const handleEditStart = (session: SearchSession, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditingTitle(session.title);
  };

  const handleEditSave = (sessionId: string) => {
    if (editingTitle.trim()) {
      SearchHistoryManager.updateSession(sessionId, { title: editingTitle.trim() });
      loadSessions();
    }
    setEditingSessionId(null);
    setEditingTitle('');
  };

  const handleEditCancel = () => {
    setEditingSessionId(null);
    setEditingTitle('');
  };

  const handleEditKeyDown = (e: React.KeyboardEvent, sessionId: string) => {
    if (e.key === 'Enter') {
      handleEditSave(sessionId);
    } else if (e.key === 'Escape') {
      handleEditCancel();
    }
  };

  const handleClearAll = () => {
    if (window.confirm('確定要清除所有搜尋歷史嗎？')) {
      SearchHistoryManager.clearAllSessions();
      loadSessions();
    }
  };

  const toggleSearchList = () => {
    setIsSearchListCollapsed(!isSearchListCollapsed);
  };

  const groupedSessions = SearchHistoryManager.getSessionsByDate();

  const renderSessionGroup = (title: string, sessions: SearchSession[]) => {
    if (sessions.length === 0) return null;

    return (
      <div className="session-group" key={title}>
        <div className="session-group-title">{title}</div>
        {sessions.map(session => (
          <div
            key={session.id}
            className={`session-item ${currentSessionId === session.id ? 'active' : ''}`}
            onClick={() => onSessionSelect(session)}
          >
            <div className="session-content">
              {editingSessionId === session.id ? (
                <input
                  ref={editInputRef}
                  type="text"
                  value={editingTitle}
                  onChange={(e) => setEditingTitle(e.target.value)}
                  onBlur={() => handleEditSave(session.id)}
                  onKeyDown={(e) => handleEditKeyDown(e, session.id)}
                  className="session-edit-input"
                />
              ) : (
                <>
                  <div className="session-title">{session.title}</div>
                  {session.newsCount !== undefined && (
                    <div className="session-info">{session.newsCount} 則新聞</div>
                  )}
                </>
              )}
            </div>
            
            <div className="session-actions">
              <button
                className="session-action-btn edit-btn"
                onClick={(e) => handleEditStart(session, e)}
                title="編輯名稱"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="m18.5 2.5 3 3-12 12-6 1 1-6 14-14z"/>
                </svg>
              </button>
              <button
                className="session-action-btn delete-btn"
                onClick={(e) => handleDeleteSession(session.id, e)}
                title="刪除"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="3,6 5,6 21,6"/>
                  <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"/>
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <>
      {/* 移動端遮罩 */}
      {isOpen && <div className="sidebar-overlay" onClick={onToggle} />}
      
      <div className={`search-sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <button className="new-search-btn" onClick={onNewSearch}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            新搜尋
          </button>
          
          <button className="sidebar-toggle" onClick={onToggle}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
        </div>

        <div className="search-list-header">
          <button className={`hamburger-toggle ${isSearchListCollapsed ? 'collapsed' : ''}`} onClick={toggleSearchList}>
            {isSearchListCollapsed ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="m9 18 6-6-6-6"/>
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="m6 9 6 6 6-6"/>
              </svg>
            )}
          </button>
          <span className="search-list-title">搜尋記錄</span>
          {sessions.length > 0 && (
            <span className="search-count">({sessions.length})</span>
          )}
        </div>

        <div className={`sidebar-content ${isSearchListCollapsed ? 'collapsed' : ''}`}>
          {!isSearchListCollapsed && (
            sessions.length > 0 ? (
              <>
                {renderSessionGroup('今天', groupedSessions.today)}
                {renderSessionGroup('昨天', groupedSessions.yesterday)}
                {renderSessionGroup('更早', groupedSessions.older)}
              </>
            ) : (
              <div className="empty-sessions">
                <div className="empty-icon">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="m21 21-4.35-4.35"/>
                  </svg>
                </div>
                <p>尚無搜尋記錄</p>
                <p className="empty-hint">開始搜尋新聞來建立記錄</p>
              </div>
            )
          )}
        </div>

        {sessions.length > 0 && !isSearchListCollapsed && (
          <div className="sidebar-footer">
            <button className="clear-all-btn" onClick={handleClearAll}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="3,6 5,6 21,6"/>
                <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"/>
              </svg>
              清除所有記錄
            </button>
          </div>
        )}
      </div>
    </>
  );
};

export default SearchSidebar;