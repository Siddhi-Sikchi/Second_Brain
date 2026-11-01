export interface User {
  id: number;
  email: string;
  full_name: string;
  avatar_url?: string | null;
  bio?: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Tag {
  id: number;
  name: string;
  color?: string;
  created_at: string;
}

export interface DocumentItem {
  id: number;
  title: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string | null;
  extracted_text?: string | null;
  page_count: number;
  word_count: number;
  summary?: string | null;
  key_takeaways?: string[] | null;
  category: string;
  created_at: string;
  updated_at: string;
  tags: Tag[];
}

export interface NoteItem {
  id: number;
  title: string;
  content: string;
  summary?: string | null;
  category: string;
  word_count: number;
  is_pinned: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  tags: Tag[];
}

export interface SearchResultItem {
  id: number;
  title: string;
  type: 'document' | 'note';
  snippet: string;
  relevance_score: number;
  category: string;
  created_at: string;
  tags: string[];
}

export interface Citation {
  source_title: string;
  source_type: 'document' | 'note';
  source_id: number;
  page?: number | null;
  excerpt: string;
  relevance: number;
}

export interface RagResponse {
  question: string;
  answer: string;
  is_grounded: boolean;
  citations: Citation[];
  confidence_score: number;
}

export interface GraphNode {
  id: string;
  label: string;
  group: 'document' | 'note' | 'tag' | 'category';
  val: number;
  source_id?: number | null;
  meta?: Record<string, any>;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface GraphLink {
  source: string;
  target: string;
  relation: string;
  weight: number;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
  total_nodes: number;
  total_edges: number;
}

export interface QuizQuestion {
  id: number;
  question_text: string;
  question_type: string;
  options?: string[];
  explanation?: string;
  order_index: number;
}

export interface Quiz {
  id: number;
  title: string;
  description?: string;
  source_type: string;
  source_id?: number;
  question_count: number;
  created_at: string;
  questions: QuizQuestion[];
}

export interface QuestionEvaluation {
  question_id: number;
  question_text: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation?: string;
  source_excerpt?: string;
}

export interface QuizResult {
  attempt_id: number;
  quiz_id: number;
  quiz_title: string;
  score: number;
  total_questions: number;
  correct_count: number;
  time_taken_seconds: number;
  completed_at: string;
  evaluations: QuestionEvaluation[];
}

export interface QuizAttemptHistory {
  id: number;
  quiz_id: number;
  quiz_title: string;
  score: number;
  total_questions: number;
  correct_count: number;
  time_taken_seconds: number;
  completed_at: string;
}

export interface RevisionItem {
  id: number;
  item_type: string;
  item_id?: number;
  title: string;
  content_preview?: string;
  repetition_level: number;
  interval_days: number;
  ease_factor: number;
  next_review_date: string;
  last_reviewed_at?: string;
  review_count: number;
}

export interface AnalyticsSummary {
  total_documents: number;
  total_notes: number;
  total_words: number;
  total_quizzes_taken: number;
  average_quiz_score: number;
  storage_used_bytes: number;
  active_streak_days: number;
  categories: Record<string, number>;
  top_tags: Array<{ id: number; name: string; color: string; count: number }>;
  recent_activity: Array<{ type: string; title: string; category: string; timestamp: string }>;
}
