import React, { useState, useEffect } from 'react';
import SearchSidebar from './SearchSidebar';
import NewsList from './NewsList';
import PlaylistPanel from './PlaylistPanel';
import AudioPlayer from './AudioPlayer';
import { SearchSession, SearchHistoryManager } from '../utils/searchHistory';
import { Playlist, PlaylistManager } from '../utils/playlistManager';
import { AudioService } from '../services/audioService';
import './MainLayout.css';

const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [playlistOpen, setPlaylistOpen] = useState(false);
  const [currentSession, setCurrentSession] = useState<SearchSession | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isNewSearchClearing, setIsNewSearchClearing] = useState(false);
  const [playlist, setPlaylist] = useState<Playlist>(() => {
    return PlaylistManager.getCurrentPlaylist() || PlaylistManager.createPlaylist();
  });
  const [audioGenerating, setAudioGenerating] = useState(false);
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null);
  const [showAudioPlayer, setShowAudioPlayer] = useState(false);

  useEffect(() => {
    // 桌面版預設關閉側邊欄來測試容器寬度
    if (window.innerWidth >= 1024) {
      setSidebarOpen(false);
    }
  }, []);

  const handleNewSearch = () => {
    setCurrentSession(null);
    setSearchQuery('');
    setIsNewSearchClearing(true);
    
    // 短暫延遲後重置清除標誌
    setTimeout(() => {
      setIsNewSearchClearing(false);
    }, 100);
  };

  const handleSessionSelect = (session: SearchSession) => {
    setCurrentSession(session);
    setSearchQuery(session.query);
    // 移動端選擇後關閉側邊欄
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  };

  const handleSearch = (query: string) => {
    // 創建新的搜尋 session
    const newSession = SearchHistoryManager.createSession(query);
    setCurrentSession(newSession);
    setSearchQuery(query);
  };

  const handleSearchComplete = (newsCount: number) => {
    // 更新當前 session 的新聞數量
    if (currentSession) {
      SearchHistoryManager.updateSession(currentSession.id, { newsCount });
      setCurrentSession({ ...currentSession, newsCount });
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const togglePlaylist = () => {
    setPlaylistOpen(!playlistOpen);
  };

  const handlePlaylistUpdate = (updatedPlaylist: Playlist) => {
    setPlaylist(updatedPlaylist);
  };

  const handleGenerateAudio = async () => {
    if (playlist.items.length === 0) {
      alert('播放清單是空的，請先加入一些新聞');
      return;
    }

    try {
      setAudioGenerating(true);
      console.log('開始生成音頻檔案...');
      
      // Test TTS service first
      try {
        await AudioService.testTTS();
        console.log('TTS 服務可用');
      } catch (error) {
        console.error('TTS 服務不可用:', error);
        alert('TTS 服務尚未設定完成，請檢查 Google Cloud 設定。詳見後端 GOOGLE_TTS_SETUP.md');
        return;
      }

      // Generate playlist audio
      const audioBlob = await AudioService.generatePlaylistAudio(playlist);
      console.log('音頻生成成功:', audioBlob.size, 'bytes');
      
      // Generate filename with timestamp
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-');
      const filename = `${playlist.title}_${timestamp}.mp3`;
      
      // Download the audio file
      AudioService.downloadAudio(audioBlob, filename);
      
      alert(`音頻檔案生成成功！檔案已開始下載：${filename}`);
      
    } catch (error) {
      console.error('音頻生成失敗:', error);
      alert(`音頻生成失敗: ${error instanceof Error ? error.message : '未知錯誤'}`);
    } finally {
      setAudioGenerating(false);
    }
  };

  const handleStartPlayback = async () => {
    if (playlist.items.length === 0) {
      alert('播放清單是空的，請先加入一些新聞');
      return;
    }

    try {
      setAudioGenerating(true);
      console.log('開始生成播放音頻...');
      
      // 立即關閉播放清單側邊欄
      setPlaylistOpen(false);
      
      // Test TTS service first
      await AudioService.testTTS();
      
      // Generate playlist audio
      const audioBlob = await AudioService.generatePlaylistAudio(playlist);
      console.log('音頻生成成功，準備播放');
      
      // Create object URL for playback
      const audioUrl = AudioService.createAudioURL(audioBlob);
      setCurrentAudioUrl(audioUrl);
      setShowAudioPlayer(true);
      
    } catch (error) {
      console.error('音頻生成失敗:', error);
      alert(`音頻生成失敗: ${error instanceof Error ? error.message : '未知錯誤'}`);
    } finally {
      setAudioGenerating(false);
    }
  };

  const handleCloseAudioPlayer = () => {
    // Clean up audio URL
    if (currentAudioUrl) {
      AudioService.revokeAudioURL(currentAudioUrl);
      setCurrentAudioUrl(null);
    }
    setShowAudioPlayer(false);
  };

  return (
    <div className={`main-layout ${sidebarOpen ? 'sidebar-open' : ''}`}>
      <SearchSidebar
        isOpen={sidebarOpen}
        onToggle={toggleSidebar}
        currentSessionId={currentSession?.id}
        onSessionSelect={handleSessionSelect}
        onNewSearch={handleNewSearch}
      />
      
      <div className="main-content">
        <div className="main-header">
          <div className="header-left">
            {!sidebarOpen && (
              <button className="sidebar-toggle-btn" onClick={toggleSidebar}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="3" y1="6" x2="21" y2="6"/>
                  <line x1="3" y1="12" x2="21" y2="12"/>
                  <line x1="3" y1="18" x2="21" y2="18"/>
                </svg>
              </button>
            )}
            <h1>Heario 新聞摘要</h1>
          </div>
          
          <button className="playlist-toggle-btn" onClick={togglePlaylist}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            播放清單 ({playlist.items.length})
          </button>
        </div>
        
        <NewsList
          searchQuery={searchQuery}
          onSearch={handleSearch}
          onSearchComplete={handleSearchComplete}
          playlist={playlist}
          onPlaylistUpdate={handlePlaylistUpdate}
          isNewSearchClearing={isNewSearchClearing}
        />
        
        {showAudioPlayer && (
          <AudioPlayer
            audioUrl={currentAudioUrl}
            playlist={playlist}
            onClose={handleCloseAudioPlayer}
          />
        )}
      </div>
      
      <PlaylistPanel
        playlist={playlist}
        isOpen={playlistOpen}
        onToggle={togglePlaylist}
        onPlaylistUpdate={handlePlaylistUpdate}
        onGenerateAudio={handleGenerateAudio}
        onStartPlayback={handleStartPlayback}
        audioGenerating={audioGenerating}
      />
    </div>
  );
};

export default MainLayout;