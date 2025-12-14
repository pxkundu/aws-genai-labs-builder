/**
 * useAI Hook - Easy AI Integration for Components
 * 
 * This hook provides a simple interface for AI interactions
 * with loading states, error handling, and caching.
 */

import { useState, useCallback, useRef } from 'react';
import { chat, parseTaskFromText, getSuggestions } from '../services/aiService';
import { AIResponse, Todo } from '../types';

interface UseAIOptions {
  onError?: (error: Error) => void;
  cacheTimeout?: number; // Cache responses for this many ms
}

interface UseAIReturn {
  // State
  loading: boolean;
  error: Error | null;
  lastResponse: AIResponse | null;
  
  // Actions
  sendMessage: (message: string, context?: string) => Promise<AIResponse>;
  parseTask: (text: string) => Promise<Partial<Todo> | null>;
  fetchSuggestions: (todos: Todo[]) => Promise<string[]>;
  clearError: () => void;
}

export function useAI(options: UseAIOptions = {}): UseAIReturn {
  const { onError, cacheTimeout = 60000 } = options;
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastResponse, setLastResponse] = useState<AIResponse | null>(null);
  
  // Simple cache
  const cache = useRef<Map<string, { response: AIResponse; timestamp: number }>>(new Map());

  /**
   * Send a message to the AI
   */
  const sendMessage = useCallback(async (message: string, context?: string): Promise<AIResponse> => {
    // Check cache
    const cacheKey = `${message}:${context || ''}`;
    const cached = cache.current.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < cacheTimeout) {
      setLastResponse(cached.response);
      return cached.response;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await chat(message, context);
      
      // Cache the response
      cache.current.set(cacheKey, {
        response,
        timestamp: Date.now(),
      });
      
      setLastResponse(response);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('AI request failed');
      setError(error);
      onError?.(error);
      
      // Return fallback response
      return {
        message: "I'm having trouble connecting right now. Please try again.",
        suggestions: [],
      };
    } finally {
      setLoading(false);
    }
  }, [cacheTimeout, onError]);

  /**
   * Parse natural language into a task
   */
  const parseTask = useCallback(async (text: string): Promise<Partial<Todo> | null> => {
    setLoading(true);
    setError(null);

    try {
      const task = await parseTaskFromText(text);
      return task;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to parse task');
      setError(error);
      onError?.(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, [onError]);

  /**
   * Get AI suggestions based on todos
   */
  const fetchSuggestions = useCallback(async (todos: Todo[]): Promise<string[]> => {
    setLoading(true);
    setError(null);

    try {
      const suggestions = await getSuggestions(todos);
      return suggestions;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to get suggestions');
      setError(error);
      onError?.(error);
      return ['Focus on your most important task.'];
    } finally {
      setLoading(false);
    }
  }, [onError]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    lastResponse,
    sendMessage,
    parseTask,
    fetchSuggestions,
    clearError,
  };
}

export default useAI;
