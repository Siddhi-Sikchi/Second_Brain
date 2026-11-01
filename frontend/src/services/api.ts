import {
  AuthResponse, User, DocumentItem, NoteItem, SearchResultItem,
  RagResponse, GraphData, Quiz, QuizResult, QuizAttemptHistory,
  RevisionItem, AnalyticsSummary
} from '../types';

const API_BASE = '/api';

class ApiService {
  private getToken(): string | null {
    return localStorage.getItem('token');
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      ...(options.headers || {}),
    };

    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData)) {
      (headers as Record<string, string>)['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = 'An error occurred';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        errorMessage = response.statusText;
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  // Auth & Profile
  async register(data: { email: string; password: string; full_name: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: { email: string; password: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async logout(): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>('/auth/logout', {
      method: 'POST',
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  async updateProfile(data: { full_name?: string; bio?: string; avatar_url?: string }): Promise<User> {
    return this.request<User>('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async changePassword(data: { current_password: string; new_password: string }): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>('/users/change-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Documents
  async uploadDocument(formData: FormData): Promise<DocumentItem> {
    return this.request<DocumentItem>('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  }

  async getDocuments(params?: { category?: string; file_type?: string; status?: string; tag?: string }): Promise<DocumentItem[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<DocumentItem[]>(`/documents${query ? `?${query}` : ''}`);
  }

  async getDocument(id: number): Promise<DocumentItem> {
    return this.request<DocumentItem>(`/documents/${id}`);
  }

  async updateDocument(id: number, data: { title?: string; category?: string; summary?: string; tags?: string[] }): Promise<DocumentItem> {
    return this.request<DocumentItem>(`/documents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteDocument(id: number): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(`/documents/${id}`, {
      method: 'DELETE',
    });
  }

  async summarizeDocument(id: number): Promise<DocumentItem> {
    return this.request<DocumentItem>(`/documents/${id}/summarize`, {
      method: 'POST',
    });
  }

  // Notes
  async getNotes(params?: { category?: string; tag?: string; is_archived?: boolean }): Promise<NoteItem[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<NoteItem[]>(`/notes${query ? `?${query}` : ''}`);
  }

  async createNote(data: { title: string; content: string; category?: string; tags?: string[]; is_pinned?: boolean }): Promise<NoteItem> {
    return this.request<NoteItem>('/notes', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateNote(id: number, data: Partial<NoteItem>): Promise<NoteItem> {
    return this.request<NoteItem>(`/notes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteNote(id: number): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(`/notes/${id}`, {
      method: 'DELETE',
    });
  }

  // Search & RAG
  async search(query: string, filters?: { file_type?: string; category?: string; tag?: string }): Promise<SearchResultItem[]> {
    return this.request<SearchResultItem[]>('/search', {
      method: 'POST',
      body: JSON.stringify({ query, ...filters }),
    });
  }

  async askRag(question: string, filters?: { document_ids?: number[]; note_ids?: number[] }): Promise<RagResponse> {
    return this.request<RagResponse>('/search/rag', {
      method: 'POST',
      body: JSON.stringify({ question, ...filters }),
    });
  }

  // Knowledge Graph
  async getGraph(): Promise<GraphData> {
    return this.request<GraphData>('/graph');
  }

  // Quizzes
  async generateQuiz(data: { title: string; source_type: string; source_id?: number; question_count: number }): Promise<Quiz> {
    return this.request<Quiz>('/quizzes/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getQuizzes(): Promise<Quiz[]> {
    return this.request<Quiz[]>('/quizzes');
  }

  async getQuiz(id: number): Promise<Quiz> {
    return this.request<Quiz>(`/quizzes/${id}`);
  }

  async submitQuiz(id: number, answers: Array<{ question_id: number; user_answer: string }>, time_taken_seconds: number): Promise<QuizResult> {
    return this.request<QuizResult>(`/quizzes/${id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers, time_taken_seconds }),
    });
  }

  async getQuizHistory(): Promise<QuizAttemptHistory[]> {
    return this.request<QuizAttemptHistory[]>('/quizzes/attempts/history');
  }

  // Revision & Spaced Repetition
  async getDueRevisions(): Promise<RevisionItem[]> {
    return this.request<RevisionItem[]>('/revision/due');
  }

  async getAllRevisions(): Promise<RevisionItem[]> {
    return this.request<RevisionItem[]>('/revision/all');
  }

  async reviewRevisionItem(id: number, rating: 'again' | 'hard' | 'good' | 'easy'): Promise<RevisionItem> {
    return this.request<RevisionItem>(`/revision/${id}/review`, {
      method: 'POST',
      body: JSON.stringify({ rating }),
    });
  }

  // Analytics
  async getAnalytics(): Promise<AnalyticsSummary> {
    return this.request<AnalyticsSummary>('/analytics/dashboard');
  }
}

export const api = new ApiService();
