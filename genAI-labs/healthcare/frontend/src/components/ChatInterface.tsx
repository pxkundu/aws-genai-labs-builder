'use client'

import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon, StopIcon } from '@heroicons/react/24/outline'
import { useChat } from '@/hooks/useChat'
import { Message } from '@/components/Message'
import { TypingIndicator } from '@/components/TypingIndicator'
import { EmergencyAlert } from '@/components/EmergencyAlert'
import { KnowledgeSuggestions } from '@/components/KnowledgeSuggestions'

export function ChatInterface() {
  const [input, setInput] = useState('')
  const [isEmergency, setIsEmergency] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const {
    messages,
    isLoading,
    sendMessage,
    stopGeneration,
    clearChat,
    error
  } = useChat()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const message = input.trim()
    setInput('')
    
    // Check for emergency keywords
    const emergencyKeywords = [
      'chest pain', 'heart attack', 'stroke', 'difficulty breathing',
      'severe bleeding', 'unconscious', 'suicidal', 'overdose',
      'severe allergic reaction', 'seizure', 'choking'
    ]
    
    const isEmergencyMessage = emergencyKeywords.some(keyword => 
      message.toLowerCase().includes(keyword)
    )
    
    if (isEmergencyMessage) {
      setIsEmergency(true)
    }

    await sendMessage(message)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Healthcare Assistant</h2>
            <p className="text-sm text-gray-500">
              Ask me anything about healthcare, symptoms, or medical information
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={clearChat}
              className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1 rounded-md hover:bg-gray-100"
            >
              Clear Chat
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-500">Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Emergency Alert */}
      {isEmergency && (
        <EmergencyAlert 
          onDismiss={() => setIsEmergency(false)}
          message="Emergency detected. Please call 911 immediately if this is a medical emergency."
        />
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto chat-container px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl">🏥</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to Healthcare Assistant
            </h3>
            <p className="text-gray-500 mb-6 max-w-md">
              I'm here to help with your healthcare questions. Ask me about symptoms, 
              medications, treatments, or any medical concerns you might have.
            </p>
            <KnowledgeSuggestions onSelect={setInput} />
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-6 py-2">
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-700">
              Error: {error}. Please try again.
            </p>
          </div>
        </div>
      )}

      {/* Input Form */}
      <div className="flex-shrink-0 px-6 py-4 border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about symptoms, medications, treatments..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              rows={1}
              style={{ minHeight: '48px', maxHeight: '120px' }}
              disabled={isLoading}
            />
          </div>
          <div className="flex items-center space-x-2">
            {isLoading ? (
              <button
                type="button"
                onClick={stopGeneration}
                className="p-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <StopIcon className="h-5 w-5" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={!input.trim()}
                className="p-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <PaperAirplaneIcon className="h-5 w-5" />
              </button>
            )}
          </div>
        </form>
        
        {/* Disclaimer */}
        <div className="mt-3 text-xs text-gray-500">
          <p>
            ⚠️ This AI assistant is for informational purposes only and does not replace 
            professional medical advice. Always consult with a healthcare provider for 
            medical decisions.
          </p>
        </div>
      </div>
    </div>
  )
}
