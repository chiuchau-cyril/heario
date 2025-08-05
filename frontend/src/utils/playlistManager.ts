import { NewsItem } from '../services/api';

export interface PlaylistItem {
  id: string;
  newsItem: NewsItem;
  order: number;
  estimatedDuration: number; // 以秒為單位
  audioUrl?: string;
}

export interface Playlist {
  id: string;
  title: string;
  items: PlaylistItem[];
  totalDuration: number;
  createdAt: number;
  updatedAt: number;
}

export class PlaylistManager {
  private static readonly STORAGE_KEY = 'currentPlaylist';
  private static readonly PLAYLISTS_KEY = 'savedPlaylists';

  // 估算文字閱讀時間（中文約180字/分鐘）
  static estimateReadingTime(text: string): number {
    const chineseChars = (text.match(/[\u4e00-\u9fff]/g) || []).length;
    const englishWords = (text.match(/[a-zA-Z]+/g) || []).length;
    
    // 中文：180字/分鐘，英文：200詞/分鐘，加上標點和停頓時間
    const chineseTime = (chineseChars / 180) * 60;
    const englishTime = (englishWords / 200) * 60;
    
    return Math.max(30, Math.ceil(chineseTime + englishTime + 10)); // 最少30秒，加10秒緩衝
  }

  // 獲取當前播放清單
  static getCurrentPlaylist(): Playlist | null {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Error loading current playlist:', error);
      return null;
    }
  }

  // 保存當前播放清單
  static saveCurrentPlaylist(playlist: Playlist): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(playlist));
    } catch (error) {
      console.error('Error saving current playlist:', error);
    }
  }

  // 創建新的播放清單
  static createPlaylist(title: string = '我的播放清單'): Playlist {
    const playlist: Playlist = {
      id: `playlist_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title,
      items: [],
      totalDuration: 0,
      createdAt: Date.now(),
      updatedAt: Date.now()
    };
    
    this.saveCurrentPlaylist(playlist);
    return playlist;
  }

  // 添加新聞到播放清單
  static addToPlaylist(newsItem: NewsItem, playlist?: Playlist): Playlist {
    const currentPlaylist = playlist || this.getCurrentPlaylist() || this.createPlaylist();
    
    // 檢查是否已存在
    const existingIndex = currentPlaylist.items.findIndex(item => item.newsItem.id === newsItem.id);
    if (existingIndex !== -1) {
      return currentPlaylist; // 已存在，不重複添加
    }

    const estimatedDuration = this.estimateReadingTime(newsItem.summary + ' ' + (newsItem.title || ''));
    
    const playlistItem: PlaylistItem = {
      id: `item_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      newsItem,
      order: currentPlaylist.items.length,
      estimatedDuration
    };

    // 建立新的播放清單物件以觸發 React 重新渲染
    const updatedPlaylist = {
      ...currentPlaylist,
      items: [...currentPlaylist.items, playlistItem],
      totalDuration: currentPlaylist.totalDuration + estimatedDuration,
      updatedAt: Date.now()
    };

    this.saveCurrentPlaylist(updatedPlaylist);
    return updatedPlaylist;
  }

  // 從播放清單移除新聞
  static removeFromPlaylist(itemId: string, playlist?: Playlist): Playlist {
    const currentPlaylist = playlist || this.getCurrentPlaylist();
    if (!currentPlaylist) return this.createPlaylist();

    const itemIndex = currentPlaylist.items.findIndex(item => item.id === itemId);
    if (itemIndex === -1) return currentPlaylist;

    const removedItem = currentPlaylist.items[itemIndex];
    
    // 建立新的項目陣列（移除指定項目）
    const newItems = currentPlaylist.items.filter((_, index) => index !== itemIndex);
    
    // 重新排序並建立新的播放清單物件
    const reorderedItems = newItems.map((item, index) => ({
      ...item,
      order: index
    }));

    const updatedPlaylist = {
      ...currentPlaylist,
      items: reorderedItems,
      totalDuration: currentPlaylist.totalDuration - removedItem.estimatedDuration,
      updatedAt: Date.now()
    };

    this.saveCurrentPlaylist(updatedPlaylist);
    return updatedPlaylist;
  }

  // 重新排序播放清單
  static reorderPlaylist(itemIds: string[], playlist?: Playlist): Playlist {
    const currentPlaylist = playlist || this.getCurrentPlaylist();
    if (!currentPlaylist) return this.createPlaylist();

    const reorderedItems: PlaylistItem[] = [];
    
    itemIds.forEach((itemId, index) => {
      const item = currentPlaylist.items.find(item => item.id === itemId);
      if (item) {
        // 建立新的項目物件以確保參考不同
        reorderedItems.push({
          ...item,
          order: index
        });
      }
    });

    const updatedPlaylist = {
      ...currentPlaylist,
      items: reorderedItems,
      updatedAt: Date.now()
    };
    
    this.saveCurrentPlaylist(updatedPlaylist);
    return updatedPlaylist;
  }

  // 清空播放清單
  static clearPlaylist(): Playlist {
    const emptyPlaylist = this.createPlaylist();
    this.saveCurrentPlaylist(emptyPlaylist);
    return emptyPlaylist;
  }

  // 檢查新聞是否在播放清單中
  static isInPlaylist(newsId: string, playlist?: Playlist): boolean {
    const currentPlaylist = playlist || this.getCurrentPlaylist();
    if (!currentPlaylist) return false;
    
    return currentPlaylist.items.some(item => item.newsItem.id === newsId);
  }

  // 格式化時間顯示
  static formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes === 0) {
      return `${remainingSeconds}秒`;
    } else if (remainingSeconds === 0) {
      return `${minutes}分鐘`;
    } else {
      return `${minutes}分${remainingSeconds}秒`;
    }
  }

  // 獲取所有保存的播放清單
  static getSavedPlaylists(): Playlist[] {
    try {
      const stored = localStorage.getItem(this.PLAYLISTS_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error loading saved playlists:', error);
      return [];
    }
  }

  // 保存播放清單到歷史記錄
  static savePlaylistToHistory(playlist: Playlist): void {
    try {
      const savedPlaylists = this.getSavedPlaylists();
      const existingIndex = savedPlaylists.findIndex(p => p.id === playlist.id);
      
      if (existingIndex !== -1) {
        savedPlaylists[existingIndex] = playlist;
      } else {
        savedPlaylists.unshift(playlist);
      }
      
      // 保留最近20個播放清單
      const limitedPlaylists = savedPlaylists.slice(0, 20);
      localStorage.setItem(this.PLAYLISTS_KEY, JSON.stringify(limitedPlaylists));
    } catch (error) {
      console.error('Error saving playlist to history:', error);
    }
  }
}