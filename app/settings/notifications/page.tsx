'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function NotificationsPage() {
  const router = useRouter();
  const [isNotificationsEnabled, setIsNotificationsEnabled] = useState(true);

  const toggleNotifications = () => {
    // This is a visual toggle. Actual notification control would need backend implementation.
    setIsNotificationsEnabled(!isNotificationsEnabled);
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center py-8">
      <div className="w-full max-w-sm bg-zinc-900 rounded-xl shadow-lg p-6 mt-4">
        <button onClick={() => router.back()} className="mb-4 text-white flex items-center gap-2 hover:text-blue-400">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="font-semibold">Notifications</span>
        </button>
        
        <div className="flex items-center justify-between mb-6">
          <p className="text-zinc-200 text-base">Notifications Status:</p>
          <button 
            onClick={toggleNotifications}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isNotificationsEnabled 
                ? 'bg-green-600 hover:bg-green-700 text-white' 
                : 'bg-red-600 hover:bg-red-700 text-white'
            }`}
          >
            {isNotificationsEnabled ? 'ON' : 'OFF'}
          </button>
        </div>

        <p className="text-zinc-400 text-sm italic text-center">
          Note: Notification settings are currently managed by the system. This toggle is for demonstration.
        </p>

      </div>
    </div>
  );
} 