import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import UPINavBar from './components/UPINavBar'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'Statement Analyzer',
  description: 'Analyze your bank statements and track your spending',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`antialiased ${inter.variable}`} suppressHydrationWarning>
        {children}
        <UPINavBar />
      </body>
    </html>
  )
} 