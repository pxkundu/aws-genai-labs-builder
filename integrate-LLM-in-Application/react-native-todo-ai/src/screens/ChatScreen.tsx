/**
 * Chat Screen - AI Assistant Chat Interface
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';

import { useApp } from '../context/AppContext';
import { useAI } from '../hooks/useAI';
import { Message } from '../types';

// Initial welcome message
const WELCOME_MESSAGE: Message = {
  id: 'welcome',
  role: 'assistant',
  content: `👋 Hi! I'm your AI task assistant. I can help you:

• Manage and organize your tasks
• Create tasks from natural language
• Get productivity suggestions
• Answer questions about your todos

Try asking: "What should I focus on today?"`,
  timestamp: new Date(),
};

// Quick suggestion buttons
const QUICK_SUGGESTIONS = [
  'What should I prioritize?',
  'Help me plan my day',
  'Add a task',
];

export function ChatScreen() {
  const { state, addTodo, addMessage } = useApp();
  const { sendMessage, loading, error } = useAI();
  
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  // Initialize with welcome message if empty
  const messages = state.chatMessages.length > 0 
    ? state.chatMessages 
    : [WELCOME_MESSAGE];

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages.length]);

  // Handle sending a message
  const handleSend = async () => {
    if (!inputText.trim() || loading) return;

    const userMessage = inputText.trim();
    setInputText('');

    // Add user message
    addMessage('user', userMessage);

    // Build context from todos
    const todoContext = state.todos
      .map(t => `- [${t.completed ? 'x' : ' '}] ${t.title}`)
      .join('\n');

    // Get AI response
    const response = await sendMessage(userMessage, todoContext);

    // Add AI response
    addMessage('assistant', response.message);

    // Check if AI suggested creating a task
    if (response.parsedTask?.title) {
      // Ask user to confirm
      addMessage(
        'assistant',
        `Would you like me to add this task?\n📝 "${response.parsedTask.title}"`
      );
    }
  };

  // Handle quick suggestion tap
  const handleSuggestion = (suggestion: string) => {
    setInputText(suggestion);
  };

  // Render a single message
  const renderMessage = ({ item }: { item: Message }) => {
    const isUser = item.role === 'user';
    
    return (
      <View style={[styles.messageContainer, isUser && styles.userMessageContainer]}>
        <View style={[styles.messageBubble, isUser ? styles.userBubble : styles.aiBubble]}>
          {!isUser && <Text style={styles.aiIcon}>🤖</Text>}
          <Text style={[styles.messageText, isUser && styles.userMessageText]}>
            {item.content}
          </Text>
        </View>
        <Text style={[styles.timestamp, isUser && styles.userTimestamp]}>
          {formatTime(item.timestamp)}
        </Text>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={100}
    >
      {/* Messages List */}
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={renderMessage}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContent}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
      />

      {/* Loading Indicator */}
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color="#4A90D9" />
          <Text style={styles.loadingText}>AI is thinking...</Text>
        </View>
      )}

      {/* Error Message */}
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>⚠️ {error.message}</Text>
        </View>
      )}

      {/* Quick Suggestions */}
      {messages.length <= 1 && (
        <View style={styles.suggestionsContainer}>
          {QUICK_SUGGESTIONS.map((suggestion, index) => (
            <TouchableOpacity
              key={index}
              style={styles.suggestionButton}
              onPress={() => handleSuggestion(suggestion)}
            >
              <Text style={styles.suggestionText}>{suggestion}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Input Area */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Ask me anything about your tasks..."
          value={inputText}
          onChangeText={setInputText}
          onSubmitEditing={handleSend}
          returnKeyType="send"
          multiline
          maxLength={500}
        />
        <TouchableOpacity
          style={[styles.sendButton, (!inputText.trim() || loading) && styles.sendButtonDisabled]}
          onPress={handleSend}
          disabled={!inputText.trim() || loading}
        >
          <Text style={styles.sendButtonText}>
            {loading ? '...' : '➤'}
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

// Helper: Format timestamp
function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    padding: 12,
    paddingBottom: 20,
  },
  messageContainer: {
    marginBottom: 12,
    maxWidth: '85%',
  },
  userMessageContainer: {
    alignSelf: 'flex-end',
  },
  messageBubble: {
    padding: 12,
    borderRadius: 16,
  },
  userBubble: {
    backgroundColor: '#4A90D9',
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    backgroundColor: '#fff',
    borderBottomLeftRadius: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  aiIcon: {
    fontSize: 16,
    marginBottom: 4,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
    color: '#333',
  },
  userMessageText: {
    color: '#fff',
  },
  timestamp: {
    fontSize: 11,
    color: '#999',
    marginTop: 4,
    marginLeft: 4,
  },
  userTimestamp: {
    textAlign: 'right',
    marginRight: 4,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 8,
    backgroundColor: '#E8F4FD',
  },
  loadingText: {
    marginLeft: 8,
    color: '#4A90D9',
    fontSize: 14,
  },
  errorContainer: {
    padding: 8,
    backgroundColor: '#FEE2E2',
  },
  errorText: {
    color: '#DC2626',
    fontSize: 14,
    textAlign: 'center',
  },
  suggestionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  suggestionButton: {
    backgroundColor: '#E8F4FD',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 16,
    margin: 4,
  },
  suggestionText: {
    color: '#4A90D9',
    fontSize: 13,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    minHeight: 44,
    maxHeight: 100,
    backgroundColor: '#f5f5f5',
    borderRadius: 22,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 16,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#4A90D9',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 8,
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
  },
  sendButtonText: {
    color: '#fff',
    fontSize: 20,
  },
});

export default ChatScreen;
