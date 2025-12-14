/**
 * App Context - Global State Management
 */
import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { Todo, Message, TodoFilter, AppState, AppAction } from '../types';
import { loadTodos, saveTodos } from '../utils/storage';

// Initial State
const initialState: AppState = {
  todos: [],
  filter: 'all',
  chatMessages: [],
  isLoading: false,
};

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        ...state,
        todos: [...state.todos, action.payload],
      };

    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map((todo) =>
          todo.id === action.payload
            ? { ...todo, completed: !todo.completed }
            : todo
        ),
      };

    case 'DELETE_TODO':
      return {
        ...state,
        todos: state.todos.filter((todo) => todo.id !== action.payload),
      };

    case 'UPDATE_TODO':
      return {
        ...state,
        todos: state.todos.map((todo) =>
          todo.id === action.payload.id
            ? { ...todo, ...action.payload.updates }
            : todo
        ),
      };

    case 'SET_FILTER':
      return {
        ...state,
        filter: action.payload,
      };

    case 'SET_TODOS':
      return {
        ...state,
        todos: action.payload,
      };

    case 'ADD_MESSAGE':
      return {
        ...state,
        chatMessages: [...state.chatMessages, action.payload],
      };

    case 'SET_MESSAGES':
      return {
        ...state,
        chatMessages: action.payload,
      };

    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };

    default:
      return state;
  }
}

// Context Types
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  // Helper functions
  addTodo: (title: string, options?: Partial<Todo>) => void;
  toggleTodo: (id: string) => void;
  deleteTodo: (id: string) => void;
  addMessage: (role: Message['role'], content: string) => void;
  filteredTodos: Todo[];
}

// Create Context
const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider Component
export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Load todos from storage on mount
  useEffect(() => {
    const loadStoredTodos = async () => {
      const todos = await loadTodos();
      dispatch({ type: 'SET_TODOS', payload: todos });
    };
    loadStoredTodos();
  }, []);

  // Save todos to storage when they change
  useEffect(() => {
    saveTodos(state.todos);
  }, [state.todos]);

  // Helper: Add Todo
  const addTodo = (title: string, options?: Partial<Todo>) => {
    const newTodo: Todo = {
      id: Date.now().toString(),
      title,
      completed: false,
      createdAt: new Date(),
      ...options,
    };
    dispatch({ type: 'ADD_TODO', payload: newTodo });
  };

  // Helper: Toggle Todo
  const toggleTodo = (id: string) => {
    dispatch({ type: 'TOGGLE_TODO', payload: id });
  };

  // Helper: Delete Todo
  const deleteTodo = (id: string) => {
    dispatch({ type: 'DELETE_TODO', payload: id });
  };

  // Helper: Add Message
  const addMessage = (role: Message['role'], content: string) => {
    const message: Message = {
      id: Date.now().toString(),
      role,
      content,
      timestamp: new Date(),
    };
    dispatch({ type: 'ADD_MESSAGE', payload: message });
  };

  // Computed: Filtered Todos
  const filteredTodos = state.todos.filter((todo) => {
    if (state.filter === 'active') return !todo.completed;
    if (state.filter === 'completed') return todo.completed;
    return true;
  });

  const value: AppContextType = {
    state,
    dispatch,
    addTodo,
    toggleTodo,
    deleteTodo,
    addMessage,
    filteredTodos,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// Custom Hook
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}
