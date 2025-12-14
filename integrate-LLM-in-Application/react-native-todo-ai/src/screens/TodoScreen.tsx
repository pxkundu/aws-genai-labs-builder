/**
 * Todo Screen - Main todo list view
 */

import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';

import { useApp } from '../context/AppContext';
import { TodoItem } from '../components/TodoItem';
import { useAI } from '../hooks/useAI';
import { TodoFilter } from '../types';

export function TodoScreen() {
  const { state, addTodo, filteredTodos, dispatch } = useApp();
  const { parseTask, loading: aiLoading } = useAI();
  
  const [inputText, setInputText] = useState('');
  const [useAIInput, setUseAIInput] = useState(false);

  // Handle adding a new todo
  const handleAddTodo = async () => {
    if (!inputText.trim()) return;

    if (useAIInput) {
      // Use AI to parse natural language
      const parsedTask = await parseTask(inputText);
      if (parsedTask?.title) {
        addTodo(parsedTask.title, {
          dueDate: parsedTask.dueDate,
          priority: parsedTask.priority,
        });
      } else {
        // Fallback to simple add
        addTodo(inputText.trim());
      }
    } else {
      // Simple add
      addTodo(inputText.trim());
    }

    setInputText('');
  };

  // Filter buttons
  const filters: { key: TodoFilter; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'active', label: 'Active' },
    { key: 'completed', label: 'Done' },
  ];

  const completedCount = state.todos.filter(t => t.completed).length;
  const totalCount = state.todos.length;

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {/* Stats */}
      <View style={styles.stats}>
        <Text style={styles.statsText}>
          {completedCount}/{totalCount} completed
        </Text>
      </View>

      {/* Filter Tabs */}
      <View style={styles.filterContainer}>
        {filters.map((filter) => (
          <TouchableOpacity
            key={filter.key}
            style={[
              styles.filterButton,
              state.filter === filter.key && styles.filterButtonActive,
            ]}
            onPress={() => dispatch({ type: 'SET_FILTER', payload: filter.key })}
          >
            <Text
              style={[
                styles.filterText,
                state.filter === filter.key && styles.filterTextActive,
              ]}
            >
              {filter.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Todo List */}
      <FlatList
        data={filteredTodos}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <TodoItem todo={item} />}
        style={styles.list}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcon}>📝</Text>
            <Text style={styles.emptyText}>No tasks yet</Text>
            <Text style={styles.emptySubtext}>Add your first task below</Text>
          </View>
        }
      />

      {/* Add Todo Input */}
      <View style={styles.inputContainer}>
        {/* AI Toggle */}
        <TouchableOpacity
          style={[styles.aiToggle, useAIInput && styles.aiToggleActive]}
          onPress={() => setUseAIInput(!useAIInput)}
        >
          <Text style={styles.aiToggleText}>🤖</Text>
        </TouchableOpacity>

        <TextInput
          style={styles.input}
          placeholder={
            useAIInput
              ? 'Try: "Buy groceries tomorrow"'
              : 'Add a new task...'
          }
          value={inputText}
          onChangeText={setInputText}
          onSubmitEditing={handleAddTodo}
          returnKeyType="done"
        />

        <TouchableOpacity
          style={[styles.addButton, !inputText.trim() && styles.addButtonDisabled]}
          onPress={handleAddTodo}
          disabled={!inputText.trim() || aiLoading}
        >
          <Text style={styles.addButtonText}>
            {aiLoading ? '...' : '+'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* AI Input Hint */}
      {useAIInput && (
        <View style={styles.aiHint}>
          <Text style={styles.aiHintText}>
            🤖 AI mode: Describe your task naturally
          </Text>
        </View>
      )}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  stats: {
    padding: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  statsText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 14,
  },
  filterContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  filterButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginHorizontal: 4,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
  },
  filterButtonActive: {
    backgroundColor: '#4A90D9',
  },
  filterText: {
    fontSize: 14,
    color: '#666',
  },
  filterTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  list: {
    flex: 1,
  },
  listContent: {
    padding: 12,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#666',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    alignItems: 'center',
  },
  aiToggle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  aiToggleActive: {
    backgroundColor: '#E8F4FD',
    borderWidth: 2,
    borderColor: '#4A90D9',
  },
  aiToggleText: {
    fontSize: 18,
  },
  input: {
    flex: 1,
    height: 44,
    backgroundColor: '#f5f5f5',
    borderRadius: 22,
    paddingHorizontal: 16,
    fontSize: 16,
  },
  addButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#4A90D9',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 8,
  },
  addButtonDisabled: {
    backgroundColor: '#ccc',
  },
  addButtonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '600',
  },
  aiHint: {
    backgroundColor: '#E8F4FD',
    padding: 8,
  },
  aiHintText: {
    textAlign: 'center',
    color: '#4A90D9',
    fontSize: 12,
  },
});

export default TodoScreen;
