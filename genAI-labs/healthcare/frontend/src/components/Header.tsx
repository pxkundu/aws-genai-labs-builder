'use client'

import { useState } from 'react'
import { Bars3Icon, BellIcon, UserCircleIcon } from '@heroicons/react/24/outline'
import { HeartIcon } from '@heroicons/react/24/solid'

interface HeaderProps {
  onMenuClick: () => void
  activeTab: string
  onTabChange: (tab: string) => void
}

export function Header({ onMenuClick, activeTab, onTabChange }: HeaderProps) {
  const [notifications] = useState(3) // Mock notification count

  const tabs = [
    { id: 'chat', label: 'Chat', icon: '💬' },
    { id: 'knowledge', label: 'Knowledge', icon: '📚' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ]

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left side */}
          <div className="flex items-center">
            <button
              type="button"
              className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 lg:hidden"
              onClick={onMenuClick}
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            
            <div className="flex items-center ml-4 lg:ml-0">
              <HeartIcon className="h-8 w-8 text-healthcare-600" />
              <div className="ml-3">
                <h1 className="text-xl font-semibold text-gray-900">
                  Healthcare ChatGPT
                </h1>
                <p className="text-sm text-gray-500">AI-Powered Healthcare Assistant</p>
              </div>
            </div>
          </div>

          {/* Center - Tabs */}
          <div className="hidden md:flex items-center space-x-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                  activeTab === tab.id
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button
              type="button"
              className="relative p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-lg"
            >
              <BellIcon className="h-6 w-6" />
              {notifications > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 bg-emergency-500 text-white text-xs rounded-full flex items-center justify-center">
                  {notifications}
                </span>
              )}
            </button>

            {/* User menu */}
            <button
              type="button"
              className="flex items-center space-x-2 p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-lg"
            >
              <UserCircleIcon className="h-6 w-6" />
              <span className="hidden sm:block text-sm font-medium text-gray-700">
                Dr. Smith
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
