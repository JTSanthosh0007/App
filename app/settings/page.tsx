'use client';

import { useRouter } from 'next/navigation';

export default function SettingsPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-black flex flex-col items-center py-8">
      <div className="w-full max-w-md bg-zinc-900 rounded-xl shadow-lg p-6 mt-4">
        <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>
        <div className="flex items-center gap-4 mb-6">
          <div className="w-12 h-12 rounded-full bg-zinc-800 flex items-center justify-center text-white text-xl font-bold">U</div>
          <div>
            <div className="text-white font-semibold">User</div>
            <div className="text-zinc-400 text-sm">No email set</div>
          </div>
        </div>
        <div className="space-y-3">
          <button className="w-full bg-zinc-800 text-white text-left px-4 py-3 rounded-lg font-medium hover:bg-zinc-700 transition" onClick={() => router.push('/settings/account')}>Account Settings</button>
          <button className="w-full bg-zinc-800 text-white text-left px-4 py-3 rounded-lg font-medium hover:bg-zinc-700 transition" onClick={() => router.push('/settings/notifications')}>Notifications</button>
          <button className="w-full bg-zinc-800 text-white text-left px-4 py-3 rounded-lg font-medium hover:bg-zinc-700 transition" onClick={() => router.push('/settings/privacy')}>Privacy</button>
          <button className="w-full bg-zinc-800 text-white text-left px-4 py-3 rounded-lg font-medium hover:bg-zinc-700 transition" onClick={() => router.push('/settings/help-support')}>Help & Support</button>
          <button className="w-full bg-red-600 text-white text-left px-4 py-3 rounded-lg font-medium hover:bg-red-700 transition mt-2">Log Out</button>
        </div>
      </div>
    </div>
  );
} 