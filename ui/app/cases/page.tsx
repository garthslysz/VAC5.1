'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import {
  UserGroupIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  CalendarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  PlusIcon,
} from '@heroicons/react/24/outline'
import { DashboardLayout } from '../../components/DashboardLayout'
import { useApp } from '../providers'

interface Case {
  id: string
  veteran_name: string
  status: 'pending' | 'in-progress' | 'completed' | 'review'
  disability_rating?: number
  conditions: string[]
  assigned_adjudicator: string
  created_date: string
  updated_date: string
  priority: 'low' | 'normal' | 'high' | 'urgent'
  documents_count: number
  assessment_progress: number
}

export default function CaseManagement() {
  const { api, user, setCurrentCase } = useApp()
  const [cases, setCases] = useState<Case[]>([])
  const [filteredCases, setFilteredCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'date' | 'priority' | 'rating'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  useEffect(() => {
    loadCases()
  }, [])

  useEffect(() => {
    filterAndSortCases()
  }, [cases, searchQuery, statusFilter, priorityFilter, sortBy, sortOrder])

  const loadCases = async () => {
    try {
      setLoading(true)
      
      // Mock data - in real implementation, this would be an API call
      const mockCases: Case[] = [
        {
          id: 'VAC-2024-001',
          veteran_name: 'Smith, John A.',
          status: 'completed',
          disability_rating: 65,
          conditions: ['PTSD', 'Lower Back Pain', 'Tinnitus'],
          assigned_adjudicator: user.name,
          created_date: '2024-01-10T09:00:00Z',
          updated_date: '2024-01-15T14:30:00Z',
          priority: 'normal',
          documents_count: 8,
          assessment_progress: 100
        },
        {
          id: 'VAC-2024-002',
          veteran_name: 'Johnson, Mary K.',
          status: 'in-progress',
          conditions: ['Anxiety Disorder', 'Hearing Loss'],
          assigned_adjudicator: user.name,
          created_date: '2024-01-12T10:15:00Z',
          updated_date: '2024-01-15T11:45:00Z',
          priority: 'high',
          documents_count: 5,
          assessment_progress: 75
        },
        {
          id: 'VAC-2024-003',
          veteran_name: 'Williams, Robert L.',
          status: 'pending',
          conditions: ['Shoulder Injury', 'Sleep Disorder'],
          assigned_adjudicator: user.name,
          created_date: '2024-01-14T13:20:00Z',
          updated_date: '2024-01-14T13:20:00Z',
          priority: 'urgent',
          documents_count: 12,
          assessment_progress: 25
        },
        {
          id: 'VAC-2024-004',
          veteran_name: 'Brown, Susan M.',
          status: 'review',
          disability_rating: 45,
          conditions: ['Depression', 'Knee Injury'],
          assigned_adjudicator: user.name,
          created_date: '2024-01-08T16:00:00Z',
          updated_date: '2024-01-14T09:15:00Z',
          priority: 'normal',
          documents_count: 7,
          assessment_progress: 100
        },
        {
          id: 'VAC-2024-005',
          veteran_name: 'Davis, Michael R.',
          status: 'pending',
          conditions: ['Traumatic Brain Injury'],
          assigned_adjudicator: user.name,
          created_date: '2024-01-15T08:30:00Z',
          updated_date: '2024-01-15T08:30:00Z',
          priority: 'urgent',
          documents_count: 15,
          assessment_progress: 0
        }
      ]
      
      setCases(mockCases)
    } catch (error) {
      console.error('Failed to load cases:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterAndSortCases = () => {
    let filtered = cases.filter((case_item) => {
      const matchesSearch = 
        case_item.veteran_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        case_item.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        case_item.conditions.some(condition => 
          condition.toLowerCase().includes(searchQuery.toLowerCase())
        )
      
      const matchesStatus = statusFilter === 'all' || case_item.status === statusFilter
      const matchesPriority = priorityFilter === 'all' || case_item.priority === priorityFilter
      
      return matchesSearch && matchesStatus && matchesPriority
    })

    // Sort cases
    filtered.sort((a, b) => {
      let aValue: any, bValue: any
      
      switch (sortBy) {
        case 'priority':
          const priorityOrder = { urgent: 4, high: 3, normal: 2, low: 1 }
          aValue = priorityOrder[a.priority]
          bValue = priorityOrder[b.priority]
          break
        case 'rating':
          aValue = a.disability_rating || 0
          bValue = b.disability_rating || 0
          break
        default: // date
          aValue = new Date(a.updated_date).getTime()
          bValue = new Date(b.updated_date).getTime()
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    setFilteredCases(filtered)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-600" />
      case 'in-progress':
        return <ClockIcon className="w-5 h-5 text-blue-600" />
      case 'review':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600" />
      default:
        return <ClockIcon className="w-5 h-5 text-vac-gray-400" />
    }
  }

  const getPriorityBadge = (priority: string) => {
    const classes = {
      urgent: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      normal: 'bg-vac-gray-100 text-vac-gray-800',
      low: 'bg-blue-100 text-blue-800'
    }
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${classes[priority as keyof typeof classes]}`}>
        {priority}
      </span>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-CA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const openCaseInChat = (caseItem: Case) => {
    setCurrentCase({
      id: caseItem.id,
      veteran_name: caseItem.veteran_name
    })
    // Navigate to chat with case context - in real app would use router.push
    window.location.href = `/chat?case_id=${caseItem.id}`
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
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <UserGroupIcon className="w-8 h-8 text-vac-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-vac-gray-900">Case Management</h1>
              <p className="text-sm text-vac-gray-600">
                Manage veteran disability assessment cases assigned to you
              </p>
            </div>
          </div>
          
          <button className="vac-button-primary flex items-center space-x-2">
            <PlusIcon className="w-4 h-4" />
            <span>New Case</span>
          </button>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-lg shadow-sm border border-vac-gray-200 p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-3 h-4 w-4 text-vac-gray-400" />
                <input
                  type="text"
                  placeholder="Search by veteran name, case ID, or condition..."
                  className="vac-input pl-9"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <select
                className="vac-input"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="review">Under Review</option>
              </select>
            </div>

            {/* Priority Filter */}
            <div>
              <select
                className="vac-input"
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
              >
                <option value="all">All Priorities</option>
                <option value="urgent">Urgent</option>
                <option value="high">High</option>
                <option value="normal">Normal</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>

          {/* Sort Options */}
          <div className="mt-4 flex items-center space-x-4">
            <span className="text-sm font-medium text-vac-gray-700">Sort by:</span>
            <div className="flex items-center space-x-2">
              <select
                className="text-sm border-vac-gray-300 rounded-md"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
              >
                <option value="date">Last Updated</option>
                <option value="priority">Priority</option>
                <option value="rating">Disability Rating</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="text-sm text-vac-blue-600 hover:text-vac-blue-700"
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>
          </div>
        </div>

        {/* Cases Table */}
        <div className="bg-white rounded-lg shadow-sm border border-vac-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-vac-gray-200">
            <h2 className="text-lg font-semibold text-vac-gray-900">
              Cases ({filteredCases.length})
            </h2>
          </div>

          {filteredCases.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-vac-gray-200">
                <thead className="bg-vac-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-vac-gray-500 uppercase tracking-wider">
                      Case / Veteran
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-vac-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-vac-gray-500 uppercase tracking-wider">
                      Conditions
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-vac-gray-500 uppercase tracking-wider">
                      Progress
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-vac-gray-500 uppercase tracking-wider">
                      Rating
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-vac-gray-500 uppercase tracking-wider">
                      Updated
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-vac-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-vac-gray-200">
                  {filteredCases.map((case_item) => (
                    <tr key={case_item.id} className="hover:bg-vac-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="flex items-center space-x-2">
                            <div className="text-sm font-medium text-vac-gray-900">
                              {case_item.id}
                            </div>
                            {getPriorityBadge(case_item.priority)}
                          </div>
                          <div className="text-sm text-vac-gray-600">
                            {case_item.veteran_name}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(case_item.status)}
                          <span className={`text-sm assessment-status-${case_item.status.replace('-', '-')}`}>
                            {case_item.status.replace('-', ' ')}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {case_item.conditions.slice(0, 2).map((condition, idx) => (
                            <span
                              key={idx}
                              className="inline-block px-2 py-1 text-xs bg-vac-blue-100 text-vac-blue-800 rounded-full"
                            >
                              {condition}
                            </span>
                          ))}
                          {case_item.conditions.length > 2 && (
                            <span className="inline-block px-2 py-1 text-xs bg-vac-gray-100 text-vac-gray-600 rounded-full">
                              +{case_item.conditions.length - 2}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <div className="w-16 bg-vac-gray-200 rounded-full h-2">
                            <div
                              className="bg-vac-blue-600 h-2 rounded-full"
                              style={{ width: `${case_item.assessment_progress}%` }}
                            />
                          </div>
                          <span className="text-xs text-vac-gray-600">
                            {case_item.assessment_progress}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {case_item.disability_rating ? (
                          <span className={`text-sm font-semibold ${api.getDisabilityRatingClass(case_item.disability_rating)}`}>
                            {api.formatDisabilityRating(case_item.disability_rating)}
                          </span>
                        ) : (
                          <span className="text-sm text-vac-gray-400">Pending</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-vac-gray-500">
                        {formatDate(case_item.updated_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => openCaseInChat(case_item)}
                            className="text-vac-blue-600 hover:text-vac-blue-700 p-1 rounded"
                            title="Open in chat"
                          >
                            <ChatBubbleLeftRightIcon className="w-4 h-4" />
                          </button>
                          <Link
                            href={`/cases/${case_item.id}/documents`}
                            className="text-vac-gray-600 hover:text-vac-gray-700 p-1 rounded"
                            title="View documents"
                          >
                            <DocumentTextIcon className="w-4 h-4" />
                          </Link>
                          <Link
                            href={`/cases/${case_item.id}`}
                            className="text-vac-gray-600 hover:text-vac-gray-700 p-1 rounded"
                            title="View details"
                          >
                            <EyeIcon className="w-4 h-4" />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <UserGroupIcon className="w-16 h-16 text-vac-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-vac-gray-900 mb-2">No Cases Found</h3>
              <p className="text-vac-gray-600 mb-4">
                {searchQuery || statusFilter !== 'all' || priorityFilter !== 'all'
                  ? 'No cases match your current filters.'
                  : 'You have no cases assigned yet.'
                }
              </p>
              {(searchQuery || statusFilter !== 'all' || priorityFilter !== 'all') && (
                <button
                  onClick={() => {
                    setSearchQuery('')
                    setStatusFilter('all')
                    setPriorityFilter('all')
                  }}
                  className="vac-button-secondary"
                >
                  Clear Filters
                </button>
              )}
            </div>
          )}
        </div>

        {/* Summary Stats */}
        {filteredCases.length > 0 && (
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg border border-vac-gray-200">
              <div className="text-2xl font-bold text-vac-blue-600">
                {filteredCases.filter(c => c.status === 'pending').length}
              </div>
              <div className="text-sm text-vac-gray-600">Pending Review</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-vac-gray-200">
              <div className="text-2xl font-bold text-blue-600">
                {filteredCases.filter(c => c.status === 'in-progress').length}
              </div>
              <div className="text-sm text-vac-gray-600">In Progress</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-vac-gray-200">
              <div className="text-2xl font-bold text-green-600">
                {filteredCases.filter(c => c.status === 'completed').length}
              </div>
              <div className="text-sm text-vac-gray-600">Completed</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-vac-gray-200">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(filteredCases.reduce((sum, c) => sum + (c.disability_rating || 0), 0) / filteredCases.filter(c => c.disability_rating).length) || 0}%
              </div>
              <div className="text-sm text-vac-gray-600">Avg. Rating</div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}