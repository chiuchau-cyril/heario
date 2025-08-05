import React, { useState, useRef, useEffect } from 'react';
import './AudioPlayer.css';

interface AudioPlayerProps {
  audioUrl: string | null;
  playlist?: any;
  onClose?: () => void;
  onPlaylistItemChange?: (index: number) => void;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ 
  audioUrl, 
  playlist,
  onClose,
  onPlaylistItemChange 
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressBarRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !audioUrl) return;

    const setAudioData = () => {
      setDuration(audio.duration);
      setCurrentTime(audio.currentTime);
      setIsLoading(false);
    };

    const setAudioTime = () => setCurrentTime(audio.currentTime);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    const handleCanPlay = () => {
      setIsLoading(false);
      // 自動開始播放
      audio.play().then(() => {
        setIsPlaying(true);
      }).catch(error => {
        console.log('自動播放被瀏覽器阻擋，需要使用者手動點擊播放');
      });
    };

    // Event listeners
    audio.addEventListener('loadeddata', setAudioData);
    audio.addEventListener('timeupdate', setAudioTime);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('loadstart', () => setIsLoading(true));
    audio.addEventListener('canplay', handleCanPlay);

    return () => {
      audio.removeEventListener('loadeddata', setAudioData);
      audio.removeEventListener('timeupdate', setAudioTime);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('loadstart', () => setIsLoading(true));
      audio.removeEventListener('canplay', handleCanPlay);
    };
  }, [audioUrl]);

  const togglePlayPause = () => {
    const audio = audioRef.current;
    if (!audio || !audioUrl) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleProgressBarClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    const progressBar = progressBarRef.current;
    if (!audio || !progressBar) return;

    const rect = progressBar.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = percentage * duration;
    
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    if (audioRef.current) {
      if (isMuted) {
        audioRef.current.volume = volume || 0.5;
        setVolume(volume || 0.5);
      } else {
        audioRef.current.volume = 0;
      }
      setIsMuted(!isMuted);
    }
  };

  const changePlaybackRate = () => {
    const rates = [0.5, 0.75, 1, 1.25, 1.5, 2];
    const currentIndex = rates.indexOf(playbackRate);
    const nextIndex = (currentIndex + 1) % rates.length;
    const newRate = rates[nextIndex];
    
    setPlaybackRate(newRate);
    if (audioRef.current) {
      audioRef.current.playbackRate = newRate;
    }
  };

  const skipTime = (seconds: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    const newTime = Math.max(0, Math.min(audio.currentTime + seconds, duration));
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const formatTime = (time: number) => {
    if (isNaN(time)) return '0:00';
    
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    return duration > 0 ? (currentTime / duration) * 100 : 0;
  };

  // 估算目前播放到哪則新聞
  useEffect(() => {
    if (playlist && playlist.items && playlist.items.length > 0) {
      let accumulatedTime = 0;
      for (let i = 0; i < playlist.items.length; i++) {
        accumulatedTime += playlist.items[i].estimatedDuration || 0;
        if (currentTime < accumulatedTime) {
          if (i !== currentItemIndex) {
            setCurrentItemIndex(i);
            if (onPlaylistItemChange) {
              onPlaylistItemChange(i);
            }
          }
          break;
        }
      }
    }
  }, [currentTime, playlist, currentItemIndex, onPlaylistItemChange]);

  if (!audioUrl) {
    return null;
  }

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={audioUrl}
        preload="metadata"
      />
      
      <div className="player-header">
        <div className="player-info">
          <h3 className="player-title">
            {playlist?.title || '新聞播放'}
          </h3>
          {playlist?.items && playlist.items.length > 0 && (
            <div className="current-item">
              正在播放: {playlist.items[currentItemIndex]?.newsItem?.title || '...'}
            </div>
          )}
        </div>
        {onClose && (
          <button className="player-close" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        )}
      </div>

      <div className="player-progress">
        <span className="time-display">{formatTime(currentTime)}</span>
        <div 
          ref={progressBarRef}
          className="progress-bar" 
          onClick={handleProgressBarClick}
        >
          <div 
            className="progress-fill" 
            style={{ width: `${getProgressPercentage()}%` }}
          />
          <div 
            className="progress-handle" 
            style={{ left: `${getProgressPercentage()}%` }}
          />
        </div>
        <span className="time-display">{formatTime(duration)}</span>
      </div>

      <div className="player-controls">
        <div className="control-group">
          <button 
            className="control-btn"
            onClick={() => skipTime(-10)}
            title="倒退 10 秒"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
              <path d="M3 3v5h5"/>
              <text x="12" y="16" textAnchor="middle" fontSize="10" fill="currentColor">10</text>
            </svg>
          </button>

          <button 
            className={`play-pause-btn ${isLoading ? 'loading' : ''}`}
            onClick={togglePlayPause}
            disabled={isLoading}
          >
            {isLoading ? (
              <svg className="loading-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 2v4"/>
                <path d="m16.2 7.8 2.9-2.9"/>
                <path d="M18 12h4"/>
                <path d="m16.2 16.2 2.9 2.9"/>
                <path d="M12 18v4"/>
                <path d="m4.9 19.1 2.9-2.9"/>
                <path d="M2 12h4"/>
                <path d="m4.9 4.9 2.9 2.9"/>
              </svg>
            ) : isPlaying ? (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
              </svg>
            ) : (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
            )}
          </button>

          <button 
            className="control-btn"
            onClick={() => skipTime(10)}
            title="快進 10 秒"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 12a9 9 0 1 1-9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
              <path d="M21 3v5h-5"/>
              <text x="12" y="16" textAnchor="middle" fontSize="10" fill="currentColor">10</text>
            </svg>
          </button>
        </div>

        <div className="control-group">
          <button 
            className="control-btn"
            onClick={changePlaybackRate}
            title="播放速度"
          >
            <span className="speed-text">{playbackRate}x</span>
          </button>

          <div className="volume-control">
            <button 
              className="control-btn"
              onClick={toggleMute}
              title={isMuted ? '取消靜音' : '靜音'}
            >
              {isMuted || volume === 0 ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                  <line x1="23" y1="9" x2="17" y2="15"/>
                  <line x1="17" y1="9" x2="23" y2="15"/>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
                </svg>
              )}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="volume-slider"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioPlayer;