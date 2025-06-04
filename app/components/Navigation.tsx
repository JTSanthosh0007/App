import React from 'react';
import { Star } from 'lucide-react';

interface NavigationProps {
  currentView: string;
  setCurrentView: (view: string) => void;
}

const Navigation: React.FC<NavigationProps> = ({ currentView, setCurrentView }) => {
  return (
    <nav className="flex space-x-4 mb-6">
      <button
        onClick={() => setCurrentView('home')}
        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
          currentView === 'home'
            ? 'bg-white/10 text-white'
            : 'text-gray-400 hover:text-white hover:bg-white/5'
        }`}
      >
        Home
      </button>
      <button
        onClick={() => setCurrentView('favorites')}
        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2 ${
          currentView === 'favorites'
            ? 'bg-white/10 text-white'
            : 'text-gray-400 hover:text-white hover:bg-white/5'
        }`}
      >
        <Star className="w-4 h-4" />
        Favorites
      </button>
    </nav>
  );
};

export default Navigation; 