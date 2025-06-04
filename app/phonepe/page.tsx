'use client'

import { useRouter } from 'next/navigation'
import { PhonePeAnalysisView } from '../components/StatementAnalysis'

export default function PhonePePage() {
  const router = useRouter()
  
  return (
    <div className="min-h-screen bg-black">
      <PhonePeAnalysisView setCurrentView={() => router.push('/')} />
    </div>
  )
} 