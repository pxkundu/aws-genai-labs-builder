/**
 * React Native Todo App with AI Chat
 * Main Application Entry Point
 */
import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  SafeAreaView,
  StatusBar,
  TouchableOpacity,
  Text,
} from 'react-native';

import { TodoScreen } from './src/screens/TodoScreen';
import { ChatScreen } from './src/screens/ChatScreen';
import { AppProvider } from './src/context/AppContext';

type Screen = 'todos' | 'chat';

export default function App() {
  const [activeScreen, setActiveScreen] = useState<Screen>('todos');

  return (
    <AppProvider>
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" />
        
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>📝 Todo AI</Text>
        </View>

        {/* Main Content */}
        <View style={styles.content}>
          {activeScreen === 'todos' ? <TodoScreen /> : <ChatScreen />}
        </View>

        {/* Bottom Navigation */}
        <View style={styles.tabBar}>
          <TouchableOpacity
            style={[styles.tab, activeScreen === 'todos' && styles.activeTab]}
            onPress={() => setActiveScreen('todos')}
          >
            <Text style={[styles.tabIcon, activeScreen === 'todos' && styles.activeTabText]}>
              ✅
            </Text>
            <Text style={[styles.tabLabel, activeScreen === 'todos' && styles.activeTabText]}>
              Todos
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tab, activeScreen === 'chat' && styles.activeTab]}
            onPress={() => setActiveScreen('chat')}
          >
            <Text style={[styles.tabIcon, activeScreen === 'chat' && styles.activeTabText]}>
              🤖
            </Text>
            <Text style={[styles.tabLabel, activeScreen === 'chat' && styles.activeTabText]}>
              AI Chat
            </Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </AppProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#4A90D9',
    paddingVertical: 16,
    paddingHorizontal: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  content: {
    flex: 1,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingBottom: 20,
    paddingTop: 10,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  activeTab: {
    borderTopWidth: 2,
    borderTopColor: '#4A90D9',
  },
  tabIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  tabLabel: {
    fontSize: 12,
    color: '#666',
  },
  activeTabText: {
    color: '#4A90D9',
    fontWeight: '600',
  },
});
