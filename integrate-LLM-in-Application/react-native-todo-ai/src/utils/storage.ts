/**
 * Storage Utilities - Persistent Data Storage
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Todo, Message } from '../types';

const STORAGE_KEYS = {
  TODOS: '@todo_ai:todos',
  CHAT_HISTORY: '@todo_ai:chat_history',
  SETTINGS: '@todo_ai:settings',
};

/**
 * Load todos from storage
 */
export async function loadTodos(): Promise<Todo[]> {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.TODOS);
    if (data) {
      const todos = JSON.parse(data);
      // Convert date strings back to Date objects
      return todos.map((todo: Todo) => ({
        ...todo,
        createdAt: new Date(todo.createdAt),
        dueDate: todo.dueDate ? new Date(todo.dueDate) : undefined,
      }));
    }
    return [];
  } catch (error) {
    console.error('Error loading todos:', error);
    return [];
  }
}

/**
 * Save todos to storage
 */
export async function saveTodos(todos: Todo[]): Promise<void> {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.TODOS, JSON.stringify(todos));
  } catch (error) {
    console.error('Error saving todos:', error);
  }
}

/**
 * Load chat history from storage
 */
export async function loadChatHistory(): Promise<Message[]> {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
    if (data) {
      const messages = JSON.parse(data);
      return messages.map((msg: Message) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      }));
    }
    return [];
  } catch (error) {
    console.error('Error loading chat history:', error);
    return [];
  }
}

/**
 * Save chat history to storage
 */
export async function saveChatHistory(messages: Message[]): Promise<void> {
  try {
    // Keep only last 100 messages
    const recentMessages = messages.slice(-100);
    await AsyncStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(recentMessages));
  } catch (error) {
    console.error('Error saving chat history:', error);
  }
}

/**
 * Clear all app data
 */
export async function clearAllData(): Promise<void> {
  try {
    await AsyncStorage.multiRemove([
      STORAGE_KEYS.TODOS,
      STORAGE_KEYS.CHAT_HISTORY,
      STORAGE_KEYS.SETTINGS,
    ]);
  } catch (error) {
    console.error('Error clearing data:', error);
  }
}

export default {
  loadTodos,
  saveTodos,
  loadChatHistory,
  saveChatHistory,
  clearAllData,
};
