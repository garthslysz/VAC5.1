'use client'

import { useState, useEffect } from 'react'
import {
  MagnifyingGlassIcon,
  BookOpenIcon,
  InformationCircleIcon,
  ChevronRightIcon,
  DocumentMagnifyingGlassIcon,
} from '@heroicons/react/24/outline'
import { DashboardLayout } from '../../components/DashboardLayout'
import { useApp } from '../providers'

interface Chapter {
  id: string
  title: string
  description: string
  condition_count: number
}

interface Condition {
  id: string
  name: string
  chapter: string
  symptoms: string[]
  relevance_score?: number
}

export default function VACToDrowser() {
  const { api } = useApp()
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [conditions, setConditions] = useState<Condition[]>([])
  const [selectedChapter, setSelectedChapter] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [activeTab, setActiveTab] = useState<'browse' | 'search'>('browse')

  useEffect(() => {
    loadChapters()
  }, [])

  useEffect(() => {
    if (selectedChapter) {
      loadChapterConditions(selectedChapter)
    }
  }, [selectedChapter])

  useEffect(() => {
    if (searchQuery.trim()) {
      performSearch()
    } else {
      setSearchResults([])
    }
  }, [searchQuery])

  const loadChapters = async () => {
    try {
      setLoading(true)
      const chaptersData = await api.getChapters()
      setChapters(chaptersData)
    } catch (error) {
      console.error('Failed to load chapters:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadChapterConditions = async (chapterId: string) => {
    try {
      const conditionsData = await api.getConditions(chapterId)
      setConditions(conditionsData)
    } catch (error) {
      console.error('Failed to load conditions:', error)
    }
  }

  const performSearch = async () => {
    try {
      const results = await api.searchDocuments(searchQuery, undefined, undefined, 20)
      setSearchResults(results.results || [])
    } catch (error) {
      console.error('Search failed:', error)
    }
  }

  const highlightSearchTerm = (text: string, term: string) => {
    if (!term) return text
    const regex = new RegExp(`(${term})`, 'gi')
    return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>')
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="flex items-center justify-center h-64">
            <div className="loading-spinner w-8 h-8"></div>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <BookOpenIcon className="w-8 h-8 text-vac-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-vac-gray-900">VAC Table of Disabilities 2019</h1>
              <p className="text-sm text-vac-gray-600">
                Browse and search the official Table of Disabilities for assessment criteria
              </p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-vac-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('browse')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'browse'
                    ? 'border-vac-blue-500 text-vac-blue-600'
                    : 'border-transparent text-vac-gray-500 hover:text-vac-gray-700 hover:border-vac-gray-300'
                }`}
              >
                Browse by Chapter
              </button>
              <button
                onClick={() => setActiveTab('search')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'search'
                    ? 'border-vac-blue-500 text-vac-blue-600'
                    : 'border-transparent text-vac-gray-500 hover:text-vac-gray-700 hover:border-vac-gray-300'
                }`}
              >
                Search Conditions
              </button>
            </nav>
          </div>
        </div>

        {/* Browse Tab */}
        {activeTab === 'browse' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Chapters List */}
            <div className="lg:col-span-1">
              <div className="vac-card">
                <h2 className="text-lg font-semibold text-vac-gray-900 mb-4">
                  Chapters ({chapters.length})
                </h2>
                <div className="space-y-2">
                  {chapters.map((chapter) => (
                    <button
                      key={chapter.id}
                      onClick={() => setSelectedChapter(chapter.id)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        selectedChapter === chapter.id
                          ? 'bg-vac-blue-100 text-vac-blue-900 border-vac-blue-200'
                          : 'hover:bg-vac-gray-50 text-vac-gray-900'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{chapter.title}</p>
                          <p className="text-xs text-vac-gray-600">
                            {chapter.condition_count} conditions
                          </p>
                        </div>
                        <ChevronRightIcon className="w-4 h-4 text-vac-gray-400" />
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Chapter Details */}
            <div className="lg:col-span-2">
              {selectedChapter ? (
                <div className="vac-card">
                  <div className="mb-6">
                    {chapters.find(c => c.id === selectedChapter) && (
                      <div>
                        <h2 className="text-xl font-semibold text-vac-gray-900 mb-2">
                          {chapters.find(c => c.id === selectedChapter)?.title}
                        </h2>
                        <p className="text-sm text-vac-gray-600 mb-4">
                          {chapters.find(c => c.id === selectedChapter)?.description}
                        </p>
                        <div className="flex items-center text-sm text-vac-gray-500">
                          <InformationCircleIcon className="w-4 h-4 mr-1" />
                          <span>{conditions.length} conditions in this chapter</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Conditions List */}
                  <div className="space-y-3">
                    <h3 className="text-lg font-medium text-vac-gray-900">Conditions</h3>
                    {conditions.length > 0 ? (
                      <div className="grid gap-4">
                        {conditions.map((condition) => (
                          <div
                            key={condition.id}
                            className="p-4 bg-vac-gray-50 rounded-lg hover:bg-vac-gray-100 transition-colors"
                          >
                            <h4 className="font-medium text-vac-gray-900 mb-2">
                              {condition.name}
                            </h4>
                            {condition.symptoms.length > 0 && (
                              <div>
                                <p className="text-xs text-vac-gray-600 mb-1">Common symptoms:</p>
                                <div className="flex flex-wrap gap-1">
                                  {condition.symptoms.slice(0, 5).map((symptom, idx) => (
                                    <span
                                      key={idx}
                                      className="inline-block px-2 py-1 text-xs bg-white text-vac-gray-700 rounded-full"
                                    >
                                      {symptom}
                                    </span>
                                  ))}
                                  {condition.symptoms.length > 5 && (
                                    <span className="inline-block px-2 py-1 text-xs bg-white text-vac-gray-500 rounded-full">
                                      +{condition.symptoms.length - 5} more
                                    </span>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-vac-gray-500">
                        <DocumentMagnifyingGlassIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No conditions loaded. Select a chapter to view its conditions.</p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="vac-card text-center py-12">
                  <BookOpenIcon className="w-16 h-16 text-vac-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-vac-gray-900 mb-2">
                    Select a Chapter
                  </h3>
                  <p className="text-vac-gray-600">
                    Choose a chapter from the left to view its conditions and criteria.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Search Tab */}
        {activeTab === 'search' && (
          <div>
            {/* Search Input */}
            <div className="mb-6">
              <div className="relative max-w-2xl">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-vac-gray-400" />
                </div>
                <input
                  type="text"
                  className="vac-input pl-10"
                  placeholder="Search conditions, symptoms, or criteria..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <p className="mt-2 text-sm text-vac-gray-600">
                Search across all VAC ToD conditions and criteria. Results are ranked by relevance.
              </p>
            </div>

            {/* Search Results */}
            {searchQuery && (
              <div className="vac-card">
                <h3 className="text-lg font-semibold text-vac-gray-900 mb-4">
                  Search Results ({searchResults.length})
                </h3>
                
                {searchResults.length > 0 ? (
                  <div className="space-y-6">
                    {searchResults.map((result, idx) => (
                      <div key={idx} className="border-b border-vac-gray-200 last:border-b-0 pb-6 last:pb-0">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-vac-gray-900">
                            <span
                              dangerouslySetInnerHTML={{
                                __html: highlightSearchTerm(result.title, searchQuery)
                              }}
                            />
                          </h4>
                          <div className="flex items-center text-sm text-vac-gray-500">
                            <span className="bg-vac-blue-100 text-vac-blue-700 px-2 py-1 rounded-full text-xs">
                              {result.source}
                            </span>
                          </div>
                        </div>
                        
                        <div className="text-sm text-vac-gray-600 mb-3">
                          <span
                            dangerouslySetInnerHTML={{
                              __html: highlightSearchTerm(result.content, searchQuery)
                            }}
                          />
                        </div>

                        {result.metadata?.symptoms && (
                          <div className="flex flex-wrap gap-1 mb-2">
                            {result.metadata.symptoms.slice(0, 3).map((symptom: string, symptomIdx: number) => (
                              <span
                                key={symptomIdx}
                                className="inline-block px-2 py-1 text-xs bg-vac-gray-100 text-vac-gray-700 rounded-full"
                              >
                                {symptom}
                              </span>
                            ))}
                          </div>
                        )}

                        <div className="flex items-center justify-between text-xs text-vac-gray-500">
                          <span>Chapter: {result.chapter || 'Unknown'}</span>
                          <span>Relevance: {Math.round((result.relevance_score || 0) * 100)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : searchQuery ? (
                  <div className="text-center py-8 text-vac-gray-500">
                    <MagnifyingGlassIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No results found for "{searchQuery}"</p>
                    <p className="text-sm mt-1">Try different keywords or check spelling</p>
                  </div>
                ) : null}
              </div>
            )}

            {/* Search Tips */}
            {!searchQuery && (
              <div className="bg-blue-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-blue-900 mb-3">Search Tips</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
                  <div>
                    <h4 className="font-medium mb-2">Search by Condition:</h4>
                    <ul className="list-disc list-inside space-y-1">
                      <li>PTSD</li>
                      <li>Lower back pain</li>
                      <li>Hearing loss</li>
                      <li>Anxiety disorder</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Search by Symptoms:</h4>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Chronic pain</li>
                      <li>Nightmares</li>
                      <li>Limited mobility</li>
                      <li>Memory problems</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}