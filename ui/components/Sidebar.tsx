'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Fragment } from 'react'
import {
  HomeIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  FolderIcon,
  BookOpenIcon,
  ChartBarIcon,
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'
import { useApp } from '../app/providers'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Assessment Chat', href: '/chat', icon: ChatBubbleLeftRightIcon },
  { name: 'Upload Documents', href: '/upload', icon: DocumentTextIcon },
  { name: 'Case Management', href: '/cases', icon: FolderIcon },
  { name: 'VAC ToD Browser', href: '/tod', icon: BookOpenIcon },
  { name: 'Reports', href: '/reports', icon: ChartBarIcon },
]

const secondaryNavigation = [
  { name: 'Profile', href: '/profile', icon: UserIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, currentCase } = useApp()

  return (
    <div className="flex flex-col h-full bg-white shadow-sm border-r border-vac-gray-200">
      {/* Logo and Header */}
      <div className="flex items-center justify-center h-16 px-6 bg-vac-blue-600">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center mr-3">
            <span className="text-vac-blue-600 font-bold text-sm">VAC</span>
          </div>
          <h1 className="text-white font-semibold text-lg">Assessment System</h1>
        </div>
      </div>

      {/* User Info */}
      <div className="px-6 py-4 border-b border-vac-gray-200">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-vac-blue-100 rounded-full flex items-center justify-center">
            <span className="text-vac-blue-600 font-medium text-sm">
              {user.name.split(' ').map((n: string) => n[0]).join('')}
            </span>
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-vac-gray-900">{user.name}</p>
            <p className="text-xs text-vac-gray-500">{user.role}</p>
          </div>
        </div>
      </div>

      {/* Current Case Info */}
      {currentCase && (
        <div className="px-6 py-3 bg-yellow-50 border-b border-yellow-200">
          <div className="text-xs text-yellow-800 font-medium">Active Case</div>
          <div className="text-sm text-yellow-900">{currentCase.id}</div>
          <div className="text-xs text-yellow-700">
            {currentCase.veteran_name || 'Unnamed Case'}
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`vac-nav-item ${
                isActive ? 'vac-nav-item-active' : 'vac-nav-item-inactive'
              }`}
            >
              <item.icon className="w-5 h-5 mr-3" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Secondary Navigation */}
      <div className="px-4 py-4 border-t border-vac-gray-200">
        <div className="space-y-1">
          {secondaryNavigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`vac-nav-item ${
                  isActive ? 'vac-nav-item-active' : 'vac-nav-item-inactive'
                }`}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            )
          })}
          <button
            className="vac-nav-item vac-nav-item-inactive w-full text-left"
            onClick={() => {
              // Handle logout
              console.log('Logout clicked')
            }}
          >
            <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
            Sign Out
          </button>
        </div>
      </div>

      {/* Version info */}
      <div className="px-4 py-2 text-xs text-vac-gray-500 border-t border-vac-gray-200">
        VAC Assessment System v1.0.0
        <br />
        Table of Disabilities 2019
      </div>
    </div>
  )
}

export function MobileMenuButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      className="inline-flex items-center justify-center p-2 rounded-md text-vac-gray-700 hover:text-vac-gray-900 hover:bg-vac-gray-100 focus:outline-none focus:ring-2 focus:ring-vac-blue-500"
      onClick={onClick}
    >
      <span className="sr-only">Open main menu</span>
      <svg
        className="w-6 h-6"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth="1.5"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
        />
      </svg>
    </button>
  )
}