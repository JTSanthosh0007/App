'use client';

import { useState } from 'react';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { useRouter } from 'next/navigation';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function KotakPage() {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await handleFile(files[0]);
    }
  };

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await handleFile(files[0]);
    }
  };

  const handleFile = async (file: File) => {
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    setFile(file);
    setError('');
    setIsLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/analyze-statement', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze statement');
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError('Failed to analyze statement. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="p-4 flex items-center gap-3">
        <button 
          onClick={() => router.push('/')}
          className="hover:text-zinc-300 transition-colors"
        >
          <ArrowLeftIcon className="w-6 h-6" />
        </button>
        <h1 className="text-lg font-medium">Kotak Bank Statement Analysis</h1>
      </div>

      {/* Upload Section */}
      <div className="p-4">
        <div 
          className={`border-2 border-dashed rounded-2xl p-8 text-center ${
            isDragging ? 'border-blue-500 bg-blue-500/10' : 'border-zinc-700 hover:border-zinc-600'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="max-w-sm mx-auto">
            <h2 className="font-medium mb-2">Upload Statement</h2>
            <p className="text-sm text-zinc-400 mb-4">
              Drag and drop your Kotak Bank statement PDF here, or click to select file
            </p>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileInput}
              className="hidden"
              id="file-input"
            />
            <label
              htmlFor="file-input"
              className="inline-block bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-zinc-200 transition-colors cursor-pointer"
            >
              Select File
            </label>
            {file && (
              <p className="mt-2 text-sm text-zinc-400">
                Selected: {file.name}
              </p>
            )}
            {error && (
              <p className="mt-2 text-sm text-red-500">
                {error}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="p-4 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-white"></div>
          <p className="mt-2 text-sm text-zinc-400">Analyzing your statement...</p>
        </div>
      )}

      {/* Results */}
      {data && (
        <div className="p-4 space-y-6">
          {/* Summary */}
          <div className="bg-zinc-900/80 rounded-2xl p-4 border border-zinc-800/50">
            <h2 className="font-medium mb-3">Summary</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-zinc-400">Total Received</p>
                <p className="text-lg font-medium text-green-500">₹{data.summary.totalReceived.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-zinc-400">Total Spent</p>
                <p className="text-lg font-medium text-red-500">₹{data.summary.totalSpent.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-zinc-400">Balance</p>
                <p className={`text-lg font-medium ${data.summary.balance >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ₹{data.summary.balance.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-zinc-400">Total Transactions</p>
                <p className="text-lg font-medium">{data.summary.totalTransactions}</p>
              </div>
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="bg-zinc-900/80 rounded-2xl p-4 border border-zinc-800/50">
            <h2 className="font-medium mb-3">Category Breakdown</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                {Object.entries(data.categoryBreakdown).map(([category, info]: [string, any]) => (
                  <div key={category} className="flex justify-between items-center">
                    <span className="text-sm">{category}</span>
                    <span className="text-sm text-zinc-400">₹{info.amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
              <div className="h-64">
                {data.chartData && (
                  <Pie 
                    data={data.chartData.data}
                    options={{
                      plugins: {
                        legend: {
                          position: 'bottom',
                          labels: {
                            color: 'white'
                          }
                        }
                      }
                    }}
                  />
                )}
              </div>
            </div>
          </div>

          {/* Transactions */}
          <div className="bg-zinc-900/80 rounded-2xl p-4 border border-zinc-800/50">
            <h2 className="font-medium mb-3">Recent Transactions</h2>
            <div className="space-y-2">
              {data.transactions.slice(0, 10).map((transaction: any, index: number) => (
                <div 
                  key={index}
                  className="flex justify-between items-center py-2 border-b border-zinc-800/50 last:border-0"
                >
                  <div>
                    <p className="text-sm">{transaction.description}</p>
                    <p className="text-xs text-zinc-400">{transaction.date}</p>
                  </div>
                  <p className={`text-sm ${transaction.amount >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    ₹{Math.abs(transaction.amount).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 