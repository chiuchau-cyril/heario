/**
 * 異步新聞搜尋服務
 * 支援背景處理和即時狀態更新
 */

import { NewsItem } from './api';

export interface SearchTask {
  task_id: string;
  query: string;
  status: 'started' | 'fetching_articles' | 'filtering_articles' | 'fetching_content' | 'generating_summaries' | 'completed' | 'error' | 'cancelled';
  message: string;
  progress: number;
  started_at: string;
  articles: NewsItem[];
  total_processed?: number;
  total_found?: number;
  error?: string;
}

export interface PaginatedSearchResult {
  articles: NewsItem[];
  page: number;
  per_page: number;
  total_immediate: number;
  background_task_id?: string;
  message: string;
}

class AsyncNewsService {
  private baseURL = 'http://localhost:5001/api';

  /**
   * 開始異步搜尋
   */
  async startAsyncSearch(query: string, pageSize: number = 10): Promise<{
    task_id: string;
    status: string;
    message: string;
    check_url: string;
  }> {
    const response = await fetch(`${this.baseURL}/news/search/async`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        page_size: pageSize
      })
    });

    if (!response.ok) {
      throw new Error(`搜尋請求失敗: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 獲取搜尋任務狀態
   */
  async getSearchStatus(taskId: string): Promise<SearchTask> {
    const response = await fetch(`${this.baseURL}/news/search/status/${taskId}`);
    
    if (!response.ok) {
      throw new Error(`無法獲取任務狀態: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 分頁搜尋 - 立即返回現有結果，背景搜尋新內容
   */
  async paginatedSearch(query: string, page: number = 1, perPage: number = 5): Promise<PaginatedSearchResult> {
    const response = await fetch(`${this.baseURL}/news/search/paginated`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        page,
        per_page: perPage
      })
    });

    if (!response.ok) {
      throw new Error(`分頁搜尋失敗: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 列出所有搜尋任務
   */
  async listSearchTasks(): Promise<{
    tasks: Partial<SearchTask>[];
    total: number;
  }> {
    const response = await fetch(`${this.baseURL}/news/search/tasks`);
    
    if (!response.ok) {
      throw new Error(`無法獲取任務列表: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 取消搜尋任務
   */
  async cancelSearchTask(taskId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseURL}/news/search/tasks/${taskId}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error(`無法取消任務: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 輪詢搜尋狀態直到完成
   */
  async pollSearchStatus(
    taskId: string, 
    onProgress?: (task: SearchTask) => void,
    pollInterval: number = 1000
  ): Promise<SearchTask> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const task = await this.getSearchStatus(taskId);
          
          if (onProgress) {
            onProgress(task);
          }

          if (task.status === 'completed') {
            resolve(task);
          } else if (task.status === 'error') {
            reject(new Error(task.error || task.message));
          } else if (task.status === 'cancelled') {
            reject(new Error('搜尋已取消'));
          } else {
            // 繼續輪詢
            setTimeout(poll, pollInterval);
          }
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  }

  /**
   * 智能搜尋 - 結合立即結果和背景處理
   */
  async smartSearch(
    query: string,
    onImmediateResults?: (results: PaginatedSearchResult) => void,
    onProgress?: (task: SearchTask) => void,
    onFinalResults?: (task: SearchTask) => void
  ): Promise<{
    immediateResults: PaginatedSearchResult;
    finalResults?: SearchTask;
  }> {
    // 1. 先獲取立即結果
    const immediateResults = await this.paginatedSearch(query, 1, 8);
    
    if (onImmediateResults) {
      onImmediateResults(immediateResults);
    }

    // 2. 如果有背景任務，等待其完成
    if (immediateResults.background_task_id) {
      try {
        const finalResults = await this.pollSearchStatus(
          immediateResults.background_task_id,
          onProgress,
          1000
        );

        if (onFinalResults) {
          onFinalResults(finalResults);
        }

        return { immediateResults, finalResults };
      } catch (error) {
        console.error('背景搜尋失敗:', error);
        return { immediateResults };
      }
    }

    return { immediateResults };
  }
}

export const asyncNewsService = new AsyncNewsService();
export default asyncNewsService;