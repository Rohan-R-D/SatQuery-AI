import React from 'react';
import { Satellite, ShieldCheck } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="border-b border-space-700 bg-space-800/90 backdrop-blur-md sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand & Tagline */}
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 rounded-xl bg-space-700 border border-space-600 text-satellite-cyan shadow-inner">
            <Satellite className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2.5">
              <h1 className="text-xl font-bold tracking-tight text-white font-sans">
                SATQUERY AI
              </h1>
              <span className="hidden sm:inline-block px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-space-700 text-slate-300 border border-space-600">
                SMART INDIA HACKATHON 2026
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              &quot;Ask Satellite Images. Get Real Answers.&quot;
            </p>
          </div>
        </div>

        {/* System Status Indicator */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-space-900 border border-space-700 text-xs">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-mono text-emerald-400 font-semibold tracking-wide">SYSTEM READY</span>
          </div>
        </div>

      </div>
    </header>
  );
};
