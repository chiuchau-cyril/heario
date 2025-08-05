import React, { useState, useRef } from 'react';
import './SmartSearchBar.css';

interface SmartSearchBarProps {
  onSearch: (query: string) => void;
  onSmartSearch?: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
  showAdvancedOptions?: boolean;
}

const SmartSearchBar: React.FC<SmartSearchBarProps> = ({
  onSearch,
  onSmartSearch,
  loading = false,
  placeholder = "搜尋新聞...",
  showAdvancedOptions = true
}) => {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState<'normal' | 'smart'>('smart');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    if (searchMode === 'smart' && onSmartSearch) {
      onSmartSearch(query.trim());
    } else {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
    inputRef.current?.focus();
  };

  return (
    <div className="smart-search-bar">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-container">
          <div className="search-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
          </div>
          
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            className="search-input"
            disabled={loading}
          />
          
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="clear-button"
              disabled={loading}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          )}
        </div>

        {showAdvancedOptions && (
          <div className="search-options">
            <div className="search-mode-toggle">
              <button
                type="button"
                className={`mode-button ${searchMode === 'smart' ? 'active' : ''}`}
                onClick={() => setSearchMode('smart')}
                disabled={loading}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                </svg>
                智能搜尋
              </button>
              <button
                type="button"
                className={`mode-button ${searchMode === 'normal' ? 'active' : ''}`}
                onClick={() => setSearchMode('normal')}
                disabled={loading}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="M21 21l-4.35-4.35"/>
                </svg>
                傳統搜尋
              </button>
            </div>
          </div>
        )}

        <button
          type="submit"
          className="search-button"
          disabled={!query.trim() || loading}
        >
          {loading ? (
            <>
              <svg className="loading-spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 2v4"/>
                <path d="m16.2 7.8 2.9-2.9"/>
                <path d="M18 12h4"/>
                <path d="m16.2 16.2 2.9 2.9"/>
                <path d="M12 18v4"/>
                <path d="m4.9 19.1 2.9-2.9"/>
                <path d="M2 12h4"/>
                <path d="m4.9 4.9 2.9 2.9"/>
              </svg>
              搜尋中...
            </>
          ) : (
            <>
              {searchMode === 'smart' ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="M21 21l-4.35-4.35"/>
                </svg>
              )}
              搜尋
            </>
          )}
        </button>
      </form>

      {searchMode === 'smart' && (
        <div className="search-mode-description">
          <div className="mode-description">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/>
              <circle cx="12" cy="17" r="1"/>
            </svg>
            智能搜尋會立即顯示相關新聞，同時在背景搜尋最新內容
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartSearchBar;