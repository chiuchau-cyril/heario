import React, { useState, useRef } from 'react';
import './SearchBar.css';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  showSuggestions?: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  onSearch, 
  placeholder = '搜尋新聞...',
  showSuggestions = false 
}) => {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // 執行搜尋
  const handleSearch = () => {
    if (query.trim()) {
      onSearch(query.trim());
      setQuery('');
    }
  };

  // 鍵盤事件
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="search-bar-container">
      <div className="search-input-wrapper">
        <input
          ref={inputRef}
          type="text"
          className="search-input"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        
        <div className="search-actions">
          {query && (
            <button 
              className="clear-button"
              onClick={() => setQuery('')}
              aria-label="清除搜尋"
            >
              ×
            </button>
          )}
          
          <button 
            className="search-button"
            onClick={handleSearch}
            aria-label="搜尋"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchBar;