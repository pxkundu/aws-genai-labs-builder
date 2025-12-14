/**
 * TodoItem Component - Individual todo item display
 */

import React from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  Animated,
} from 'react-native';

import { useApp } from '../context/AppContext';
import { Todo } from '../types';

interface TodoItemProps {
  todo: Todo;
}

export function TodoItem({ todo }: TodoItemProps) {
  const { toggleTodo, deleteTodo } = useApp();

  // Format due date
  const formatDueDate = (date?: Date) => {
    if (!date) return null;
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  // Priority colors
  const priorityColors = {
    high: '#EF4444',
    medium: '#F59E0B',
    low: '#22C55E',
  };

  return (
    <View style={[styles.container, todo.completed && styles.completedContainer]}>
      {/* Checkbox */}
      <TouchableOpacity
        style={[styles.checkbox, todo.completed && styles.checkboxCompleted]}
        onPress={() => toggleTodo(todo.id)}
      >
        {todo.completed && <Text style={styles.checkmark}>✓</Text>}
      </TouchableOpacity>

      {/* Content */}
      <View style={styles.content}>
        <Text style={[styles.title, todo.completed && styles.titleCompleted]}>
          {todo.title}
        </Text>

        {/* Meta info */}
        <View style={styles.meta}>
          {todo.dueDate && (
            <View style={styles.dueDateContainer}>
              <Text style={styles.dueDate}>📅 {formatDueDate(todo.dueDate)}</Text>
            </View>
          )}

          {todo.priority && (
            <View
              style={[
                styles.priorityBadge,
                { backgroundColor: priorityColors[todo.priority] + '20' },
              ]}
            >
              <View
                style={[
                  styles.priorityDot,
                  { backgroundColor: priorityColors[todo.priority] },
                ]}
              />
              <Text
                style={[styles.priorityText, { color: priorityColors[todo.priority] }]}
              >
                {todo.priority}
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* Delete Button */}
      <TouchableOpacity
        style={styles.deleteButton}
        onPress={() => deleteTodo(todo.id)}
      >
        <Text style={styles.deleteText}>×</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  completedContainer: {
    opacity: 0.7,
    backgroundColor: '#f9f9f9',
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#4A90D9',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  checkboxCompleted: {
    backgroundColor: '#4A90D9',
  },
  checkmark: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    color: '#333',
    marginBottom: 4,
  },
  titleCompleted: {
    textDecorationLine: 'line-through',
    color: '#999',
  },
  meta: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 8,
  },
  dueDateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dueDate: {
    fontSize: 12,
    color: '#666',
  },
  priorityBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  priorityDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 4,
  },
  priorityText: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  deleteButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 8,
  },
  deleteText: {
    fontSize: 20,
    color: '#999',
    fontWeight: '300',
  },
});

export default TodoItem;
