'use client'

import { useState, useRef, useEffect } from 'react'
import { PlusIcon, PaperAirplaneIcon, DocumentArrowUpIcon } from '@heroicons/react/24/outline'
import ReactMarkdown from 'react-markdown'
import dynamic from 'next/dynamic'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: string
}

interface UploadedFile {
  id: string
  name: string
  type: string
  size: number
}

function VACAssessmentChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [initialized, setInitialized] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Initialize with welcome message after component mounts
  useEffect(() => {
    if (!initialized) {
      const welcomeMessage: Message = {
        id: 'welcome-1',
        content: `Hello! I'm the VAC AI Assessment Assistant. I can help you assess veteran disability claims using Canada's Table of Disabilities 2019.

**To get started:**
- Upload medical documents (MQ, Record of Assessment, medical reports)
- Ask questions about disability ratings or conditions
- Request assessments for specific cases

**Supported file types:** PDF, DOCX, TXT, JSON

How can I assist with your VAC assessment today?`,
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString()
      }
      setMessages([welcomeMessage])
      setInitialized(true)
    }
  }, [initialized])

  const handleSendMessage = async () => {
    if (!inputText.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputText.trim(),
      role: 'user',
      timestamp: new Date().toLocaleTimeString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)

    try {
      // Make API call to chat endpoint via Next.js proxy
      const response = await fetch('/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputText.trim(),
          conversation_id: 'web-chat-' + Date.now(),
          files: uploadedFiles.map(f => f.id)
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('API Response:', data)  // Debug logging
        
        const assistantMessage: Message = {
          id: Date.now().toString() + '_ai',
          content: data.message || 'I apologize, but I encountered an issue processing your request. Please try again.',
          role: 'assistant',
          timestamp: new Date().toLocaleTimeString()
        }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        throw new Error('Failed to get response')
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: Date.now().toString() + '_error',
        content: 'I apologize, but I\'m currently unable to process your request. Please check that the backend API is running and try again.',
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    for (const file of Array.from(files)) {
      // Validate file type
      const allowedTypes = ['.pdf', '.docx', '.txt', '.json']
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()

      if (!allowedTypes.includes(fileExtension)) {
        alert(`File type ${fileExtension} not allowed. Please upload PDF, DOCX, TXT, or JSON files.`)
        continue
      }

      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        alert(`File ${file.name} is too large. Maximum size is 10MB.`)
        continue
      }

      try {
        const formData = new FormData()
        formData.append('files', file)

        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        })

        if (response.ok) {
          const result = await response.json()
          const newFile: UploadedFile = {
            id: result.files[0]?.id || Date.now().toString(),
            name: file.name,
            type: file.type,
            size: file.size
          }

          setUploadedFiles(prev => [...prev, newFile])

          // Add a system message about the upload
          const uploadMessage: Message = {
            id: Date.now().toString() + '_upload',
            content: `Successfully uploaded: ${file.name}. I can now analyze this document for your assessment.`,
            role: 'assistant',
            timestamp: new Date().toLocaleTimeString()
          }
          setMessages(prev => [...prev, uploadMessage])
        } else {
          throw new Error('Upload failed')
        }
      } catch (error) {
        console.error('Upload error:', error)
        alert(`Failed to upload ${file.name}. Please try again.`)
      }
    }

    // Clear the input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen bg-gray-50" suppressHydrationWarning>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">Veterans Affairs Canada Disability Assessments</h1>
        <p className="text-sm text-gray-600 mt-1">
          Please upload your MQ, Record of Assessment, medical reports, and other documents for a disability assessment.
        </p>
      </div>

      {/* Main Chat Interface */}
      <div className="flex flex-col h-[calc(100vh-5rem)]">

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl px-4 py-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-200 text-gray-900'
                  }`}
                >
                  <div className={`prose prose-sm max-w-none ${
                    message.role === 'user' ? 'prose-invert' : ''
                  }`}>
                    <ReactMarkdown>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                  <div className={`text-xs mt-2 ${
                    message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    {message.timestamp}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 px-4 py-3 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600">AI is analyzing...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Uploaded Files Display */}
        {uploadedFiles.length > 0 && (
          <div className="border-t border-gray-200 bg-gray-50 px-6 py-3">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center space-x-2 mb-2">
                <DocumentArrowUpIcon className="h-5 w-5 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Uploaded Files:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {uploadedFiles.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center space-x-2 bg-white border border-gray-300 rounded-md px-3 py-1 text-sm"
                  >
                    <span className="text-gray-700">{file.name}</span>
                    <span className="text-gray-500">({formatFileSize(file.size)})</span>
                    <button
                      onClick={() => removeFile(file.id)}
                      className="text-red-500 hover:text-red-700 ml-1"
                      title="Remove file"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white px-6 py-4" suppressHydrationWarning>
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-3">

              {/* File Upload Button */}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex-shrink-0 p-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                title="Upload documents"
              >
                <PlusIcon className="h-5 w-5 text-gray-600" />
              </button>

              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.json"
                onChange={handleFileUpload}
                className="hidden"
              />

              {/* Text Input */}
              <div className="flex-1" suppressHydrationWarning>
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSendMessage()
                    }
                  }}
                  placeholder="Upload your MQ, Record of Assessment, medical reports and ask me to assess the veteran's disability case..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={3}
                  disabled={isLoading}
                  suppressHydrationWarning
                />
              </div>

              {/* Send Button */}
              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim() || isLoading}
                className="flex-shrink-0 p-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 rounded-full transition-colors"
                title="Send message"
              >
                <PaperAirplaneIcon className="h-5 w-5 text-white" />
              </button>
            </div>

            <div className="mt-2 text-xs text-gray-500 text-center">
              Press Enter to send, Shift+Enter for new line. Upload MQ, Record of Assessment, medical reports (PDF, DOCX, TXT, JSON).
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Export as a dynamic component to disable SSR and avoid hydration issues
export default dynamic(() => Promise.resolve(VACAssessmentChat), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading VAC Assessment Interface...</p>
      </div>
    </div>
  )
})
