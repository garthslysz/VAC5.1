'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { VACAssessmentAPI } from '../lib/api'

interface AppContextType {
  api: VACAssessmentAPI
  user: any
  currentCase: any
  setCurrentCase: (caseData: any) => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

export function Providers({ children }: { children: ReactNode }) {
  const [user] = useState({
    id: 'adj001',
    name: 'Sarah Mitchell',
    role: 'Senior Adjudicator',
    region: 'Ontario'
  })
  const [currentCase, setCurrentCase] = useState(null)
  const [api] = useState(() => new VACAssessmentAPI(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'))

  return (
    <AppContext.Provider value={{ api, user, currentCase, setCurrentCase }}>
      {children}
    </AppContext.Provider>
  )
}