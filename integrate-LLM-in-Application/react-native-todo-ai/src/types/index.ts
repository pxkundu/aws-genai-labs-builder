/**
 * Type Definitions for Todo AI App
 */

// Todo Types
export interface Todo {
  id: string;
  title: string;
  completed: boolean;
  createdAt: Date;
  dueDate?: Date;
  priority?: 'low' | 'medium' | 'high';
  notes?: string;
}

export type TodoFilter = 'all' | 'active' | 'completed';

// Chat Types
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface ChatSession {
  id: string;
  messages: Message[];
  createdAt: Date;
}

// AI Service Types
export interface AIResponse {
  message: string;
  suggestions?: string[];
  parsedTask?: Partial<Todo>;
}

export interface AIServiceConfig {
  provider: 'openai' | 'bedrock' | 'backend';
  apiKey?: string;
  baseUrl?: string;
  model?: string;
}

// App State Types
export interface AppState {
  todos: Todo[];
  filter: TodoFilter;
  chatMessages: Message[];
  isLoading: boolean;
}

export type AppAction =
  | { type: 'ADD_TODO'; payload: Todo }
  | { type: 'TOGGLE_TODO'; payload: string }
  | { type: 'DELETE_TODO'; payload: string }
  | { type: 'UPDATE_TODO'; payload: { id: string; updates: Partial<Todo> } }
  | { type: 'SET_FILTER'; payload: TodoFilter }
  | { type: 'SET_TODOS'; payload: Todo[] }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'SET_MESSAGES'; payload: Message[] }
  | { type: 'SET_LOADING'; payload: boolean };
