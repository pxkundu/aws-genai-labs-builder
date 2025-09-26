'use client'

import { useState } from 'react'
import { ChatInterface } from '@/components/ChatInterface'
import { Header } from '@/components/Header'
import { Sidebar } from '@/components/Sidebar'
import { EmergencyAlert } from '@/components/EmergencyAlert'
import { KnowledgeBase } from '@/components/KnowledgeBase'
import { Analytics } from '@/components/Analytics'
import { Settings } from '@/components/Settings'

type TabType = 'chat' | 'knowledge' | 'analytics' | 'settings'

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<TabType>('chat')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatInterface />
      case 'knowledge':
        return <KnowledgeBase />
      case 'analytics':
        return <Analytics />
      case 'settings':
        return <Settings />
      default:
        return <ChatInterface />
    }
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header 
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar 
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
        
        <main className="flex-1 flex flex-col overflow-hidden">
          <EmergencyAlert />
          <div className="flex-1 overflow-hidden">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  )
}
