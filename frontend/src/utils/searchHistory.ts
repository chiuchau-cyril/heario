export interface SearchSession {
  id: string;
  title: string;
  query: string;
  timestamp: number;
  newsCount?: number;
}

export class SearchHistoryManager {
  private static readonly STORAGE_KEY = 'searchSessions';
  private static readonly MAX_SESSIONS = 50;

  static getSessions(): SearchSession[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error loading search sessions:', error);
      return [];
    }
  }

  static saveSessions(sessions: SearchSession[]): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(sessions));
    } catch (error) {
      console.error('Error saving search sessions:', error);
    }
  }

  static createSession(query: string, newsCount: number = 0): SearchSession {
    const sessions = this.getSessions();
    
    // 檢查是否已有相同查詢的 session
    const existingIndex = sessions.findIndex(s => s.query === query);
    if (existingIndex !== -1) {
      // 更新現有 session 的時間戳和新聞數量
      sessions[existingIndex].timestamp = Date.now();
      sessions[existingIndex].newsCount = newsCount;
      this.saveSessions(sessions);
      return sessions[existingIndex];
    }

    // 創建新 session
    const newSession: SearchSession = {
      id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title: this.generateTitle(query),
      query,
      timestamp: Date.now(),
      newsCount
    };

    // 添加到開頭並限制數量
    const updatedSessions = [newSession, ...sessions].slice(0, this.MAX_SESSIONS);
    this.saveSessions(updatedSessions);
    
    return newSession;
  }

  static updateSession(sessionId: string, updates: Partial<SearchSession>): void {
    const sessions = this.getSessions();
    const index = sessions.findIndex(s => s.id === sessionId);
    
    if (index !== -1) {
      sessions[index] = { ...sessions[index], ...updates };
      this.saveSessions(sessions);
    }
  }

  static deleteSession(sessionId: string): void {
    const sessions = this.getSessions();
    const filtered = sessions.filter(s => s.id !== sessionId);
    this.saveSessions(filtered);
  }

  static clearAllSessions(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }

  private static generateTitle(query: string): string {
    // 生成基於查詢內容的標題
    if (query.length <= 20) {
      return query;
    }
    
    // 如果查詢太長，智能截取
    const words = query.split(' ');
    if (words.length === 1) {
      return query.substring(0, 20) + '...';
    }
    
    let title = '';
    for (const word of words) {
      if ((title + word).length > 20) {
        break;
      }
      title += (title ? ' ' : '') + word;
    }
    
    return title + (title.length < query.length ? '...' : '');
  }

  static getSessionsByDate(): { today: SearchSession[], yesterday: SearchSession[], older: SearchSession[] } {
    const sessions = this.getSessions();
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
    
    return {
      today: sessions.filter(s => new Date(s.timestamp) >= today),
      yesterday: sessions.filter(s => {
        const sessionDate = new Date(s.timestamp);
        return sessionDate >= yesterday && sessionDate < today;
      }),
      older: sessions.filter(s => new Date(s.timestamp) < yesterday)
    };
  }
}