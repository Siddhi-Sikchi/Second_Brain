import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, Search, Sparkles, Bell, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface NavbarProps {
  onToggleMobileSidebar: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleMobileSidebar }) => {
  const { user } = useAuth();
  const [quickQuery, setQuickQuery] = useState('');
  const navigate = useNavigate();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (quickQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(quickQuery.trim())}`);
      setQuickQuery('');
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-slate-200 h-16 flex items-center justify-between px-4 sm:px-6">
      {/* Left side: Mobile menu & Quick Search */}
      <div className="flex items-center space-x-4 flex-1 max-w-lg">
        <button
          onClick={onToggleMobileSidebar}
          className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg lg:hidden"
          aria-label="Open Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <form onSubmit={handleSearchSubmit} className="relative w-full hidden sm:block">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search notes, documents, or concepts (press Enter)..."
            value={quickQuery}
            onChange={(e) => setQuickQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all placeholder:text-slate-400"
          />
        </form>
      </div>

      {/* Right side: AI Status, Notifications & Profile */}
      <div className="flex items-center space-x-3">
        <div className="hidden md:flex items-center space-x-1.5 px-3 py-1 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-full text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600 animate-pulse" />
          <span>RAG Engine Active</span>
        </div>

        <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-xs shadow">
            {user?.full_name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <span className="text-sm font-semibold text-slate-700 hidden sm:inline-block">
            {user?.full_name}
          </span>
        </div>
      </div>
    </header>
  );
};
