/**
 * Audio service for TTS functionality
 */

import { Playlist } from '../utils/playlistManager';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-production-api.com' 
  : 'http://localhost:5001';

export interface AudioResponse {
  status: string;
  message?: string;
}

export class AudioService {
  
  /**
   * Test TTS service availability
   */
  static async testTTS(): Promise<AudioResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/audio/test`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'TTS test failed');
      }
      
      return data;
    } catch (error) {
      console.error('TTS test error:', error);
      throw new Error(`TTS 服務測試失敗: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Synthesize text to speech
   */
  static async synthesizeText(text: string, language?: string): Promise<Blob> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/audio/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          language
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Text synthesis failed');
      }

      return await response.blob();
    } catch (error) {
      console.error('Text synthesis error:', error);
      throw new Error(`文字轉語音失敗: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate audio for an entire playlist
   */
  static async generatePlaylistAudio(playlist: Playlist): Promise<Blob> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/audio/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          playlist
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Playlist audio generation failed');
      }

      return await response.blob();
    } catch (error) {
      console.error('Playlist audio generation error:', error);
      throw new Error(`播放清單音頻生成失敗: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate audio for a single news item
   */
  static async generateNewsAudio(newsItem: any): Promise<Blob> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/audio/news`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          newsItem
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'News audio generation failed');
      }

      return await response.blob();
    } catch (error) {
      console.error('News audio generation error:', error);
      throw new Error(`新聞音頻生成失敗: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Download audio blob as file
   */
  static downloadAudio(audioBlob: Blob, filename: string = 'audio.mp3'): void {
    try {
      const url = URL.createObjectURL(audioBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Audio download error:', error);
      throw new Error('音頻下載失敗');
    }
  }

  /**
   * Create audio URL for playback
   */
  static createAudioURL(audioBlob: Blob): string {
    return URL.createObjectURL(audioBlob);
  }

  /**
   * Revoke audio URL to free memory
   */
  static revokeAudioURL(url: string): void {
    URL.revokeObjectURL(url);
  }

  /**
   * Check if browser supports audio playback
   */
  static isAudioSupported(): boolean {
    const audio = document.createElement('audio');
    return !!(audio.canPlayType && audio.canPlayType('audio/mpeg').replace(/no/, ''));
  }

  /**
   * Get estimated file size for playlist
   */
  static estimateAudioSize(playlist: Playlist): string {
    // Rough estimation: ~1KB per second for 128kbps MP3
    const totalDurationSeconds = playlist.totalDuration;
    const estimatedBytes = totalDurationSeconds * 1024 * 0.125; // 128kbps = 128/8 = 16KB/s, but compressed
    
    if (estimatedBytes < 1024 * 1024) {
      return `${Math.round(estimatedBytes / 1024)}KB`;
    } else {
      return `${(estimatedBytes / (1024 * 1024)).toFixed(1)}MB`;
    }
  }
}