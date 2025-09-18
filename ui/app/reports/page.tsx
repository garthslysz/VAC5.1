'use client'

import { useState, useEffect } from 'react'
import {
  ChartBarIcon,
  DocumentChartBarIcon,
  CalendarDaysIcon,
  UserGroupIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowDownTrayIcon,
  PrinterIcon,
} from '@heroicons/react/24/outline'
import { DashboardLayout } from '../../components/DashboardLayout'
import { useApp } from '../providers'

interface ReportData {
  casesByStatus: { status: string; count: number; percentage: number }[]
  disabilityRatingDistribution: { range: string; count: number }[]
  processingTimes: { period: string; avgDays: number }[]
  conditionFrequency: { condition: string; count: number }[]
  monthlyStats: { month: string; completed: number; avgRating: number }[]
}

export default function Reports() {
  const { user } = useApp()
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState<'month' | 'quarter' | 'year'>('month')
  const [selectedReport, setSelectedReport] = useState<string>('overview')

  useEffect(() => {
    loadReportData()
  }, [selectedPeriod])

  const loadReportData = async () => {
    try {
      setLoading(true)
      
      // Mock report data - in real implementation, this would be API calls
      const mockData: ReportData = {
        casesByStatus: [
          { status: 'Completed', count: 28, percentage: 56 },
          { status: 'In Progress', count: 12, percentage: 24 },
          { status: 'Pending', count: 8, percentage: 16 },
          { status: 'Under Review', count: 2, percentage: 4 },
        ],
        disabilityRatingDistribution: [
          { range: '0-25%', count: 8 },
          { range: '26-50%', count: 15 },
          { range: '51-75%', count: 18 },
          { range: '76-100%', count: 9 },
        ],
        processingTimes: [
          { period: 'This Month', avgDays: 14 },
          { period: 'Last Month', avgDays: 18 },
          { period: 'Last Quarter', avgDays: 21 },
        ],
        conditionFrequency: [
          { condition: 'PTSD', count: 24 },
          { condition: 'Lower Back Pain', count: 18 },
          { condition: 'Hearing Loss', count: 16 },
          { condition: 'Anxiety Disorder', count: 12 },
          { condition: 'Tinnitus', count: 11 },
          { condition: 'Knee Injury', count: 9 },
          { condition: 'Depression', count: 8 },
          { condition: 'Shoulder Injury', count: 7 },
        ],
        monthlyStats: [
          { month: 'Jan 2024', completed: 22, avgRating: 42 },
          { month: 'Feb 2024', completed: 18, avgRating: 38 },
          { month: 'Mar 2024', completed: 25, avgRating: 45 },
          { month: 'Apr 2024', completed: 28, avgRating: 44 },
          { month: 'May 2024', completed: 24, avgRating: 41 },
          { month: 'Jun 2024', completed: 30, avgRating: 47 },
        ]
      }
      
      setReportData(mockData)
    } catch (error) {
      console.error('Failed to load report data:', error)
    } finally {
      setLoading(false)
    }
  }

  const exportReport = () => {
    // In real implementation, this would generate and download a report
    alert('Export functionality would be implemented here')
  }

  const printReport = () => {
    window.print()
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
            <ChartBarIcon className="w-8 h-8 text-vac-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-vac-gray-900">Assessment Reports</h1>
              <p className="text-sm text-vac-gray-600">
                Analytics and reporting for VAC disability assessments
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <select
              className="text-sm border-vac-gray-300 rounded-md"
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value as any)}
            >
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
            </select>
            
            <button onClick={exportReport} className="vac-button-secondary flex items-center space-x-2">
              <ArrowDownTrayIcon className="w-4 h-4" />
              <span>Export</span>
            </button>
            
            <button onClick={printReport} className="vac-button-primary flex items-center space-x-2">
              <PrinterIcon className="w-4 h-4" />
              <span>Print</span>
            </button>
          </div>
        </div>

        {/* Report Tabs */}
        <div className="border-b border-vac-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview', icon: ChartBarIcon },
              { id: 'performance', name: 'Performance', icon: ArrowTrendingUpIcon },
              { id: 'conditions', name: 'Conditions Analysis', icon: DocumentChartBarIcon },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedReport(tab.id)}
                className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedReport === tab.id
                    ? 'border-vac-blue-500 text-vac-blue-600'
                    : 'border-transparent text-vac-gray-500 hover:text-vac-gray-700 hover:border-vac-gray-300'
                }`}
              >
                <tab.icon className="w-5 h-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {reportData && (
          <>
            {/* Overview Tab */}
            {selectedReport === 'overview' && (
              <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="vac-card text-center">
                    <div className="text-3xl font-bold text-vac-blue-600 mb-2">
                      {reportData.casesByStatus.reduce((sum, item) => sum + item.count, 0)}
                    </div>
                    <div className="text-sm text-vac-gray-600">Total Cases</div>
                    <div className="text-xs text-vac-gray-500 mt-1">This {selectedPeriod}</div>
                  </div>
                  
                  <div className="vac-card text-center">
                    <div className="text-3xl font-bold text-green-600 mb-2">
                      {reportData.casesByStatus.find(item => item.status === 'Completed')?.count || 0}
                    </div>
                    <div className="text-sm text-vac-gray-600">Completed</div>
                    <div className="text-xs text-vac-gray-500 mt-1">
                      {reportData.casesByStatus.find(item => item.status === 'Completed')?.percentage || 0}% of total
                    </div>
                  </div>
                  
                  <div className="vac-card text-center">
                    <div className="text-3xl font-bold text-purple-600 mb-2">
                      {Math.round(reportData.monthlyStats.reduce((sum, stat) => sum + stat.avgRating, 0) / reportData.monthlyStats.length)}%
                    </div>
                    <div className="text-sm text-vac-gray-600">Avg. Rating</div>
                    <div className="text-xs text-vac-gray-500 mt-1">Across all assessments</div>
                  </div>
                  
                  <div className="vac-card text-center">
                    <div className="text-3xl font-bold text-orange-600 mb-2">
                      {reportData.processingTimes[0]?.avgDays || 0}
                    </div>
                    <div className="text-sm text-vac-gray-600">Avg. Processing</div>
                    <div className="text-xs text-vac-gray-500 mt-1">Days to complete</div>
                  </div>
                </div>

                {/* Case Status Distribution */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="vac-card">
                    <h3 className="text-lg font-semibold text-vac-gray-900 mb-4">Cases by Status</h3>
                    <div className="space-y-3">
                      {reportData.casesByStatus.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full ${
                              item.status === 'Completed' ? 'bg-green-500' :
                              item.status === 'In Progress' ? 'bg-blue-500' :
                              item.status === 'Pending' ? 'bg-yellow-500' :
                              'bg-red-500'
                            }`} />
                            <span className="text-sm font-medium text-vac-gray-900">{item.status}</span>
                          </div>
                          <div className="flex items-center space-x-3">
                            <span className="text-sm text-vac-gray-600">{item.count}</span>
                            <div className="w-16 bg-vac-gray-200 rounded-full h-2">
                              <div 
                                className="bg-vac-blue-600 h-2 rounded-full" 
                                style={{ width: `${item.percentage}%` }}
                              />
                            </div>
                            <span className="text-sm text-vac-gray-500 w-8">{item.percentage}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="vac-card">
                    <h3 className="text-lg font-semibold text-vac-gray-900 mb-4">Disability Rating Distribution</h3>
                    <div className="space-y-3">
                      {reportData.disabilityRatingDistribution.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between">
                          <span className="text-sm font-medium text-vac-gray-900">{item.range}</span>
                          <div className="flex items-center space-x-3">
                            <span className="text-sm text-vac-gray-600">{item.count} cases</span>
                            <div className="w-16 bg-vac-gray-200 rounded-full h-2">
                              <div 
                                className="bg-purple-600 h-2 rounded-full" 
                                style={{ width: `${(item.count / 50) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Performance Tab */}
            {selectedReport === 'performance' && (
              <div className="space-y-6">
                {/* Processing Times */}
                <div className="vac-card">
                  <h3 className="text-lg font-semibold text-vac-gray-900 mb-4">Processing Times</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {reportData.processingTimes.map((item, idx) => (
                      <div key={idx} className="text-center p-4 bg-vac-gray-50 rounded-lg">
                        <div className="text-2xl font-bold text-vac-blue-600 mb-1">
                          {item.avgDays}
                        </div>
                        <div className="text-sm text-vac-gray-600">days</div>
                        <div className="text-xs text-vac-gray-500 mt-1">{item.period}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Monthly Trends */}
                <div className="vac-card">
                  <h3 className="text-lg font-semibold text-vac-gray-900 mb-4">Monthly Performance</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr className="border-b border-vac-gray-200">
                          <th className="text-left py-2 text-sm font-medium text-vac-gray-700">Month</th>
                          <th className="text-right py-2 text-sm font-medium text-vac-gray-700">Cases Completed</th>
                          <th className="text-right py-2 text-sm font-medium text-vac-gray-700">Avg. Rating</th>
                          <th className="text-right py-2 text-sm font-medium text-vac-gray-700">Trend</th>
                        </tr>
                      </thead>
                      <tbody>
                        {reportData.monthlyStats.map((stat, idx) => (
                          <tr key={idx} className="border-b border-vac-gray-100">
                            <td className="py-3 text-sm text-vac-gray-900">{stat.month}</td>
                            <td className="py-3 text-sm text-vac-gray-600 text-right">{stat.completed}</td>
                            <td className="py-3 text-sm text-vac-gray-600 text-right">{stat.avgRating}%</td>
                            <td className="py-3 text-right">
                              {idx > 0 && (
                                <span className={`text-sm ${
                                  stat.completed > reportData.monthlyStats[idx - 1].completed
                                    ? 'text-green-600'
                                    : stat.completed < reportData.monthlyStats[idx - 1].completed
                                    ? 'text-red-600'
                                    : 'text-vac-gray-500'
                                }`}>
                                  {stat.completed > reportData.monthlyStats[idx - 1].completed ? '↗' :
                                   stat.completed < reportData.monthlyStats[idx - 1].completed ? '↘' : '→'}
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* Conditions Analysis Tab */}
            {selectedReport === 'conditions' && (
              <div className="space-y-6">
                {/* Most Common Conditions */}
                <div className="vac-card">
                  <h3 className="text-lg font-semibold text-vac-gray-900 mb-4">
                    Most Frequently Assessed Conditions
                  </h3>
                  <div className="space-y-3">
                    {reportData.conditionFrequency.map((condition, idx) => (
                      <div key={idx} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="text-sm font-medium text-vac-gray-900 w-4">
                            #{idx + 1}
                          </span>
                          <span className="text-sm text-vac-gray-900">{condition.condition}</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className="text-sm text-vac-gray-600">{condition.count} cases</span>
                          <div className="w-20 bg-vac-gray-200 rounded-full h-2">
                            <div 
                              className="bg-vac-blue-600 h-2 rounded-full" 
                              style={{ width: `${(condition.count / reportData.conditionFrequency[0].count) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Condition Categories */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="vac-card">
                    <h3 className="text-lg font-semibold text-vac-gray-900 mb-4">Mental Health Conditions</h3>
                    <div className="space-y-2">
                      {reportData.conditionFrequency
                        .filter(c => ['PTSD', 'Anxiety Disorder', 'Depression'].includes(c.condition))
                        .map((condition, idx) => (
                          <div key={idx} className="flex justify-between items-center">
                            <span className="text-sm text-vac-gray-900">{condition.condition}</span>
                            <span className="text-sm text-vac-gray-600">{condition.count}</span>
                          </div>
                        ))
                      }
                    </div>
                  </div>

                  <div className="vac-card">
                    <h3 className="text-lg font-semibold text-vac-gray-900 mb-4">Physical Conditions</h3>
                    <div className="space-y-2">
                      {reportData.conditionFrequency
                        .filter(c => !['PTSD', 'Anxiety Disorder', 'Depression'].includes(c.condition))
                        .slice(0, 5)
                        .map((condition, idx) => (
                          <div key={idx} className="flex justify-between items-center">
                            <span className="text-sm text-vac-gray-900">{condition.condition}</span>
                            <span className="text-sm text-vac-gray-600">{condition.count}</span>
                          </div>
                        ))
                      }
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Footer */}
        <div className="mt-8 pt-6 border-t border-vac-gray-200 text-sm text-vac-gray-500">
          <div className="flex items-center justify-between">
            <div>
              Report generated for {user.name} - {user.role}
            </div>
            <div>
              Generated on {new Date().toLocaleDateString('en-CA', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}