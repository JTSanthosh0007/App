'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { CloudArrowUpIcon, DocumentTextIcon, XMarkIcon } from '@heroicons/react/24/outline'

type Platform = 'paytm' | 'phonepe' | 'supermoney'

type Transaction = {
  date: string
  amount: number
  description: string
  category: string
}

type AnalysisData = {
  transactions: Transaction[]
  totalSpent: number
  totalReceived: number
  categoryBreakdown: Record<string, number>
}

interface StatementUploadProps {
  onAnalysisComplete: (data: AnalysisData) => void
}

export default function StatementUpload({ onAnalysisComplete }: StatementUploadProps) {
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>('paytm')
  const [file, setFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setError(null)
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/csv': ['.csv']
    },
    maxFiles: 1
  })

  const handleSubmit = async () => {
    if (!file) return
    setIsLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('platform', selectedPlatform)

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
        mode: 'cors'
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.error || 'Failed to analyze statement')
      }
      
      const data = await response.json()
      if (data.error) {
        throw new Error(data.error)
      }
      
      onAnalysisComplete(data)
      
    } catch (error) {
      console.error('Error uploading file:', error)
      setError(error instanceof Error ? error.message : 'Failed to analyze statement')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
      <div className="mx-auto max-w-3xl">
        {/* Platform Selection */}
        <div className="mb-8">
          <label className="text-base font-semibold text-gray-900">Select Platform</label>
          <div className="mt-4 grid grid-cols-3 gap-3">
            {(['paytm', 'phonepe', 'supermoney'] as const).map((platform) => (
              <button
                key={platform}
                type="button"
                className={`
                  ${selectedPlatform === platform
                    ? 'border-primary ring-2 ring-primary'
                    : 'border-gray-200'
                  }
                  relative flex items-center justify-center rounded-lg border p-4 text-sm font-semibold uppercase hover:bg-gray-50 focus:outline-none
                `}
                onClick={() => setSelectedPlatform(platform)}
              >
                {platform}
              </button>
            ))}
          </div>
        </div>

        {/* File Upload Area */}
        <div className="mt-8">
          <div
            {...getRootProps()}
            className={`
              relative block w-full rounded-lg border-2 border-dashed p-12 text-center hover:border-gray-400 focus:outline-none
              ${isDragActive ? 'border-primary' : 'border-gray-300'}
              ${file ? 'bg-gray-50' : 'bg-white'}
            `}
          >
            <input {...getInputProps()} />
            {file ? (
              <div className="space-y-4">
                <DocumentTextIcon className="mx-auto h-12 w-12 text-primary" />
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-sm font-medium text-gray-900">{file.name}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      setFile(null)
                    }}
                    className="rounded-full p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                <div className="space-y-1">
                  <p className="text-sm font-medium text-gray-900">
                    Drop your statement here, or <span className="text-primary">browse</span>
                  </p>
                  <p className="text-xs text-gray-500">PDF or CSV files only</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 rounded-md bg-red-50">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <div className="mt-8">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!file || isLoading}
            className={`
              w-full rounded-md px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
              ${!file || isLoading
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-primary hover:bg-primary/90 focus-visible:outline-primary'
              }
            `}
          >
            {isLoading ? 'Analyzing...' : 'Analyze Statement'}
          </button>
        </div>
      </div>
    </div>
  )
} 