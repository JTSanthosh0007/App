'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import SearchModal from './SearchModal';

export default function UPINavBar() {
  const router = useRouter();
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const handleSelectApp = (app) => {
    setIsSearchOpen(false);
  };

  const upiApps = [
    {
      name: 'Home',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
      path: '/'
    },
    {
      name: 'Search',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      ),
      isSearch: true
    },
    {
      name: 'Settings',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      path: '/settings'
    }
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-black border-t border-zinc-800">
      <div className="max-w-screen-xl mx-auto px-4">
        <div className="flex justify-between items-center py-2">
          {upiApps.map((app) => (
            <button
              key={app.name}
              onClick={() => {
                if (app.isSearch) {
                  setIsSearchOpen(true);
                } else if (app.path) {
                  router.push(app.path);
                }
              }}
              className="flex flex-col items-center gap-1 p-2 text-zinc-400 hover:text-white transition-colors"
            >
              {app.icon}
              <span className="text-xs font-medium">{app.name}</span>
            </button>
          ))}
        </div>
      </div>
      <SearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onSelectApp={handleSelectApp}
      />
    </nav>
  );
} 