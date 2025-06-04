import React, { useState, useEffect } from 'react';
import { Dialog } from '@headlessui/react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { UPIApp, searchApps, getSearchSuggestions } from '../constants/upiApps';
import { useRouter } from 'next/navigation';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectApp: (app: UPIApp) => void;
}

export default function SearchModal({ isOpen, onClose, onSelectApp }: SearchModalProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<UPIApp[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [comingSoon, setComingSoon] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const query = searchQuery.trim();
    if (query) {
      setSearchResults(searchApps(query));
      setSuggestions(getSearchSuggestions(query));
    } else {
      setSearchResults([]);
      setSuggestions([]);
    }
  }, [searchQuery]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const renderAppBadge = (app: UPIApp) => {
    let bgColor = 'bg-gray-100';
    let textColor = 'text-gray-800';

    switch (app.category) {
      case 'payment':
        bgColor = 'bg-blue-100';
        textColor = 'text-blue-800';
        break;
      case 'private':
        bgColor = 'bg-green-100';
        textColor = 'text-green-800';
        break;
      case 'public':
        bgColor = 'bg-purple-100';
        textColor = 'text-purple-800';
        break;
      case 'small-finance':
        bgColor = 'bg-yellow-100';
        textColor = 'text-yellow-800';
        break;
      case 'foreign':
        bgColor = 'bg-red-100';
        textColor = 'text-red-800';
        break;
      case 'regional-rural':
        bgColor = 'bg-indigo-100';
        textColor = 'text-indigo-800';
        break;
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bgColor} ${textColor}`}>
        {app.category.charAt(0).toUpperCase() + app.category.slice(1)}
      </span>
    );
  };

  const handleSelectApp = (app: UPIApp) => {
    // Only allow navigation for PhonePe and Kotak Bank
    if (app.name.toLowerCase() === 'phonepe') {
      onClose();
      router.push('/phonepe');
    } else if (app.name.toLowerCase().includes('kotak')) {
      onClose();
      router.push('/kotak');
    } else {
      setComingSoon('Coming Soon! This feature is under development.');
      setTimeout(() => setComingSoon(null), 2000);
    }
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/70" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="mx-auto max-w-2xl w-full bg-zinc-900 rounded-xl shadow-2xl border border-zinc-800">
          <div className="p-4">
            <div className="flex items-center gap-2 mb-4">
              <div className="relative flex-1">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-zinc-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={handleSearch}
                  placeholder="Search for banks, UPI apps, or payment services..."
                  className="w-full pl-10 pr-4 py-2 bg-zinc-800 text-white border border-zinc-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-zinc-400"
                />
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-zinc-800 rounded-full"
              >
                <XMarkIcon className="h-5 w-5 text-zinc-400" />
              </button>
            </div>

            {/* Search Results */}
            <div className="mt-4 max-h-[60vh] overflow-y-auto">
              {searchResults.length > 0 ? (
                <div className="space-y-2">
                  {searchResults.map((app) => (
                    <div
                      key={app.id}
                      onClick={() => handleSelectApp(app)}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        app.available
                          ? 'hover:bg-zinc-800 active:bg-zinc-700'
                          : 'opacity-60 cursor-not-allowed'
                      } bg-zinc-800 text-white`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium text-white">{app.name}</h3>
                            {renderAppBadge(app)}
                            {!app.available && (
                              <span className="text-xs text-zinc-400">(Coming Soon)</span>
                            )}
                          </div>
                          <p className="text-sm text-zinc-400 mt-1">
                            {app.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : searchQuery ? (
                <div className="text-center py-8">
                  <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-zinc-500" />
                  <p className="mt-2 text-zinc-400">No results found</p>
                  <p className="text-sm text-zinc-600">
                    Try searching for bank names, UPI apps, or payment services
                  </p>
                </div>
              ) : (
                <div className="text-center py-8">
                  <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-zinc-500" />
                  <p className="mt-2 text-zinc-400">
                    Search for any bank or UPI app
                  </p>
                  <p className="text-sm text-zinc-600">
                    Try "SBI", "HDFC", "PhonePe", or "Google Pay"
                  </p>
                </div>
              )}
            </div>

            {/* Search Suggestions */}
            {suggestions.length > 0 && (
              <div className="mt-4 border-t border-zinc-800 pt-4">
                <p className="text-sm text-zinc-500 mb-2">Suggestions</p>
                <div className="flex flex-wrap gap-2">
                  {suggestions.map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => setSearchQuery(suggestion)}
                      className="px-3 py-1 text-sm bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-full"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {comingSoon && (
              <div className="fixed left-1/2 -translate-x-1/2 bottom-8 bg-zinc-800 text-white px-6 py-3 rounded-xl shadow-lg z-50 text-center">
                {comingSoon}
              </div>
            )}
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
} 