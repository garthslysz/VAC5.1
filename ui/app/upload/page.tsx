'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  DocumentTextIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  TrashIcon,
  EyeIcon,
} from '@heroicons/react/24/outline'
import { DashboardLayout } from '../../components/DashboardLayout'
import { useApp } from '../providers'

interface UploadedFile {
  id: string
  file: File
  name: string
  size: number
  type: string
  status: 'uploading' | 'processed' | 'failed'
  progress: number
  result?: any
  error?: string
}

export default function DocumentUpload() {
  const { api } = useApp()
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [caseId, setCaseId] = useState('')
  const [dragActive, setDragActive] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setDragActive(false)
    
    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      id: `file-${Date.now()}-${Math.random()}`,
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploading',
      progress: 0
    }))

    setFiles(prev => [...prev, ...newFiles])

    // Process each file
    newFiles.forEach(uploadFile)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'application/json': ['.json']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  const uploadFile = async (fileData: UploadedFile) => {
    try {
      // Update progress
      setFiles(prev => prev.map(f => 
        f.id === fileData.id 
          ? { ...f, progress: 25 }
          : f
      ))

      const result = await api.uploadFiles([fileData.file], caseId || undefined)
      
      // Simulate progress updates
      await new Promise(resolve => setTimeout(resolve, 500))
      setFiles(prev => prev.map(f => 
        f.id === fileData.id 
          ? { ...f, progress: 75 }
          : f
      ))

      await new Promise(resolve => setTimeout(resolve, 500))
      setFiles(prev => prev.map(f => 
        f.id === fileData.id 
          ? { 
              ...f, 
              status: 'processed', 
              progress: 100,
              result: result.files?.[0] || result
            }
          : f
      ))

    } catch (error) {
      console.error('Upload failed:', error)
      setFiles(prev => prev.map(f => 
        f.id === fileData.id 
          ? { 
              ...f, 
              status: 'failed', 
              progress: 0,
              error: error instanceof Error ? error.message : 'Upload failed'
            }
          : f
      ))
    }
  }

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return '📄'
    if (type.includes('word') || type.includes('document')) return '📝'
    if (type.includes('text')) return '📃'
    if (type.includes('json')) return '🔧'
    return '📎'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
        return <CheckCircleIcon className="w-5 h-5 text-green-600" />
      case 'failed':
        return <ExclamationCircleIcon className="w-5 h-5 text-red-600" />
      default:
        return <div className="loading-spinner w-4 h-4" />
    }
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-vac-gray-900">Document Upload</h1>
          <p className="mt-2 text-sm text-vac-gray-600">
            Upload medical records, assessments, and supporting documents for VAC evaluation.
          </p>
        </div>

        {/* Case ID Input */}
        <div className="mb-6">
          <div className="max-w-md">
            <label htmlFor="case-id" className="block text-sm font-medium text-vac-gray-700 mb-2">
              Case ID (Optional)
            </label>
            <input
              type="text"
              id="case-id"
              className="vac-input"
              placeholder="e.g., VAC-2024-001"
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
            />
            <p className="mt-1 text-xs text-vac-gray-500">
              Associate these documents with a specific case for organized tracking.
            </p>
          </div>
        </div>

        {/* Upload Area */}
        <div className="mb-8">
          <div
            {...getRootProps()}
            className={`
              relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive || dragActive
                ? 'border-vac-blue-400 bg-vac-blue-50'
                : 'border-vac-gray-300 hover:border-vac-gray-400'
              }
            `}
          >
            <input {...getInputProps()} />
            <CloudArrowUpIcon className="w-12 h-12 text-vac-gray-400 mx-auto mb-4" />
            
            {isDragActive ? (
              <div className="text-vac-blue-600">
                <p className="text-lg font-medium">Drop files here to upload</p>
                <p className="text-sm">Release to start processing</p>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium text-vac-gray-900 mb-2">
                  Upload Medical Documents
                </p>
                <p className="text-sm text-vac-gray-600 mb-4">
                  Drag and drop files here, or click to select files
                </p>
                <div className="text-xs text-vac-gray-500">
                  <p>Supported formats: PDF, DOCX, DOC, TXT, JSON</p>
                  <p>Maximum file size: 10MB each</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="vac-card">
            <h2 className="text-lg font-semibold text-vac-gray-900 mb-4">
              Uploaded Files ({files.length})
            </h2>
            
            <div className="space-y-4">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center justify-between p-4 bg-vac-gray-50 rounded-lg"
                >
                  <div className="flex items-center flex-1 min-w-0">
                    <div className="text-2xl mr-3">
                      {getFileIcon(file.type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-vac-gray-900 truncate">
                          {file.name}
                        </p>
                        {getStatusIcon(file.status)}
                      </div>
                      
                      <div className="flex items-center space-x-4 text-xs text-vac-gray-500">
                        <span>{formatFileSize(file.size)}</span>
                        <span className="capitalize">{file.status.replace('-', ' ')}</span>
                        {file.status === 'uploading' && (
                          <span>{file.progress}% complete</span>
                        )}
                      </div>

                      {/* Progress Bar */}
                      {file.status === 'uploading' && (
                        <div className="mt-2 w-full bg-vac-gray-200 rounded-full h-1">
                          <div
                            className="bg-vac-blue-600 h-1 rounded-full transition-all duration-300"
                            style={{ width: `${file.progress}%` }}
                          />
                        </div>
                      )}

                      {/* Processing Results */}
                      {file.status === 'processed' && file.result && (
                        <div className="mt-2 text-xs">
                          {file.result.conditions_detected?.length > 0 && (
                            <div className="text-green-700">
                              ✓ Detected conditions: {file.result.conditions_detected.join(', ')}
                            </div>
                          )}
                          <div className="text-vac-gray-600">
                            Extracted {file.result.text_length || 0} characters of text
                          </div>
                        </div>
                      )}

                      {/* Error Message */}
                      {file.status === 'failed' && file.error && (
                        <div className="mt-2 text-xs text-red-600">
                          Error: {file.error}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2 ml-4">
                    {file.status === 'processed' && (
                      <button
                        className="p-2 text-vac-gray-400 hover:text-vac-gray-600 rounded-md hover:bg-white"
                        title="View details"
                      >
                        <EyeIcon className="w-4 h-4" />
                      </button>
                    )}
                    
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-2 text-vac-gray-400 hover:text-red-600 rounded-md hover:bg-white"
                      title="Remove file"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div className="mt-6 pt-4 border-t border-vac-gray-200">
              <div className="flex items-center justify-between text-sm">
                <div className="text-vac-gray-600">
                  {files.filter(f => f.status === 'processed').length} of {files.length} files processed successfully
                </div>
                
                <div className="flex items-center space-x-4">
                  {files.some(f => f.status === 'processed') && (
                    <button className="vac-button-primary">
                      Start Assessment
                    </button>
                  )}
                  
                  <button
                    onClick={() => setFiles([])}
                    className="vac-button-secondary"
                  >
                    Clear All
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Help Section */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-3">Document Upload Guidelines</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-blue-800">
            <div>
              <h4 className="font-medium mb-2">Recommended Documents:</h4>
              <ul className="list-disc list-inside space-y-1">
                <li>Medical examination reports</li>
                <li>Specialist consultation notes</li>
                <li>Diagnostic test results</li>
                <li>Previous VAC assessments</li>
                <li>Service medical records</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Processing Features:</h4>
              <ul className="list-disc list-inside space-y-1">
                <li>Automatic text extraction</li>
                <li>Medical condition detection</li>
                <li>Document classification</li>
                <li>Integration with VAC ToD</li>
                <li>Searchable content indexing</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}