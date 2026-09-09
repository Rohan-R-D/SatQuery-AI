import React from 'react';
import { Header } from './components/Header/Header';
import { Dashboard } from './pages/Dashboard/Dashboard';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-space-900 text-slate-100 font-sans antialiased selection:bg-satellite-cyan selection:text-space-900">
      <Header />
      <main className="flex-1">
        <Dashboard />
      </main>
      <footer className="border-t border-space-700/80 bg-space-800/40 py-6 text-center text-xs text-slate-400 font-mono">
        SatQuery AI &copy; 2026 — Smart India Hackathon Project
      </footer>
    </div>
  );
};

export default App;
