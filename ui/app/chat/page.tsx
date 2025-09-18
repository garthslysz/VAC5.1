'use client'

import { useState, useEffect, useRef, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import {
  PaperAirplaneIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import { DashboardLayout } from '../../components/DashboardLayout'
import { useApp } from '../providers'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  metadata?: any
  function_calls?: any[]
}

function AssessmentChatContent() {
  const { api, currentCase, setCurrentCase } = useApp()
  const searchParams = useSearchParams()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [caseId, setCaseId] = useState<string>('')
  const [assessmentStatus, setAssessmentStatus] = useState<'not-started' | 'in-progress' | 'completed'>('not-started')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const paramCaseId = searchParams.get('case_id')
    if (paramCaseId) {
      setCaseId(paramCaseId)
      setCurrentCase({ id: paramCaseId, veteran_name: 'Loading...' })
    }
  }, [searchParams, setCurrentCase])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Add welcome message when component mounts
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome-1',
        role: 'assistant',
        content: `Hello! I'm your VAC assessment assistant. I'll help you conduct a comprehensive disability assessment using the Table of Disabilities 2019.

To get started, you can:
- Tell me about the veteran's conditions and symptoms
- Upload medical documents for analysis
- Ask questions about specific VAC ToD criteria

What case would you like to assess today?`,
        timestamp: new Date().toISOString()
      }
      setMessages([welcomeMessage])
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setLoading(true)

    try {
      const response = await api.sendChatMessage({
        message: inputMessage,
        conversation_id: conversationId || undefined,
        case_id: caseId || undefined,
        context: `Current case ID: ${caseId || 'New case'}, Assessment status: ${assessmentStatus}`
      })

      if (!conversationId) {
        setConversationId(response.conversation_id)
      }

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        metadata: response.metadata,
        function_calls: response.function_calls
      }

      setMessages(prev => [...prev, assistantMessage])

      // Update assessment status based on response
      if (response.metadata?.assessment_complete) {
        setAssessmentStatus('completed')
      } else if (assessmentStatus === 'not-started') {
        setAssessmentStatus('in-progress')
      }

    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again or contact technical support if the issue persists.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const startNewAssessment = () => {
    setMessages([])
    setConversationId(null)
    setCaseId('')
    setAssessmentStatus('not-started')
    setCurrentCase(null)
  }

  const getStatusIcon = () => {
    switch (assessmentStatus) {
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-600" />
      case 'in-progress':
        return <ClockIcon className="w-5 h-5 text-yellow-600" />
      default:
        return <ExclamationCircleIcon className="w-5 h-5 text-vac-gray-400" />
    }
  }

  const getStatusText = () => {
    switch (assessmentStatus) {
      case 'completed':
        return 'Assessment Complete'
      case 'in-progress':
        return 'Assessment In Progress'
      default:
        return 'Ready to Start'
    }
  }

  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user'
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`max-w-3xl ${isUser ? 'chat-message-user' : 'chat-message-assistant'}`}>
          <div className="whitespace-pre-wrap">{message.content}</div>
          
          {/* Show function call results */}
          {message.function_calls && message.function_calls.length > 0 && (
            <div className="mt-3 space-y-2">
              {message.function_calls.map((call, idx) => (
                <div key={idx} className="text-xs bg-vac-gray-100 rounded p-2">
                  <div className="font-medium text-vac-gray-700">
                    🔍 {call.function.replace('_', ' ')} 
                  </div>
                  {call.result && (
                    <div className="mt-1 text-vac-gray-600">
                      {typeof call.result === 'object' ? 
                        JSON.stringify(call.result, null, 2).substring(0, 200) + '...' :
                        call.result.toString().substring(0, 200)
                      }
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          
          <div className="text-xs opacity-70 mt-2">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    )
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col h-screen">
        {/* Header */}
        <div className="bg-white border-b border-vac-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-vac-gray-900">VAC Assessment Chat</h1>
              <p className="text-sm text-vac-gray-600">
                {caseId ? `Case: ${caseId}` : 'Start a new assessment conversation'}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {getStatusIcon()}
                <span className="text-sm font-medium text-vac-gray-700">{getStatusText()}</span>
              </div>
              <button
                onClick={startNewAssessment}
                className="vac-button-secondary text-sm"
              >
                New Assessment
              </button>
            </div>
          </div>
        </div>

        {/* Case Info Bar */}
        {caseId && (
          <div className="bg-vac-blue-50 border-b border-vac-blue-200 px-6 py-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-4">
                <span className="text-vac-blue-900 font-medium">Case ID: {caseId}</span>
                <span className="text-vac-blue-700">
                  Conversation ID: {conversationId?.substring(0, 8)}...
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <DocumentTextIcon className="w-4 h-4 text-vac-blue-600" />
                <span className="text-vac-blue-700">ToD 2019 Active</span>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-vac-gray-50 px-6 py-4">
          <div className="max-w-4xl mx-auto">
            {messages.map(renderMessage)}
            {loading && (
              <div className="flex justify-start mb-4">
                <div className="chat-message-assistant">
                  <div className="flex items-center space-x-2">
                    <div className="loading-spinner w-4 h-4"></div>
                    <span>VAC Assistant is analyzing...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white border-t border-vac-gray-200 px-6 py-2">
          <div className="flex items-center space-x-2 text-sm">
            <span className="text-vac-gray-600">Quick actions:</span>
            <button
              onClick={() => setInputMessage("What conditions should I assess for this veteran?")}
              className="text-vac-blue-600 hover:text-vac-blue-700 px-2 py-1 rounded hover:bg-vac-blue-50"
            >
              Start Assessment
            </button>
            <button
              onClick={() => setInputMessage("Calculate the combined disability rating")}
              className="text-vac-blue-600 hover:text-vac-blue-700 px-2 py-1 rounded hover:bg-vac-blue-50"
            >
              Calculate Rating
            </button>
            <button
              onClick={() => setInputMessage("Search VAC ToD for PTSD criteria")}
              className="text-vac-blue-600 hover:text-vac-blue-700 px-2 py-1 rounded hover:bg-vac-blue-50"
            >
              Search ToD
            </button>
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-vac-gray-200 px-6 py-4">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <label htmlFor="message-input" className="sr-only">
                Message
              </label>
              <textarea
                id="message-input"
                rows={3}
                className="vac-input resize-none"
                placeholder="Describe the veteran's conditions, ask about VAC ToD criteria, or request an assessment..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
              />
            </div>
            <div className="flex flex-col space-y-2">
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || loading}
                className="vac-button-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <PaperAirplaneIcon className="w-4 h-4" />
                <span>Send</span>
              </button>
              <button
                onClick={() => {/* Implement file upload */}}
                className="vac-button-secondary flex items-center space-x-2 text-sm"
              >
                <DocumentTextIcon className="w-4 h-4" />
                <span>Upload</span>
              </button>
            </div>
          </div>
          <div className="mt-2 text-xs text-vac-gray-500">
            Press Enter to send, Shift+Enter for new line. This chat uses VAC Table of Disabilities 2019.
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default function AssessmentChat() {
  return (
    <Suspense fallback={
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="loading-spinner w-8 h-8"></div>
        </div>
      </DashboardLayout>
    }>
      <AssessmentChatContent />
    </Suspense>
  )
}