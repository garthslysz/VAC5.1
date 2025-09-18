import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Veterans Affairs Canada AI Assessments',
  description: 'AI-powered disability assessment using Canada Table of Disabilities 2019',
  keywords: ['VAC', 'Veterans Affairs Canada', 'AI Assessment', 'Table of Disabilities', 'Disability Rating'],
  authors: [{ name: 'VAC AI Assessment Team' }],
  robots: 'noindex, nofollow', // Private government system
  icons: {
    icon: '/favicon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-vac-gray-50`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}