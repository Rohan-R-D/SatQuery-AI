import React from 'react';
import { Satellite, Sparkles } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="border-b border-space-700 bg-space-800/60 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-satellite-cyan to-satellite-indigo text-space-900 shadow-lg shadow-satellite-cyan/20">
            <Satellite className="h-6 w-6 font-bold" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-satellite-cyan bg-clip-text text-transparent">
              SatQuery AI
            </h1>
            <p className="text-xs text-slate-400 font-medium">Smart India Hackathon 2026</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-satellite-cyan/10 text-satellite-cyan border border-satellite-cyan/20">
            <Sparkles className="w-3.5 h-3.5" />
            Phase 1: Architecture Setup
          </span>
        </div>
      </div>
    </header>
  );
};
