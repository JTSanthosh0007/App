'use client';

import { useRouter } from 'next/navigation';

export default function AccountSettingsPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-black flex flex-col items-center py-4">
      <div className="w-full max-w-sm bg-zinc-900 rounded-xl shadow-lg p-4 mt-2">
        <button onClick={() => router.back()} className="mb-3 text-white flex items-center gap-2 hover:text-blue-400">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="font-semibold">Account Settings</span>
        </button>
        <div className="flex flex-col items-center mb-4">
          <div className="w-16 h-16 rounded-full bg-zinc-800 flex items-center justify-center text-white text-2xl font-bold mb-1">U</div>
          <button className="text-blue-400 text-xs hover:underline mb-1">Change Profile Picture</button>
        </div>
        <form className="space-y-3">
          <div>
            <label className="block text-zinc-200 mb-1 text-sm">Name</label>
            <input type="text" defaultValue="User" className="w-full bg-zinc-800 text-white px-3 py-2 rounded-lg border-none focus:ring-2 focus:ring-blue-500 text-sm" />
          </div>
          <div>
            <label className="block text-zinc-200 mb-1 text-sm">Email</label>
            <input type="email" placeholder="Enter your email" className="w-full bg-zinc-800 text-white px-3 py-2 rounded-lg border-none focus:ring-2 focus:ring-blue-500 text-sm" />
          </div>
          <div>
            <label className="block text-zinc-200 mb-1 text-sm">Phone Number</label>
            <input type="tel" placeholder="Enter your phone number" className="w-full bg-zinc-800 text-white px-3 py-2 rounded-lg border-none focus:ring-2 focus:ring-blue-500 text-sm" />
          </div>
          <div className="pt-1">
            <div className="text-zinc-200 font-semibold mb-1 text-sm">Additional Settings</div>
            <button type="button" className="w-full flex items-center justify-between bg-zinc-800 text-white px-3 py-2 rounded-lg font-medium hover:bg-zinc-700 transition text-sm">
              Change Password
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
          <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg mt-3 transition text-base">Save Changes</button>
        </form>
      </div>
    </div>
  );
} 