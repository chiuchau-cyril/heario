import React, { useState, useRef } from 'react';
import { Playlist, PlaylistItem, PlaylistManager } from '../utils/playlistManager';
import './PlaylistPanel.css';

interface PlaylistPanelProps {
  playlist: Playlist;
  isOpen: boolean;
  onToggle: () => void;
  onPlaylistUpdate: (playlist: Playlist) => void;
  onGenerateAudio?: () => void;
  onStartPlayback?: () => void;
  audioGenerating?: boolean;
}

const PlaylistPanel: React.FC<PlaylistPanelProps> = ({
  playlist,
  isOpen,
  onToggle,
  onPlaylistUpdate,
  onGenerateAudio,
  onStartPlayback,
  audioGenerating = false
}) => {
  const [draggedItem, setDraggedItem] = useState<string | null>(null);
  const [dragOverItem, setDragOverItem] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState(false);
  const [newTitle, setNewTitle] = useState(playlist.title);
  const titleInputRef = useRef<HTMLInputElement>(null);

  const handleDragStart = (e: React.DragEvent, itemId: string) => {
    setDraggedItem(itemId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, itemId: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverItem(itemId);
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
    setDragOverItem(null);
  };

  const handleDrop = (e: React.DragEvent, targetItemId: string) => {
    e.preventDefault();
    
    if (!draggedItem || draggedItem === targetItemId) {
      return;
    }

    const currentItems = [...playlist.items];
    const draggedIndex = currentItems.findIndex(item => item.id === draggedItem);
    const targetIndex = currentItems.findIndex(item => item.id === targetItemId);

    if (draggedIndex === -1 || targetIndex === -1) {
      return;
    }

    // 重新排序
    const [removed] = currentItems.splice(draggedIndex, 1);
    currentItems.splice(targetIndex, 0, removed);

    // 更新 order
    const reorderedItemIds = currentItems.map(item => item.id);
    const updatedPlaylist = PlaylistManager.reorderPlaylist(reorderedItemIds, playlist);
    onPlaylistUpdate(updatedPlaylist);

    setDraggedItem(null);
    setDragOverItem(null);
  };

  const handleRemoveItem = (itemId: string) => {
    const updatedPlaylist = PlaylistManager.removeFromPlaylist(itemId, playlist);
    onPlaylistUpdate(updatedPlaylist);
  };

  const handleTitleEdit = () => {
    setEditingTitle(true);
    setTimeout(() => titleInputRef.current?.focus(), 0);
  };

  const handleTitleSave = () => {
    if (newTitle.trim()) {
      const updatedPlaylist = { ...playlist, title: newTitle.trim(), updatedAt: Date.now() };
      PlaylistManager.saveCurrentPlaylist(updatedPlaylist);
      onPlaylistUpdate(updatedPlaylist);
    } else {
      setNewTitle(playlist.title);
    }
    setEditingTitle(false);
  };

  const handleTitleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleTitleSave();
    } else if (e.key === 'Escape') {
      setNewTitle(playlist.title);
      setEditingTitle(false);
    }
  };

  const handleClearPlaylist = () => {
    if (window.confirm('確定要清空播放清單嗎？')) {
      const clearedPlaylist = PlaylistManager.clearPlaylist();
      onPlaylistUpdate(clearedPlaylist);
    }
  };

  const formatTime = (seconds: number) => {
    return PlaylistManager.formatDuration(seconds);
  };

  return (
    <>
      {/* 移動端遮罩 */}
      {isOpen && <div className="playlist-overlay" onClick={onToggle} />}
      
      <div className={`playlist-panel ${isOpen ? 'open' : ''}`}>
        <div className="playlist-header">
          <div className="playlist-title-section">
            {editingTitle ? (
              <input
                ref={titleInputRef}
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                onBlur={handleTitleSave}
                onKeyDown={handleTitleKeyDown}
                className="title-edit-input"
              />
            ) : (
              <h3 className="playlist-title" onClick={handleTitleEdit}>
                {playlist.title}
                <svg className="edit-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="m18.5 2.5 3 3-12 12-6 1 1-6 14-14z"/>
                </svg>
              </h3>
            )}
          </div>
          
          <button className="close-btn" onClick={onToggle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div className="playlist-stats">
          <span className="stats-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            {playlist.items.length} 則新聞
          </span>
          <span className="stats-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12,6 12,12 16,14"/>
            </svg>
            約 {formatTime(playlist.totalDuration)}
          </span>
        </div>

        <div className="playlist-content">
          {playlist.items.length === 0 ? (
            <div className="empty-playlist">
              <div className="empty-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="m12 1 0 6 6 0-6 6-6-6 6 0z"/>
                  <path d="M21 16v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3"/>
                </svg>
              </div>
              <p>播放清單是空的</p>
              <p className="empty-hint">點擊新聞卡片上的 + 按鈕來新增</p>
            </div>
          ) : (
            <div className="playlist-items">
              {playlist.items.map((item, index) => (
                <div
                  key={item.id}
                  className={`playlist-item ${draggedItem === item.id ? 'dragging' : ''} ${dragOverItem === item.id ? 'drag-over' : ''}`}
                  draggable
                  onDragStart={(e) => handleDragStart(e, item.id)}
                  onDragOver={(e) => handleDragOver(e, item.id)}
                  onDragEnd={handleDragEnd}
                  onDrop={(e) => handleDrop(e, item.id)}
                >
                  <div className="item-order">{index + 1}</div>
                  
                  <div className="item-content">
                    <h4 className="item-title">{item.newsItem.title}</h4>
                    <p className="item-summary">{item.newsItem.summary.substring(0, 80)}...</p>
                    <div className="item-meta">
                      <span className="item-duration">{formatTime(item.estimatedDuration)}</span>
                      <span className="item-source">{item.newsItem.source}</span>
                    </div>
                  </div>
                  
                  <div className="item-actions">
                    <button className="drag-handle" title="拖拽排序">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <line x1="3" y1="6" x2="21" y2="6"/>
                        <line x1="3" y1="12" x2="21" y2="12"/>
                        <line x1="3" y1="18" x2="21" y2="18"/>
                      </svg>
                    </button>
                    
                    <button 
                      className="remove-btn" 
                      onClick={() => handleRemoveItem(item.id)}
                      title="移除"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {playlist.items.length > 0 && (
          <div className="playlist-actions">
            <button 
              className="action-btn secondary"
              onClick={handleClearPlaylist}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="3,6 5,6 21,6"/>
                <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"/>
              </svg>
              清空
            </button>
            
            {onGenerateAudio && (
              <button 
                className="action-btn primary"
                onClick={onGenerateAudio}
                disabled={audioGenerating}
              >
                {audioGenerating ? (
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
                    生成中...
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <polygon points="23,7 16,12 23,17 23,7"/>
                      <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                    </svg>
                    生成語音檔
                  </>
                )}
              </button>
            )}
            
            {onStartPlayback && (
              <button 
                className="action-btn primary"
                onClick={onStartPlayback}
                disabled={audioGenerating}
              >
                {audioGenerating ? (
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
                    準備播放...
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <polygon points="5,3 19,12 5,21 5,3"/>
                    </svg>
                    開始播放
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </>
  );
};

export default PlaylistPanel;