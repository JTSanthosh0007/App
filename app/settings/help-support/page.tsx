'use client';

import { useRouter } from 'next/navigation';

export default function HelpSupportPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-black flex flex-col items-center py-8">
      <div className="w-full max-w-sm bg-zinc-900 rounded-xl shadow-lg p-6 mt-4">
        <button onClick={() => router.back()} className="mb-4 text-white flex items-center gap-2 hover:text-blue-400">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="font-semibold">Help & Support</span>
        </button>
        <h1 className="text-xl font-bold text-white mb-4">Help & Support</h1>
        <div className="mb-4">
          <div className="text-zinc-200 text-base mb-2">For assistance, contact us:</div>
          <div className="text-zinc-100 text-base flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h2l.4 2M7 13h10l4-8H5.4M7 13l-1.35 2.7a1 1 0 00.9 1.45h12.2a1 1 0 00.9-1.45L17 13M7 13V6a1 1 0 011-1h5a1 1 0 011 1v7" />
            </svg>
            <a href="tel:+919876543210" className="hover:underline text-zinc-100">+91 98765 43210</a>
          </div>
          <div className="text-zinc-100 text-base flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12H8m8 0a4 4 0 11-8 0 4 4 0 018 0zm0 0v1a4 4 0 01-4 4H8a4 4 0 01-4-4v-1" />
            </svg>
            <a href="mailto:support@example.com" className="hover:underline text-zinc-100">support@example.com</a>
          </div>
        </div>
      </div>
    </div>
  );
} 