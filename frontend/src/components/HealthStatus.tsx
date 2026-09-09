import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';

interface HealthData {
  status: string;
  service: string;
}

export const HealthStatus: React.FC = () => {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/health');
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data: HealthData = await response.json();
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reach backend service');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="bg-space-800 border border-space-700 rounded-2xl p-6 shadow-xl max-w-xl mx-auto my-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-satellite-cyan" />
          <h2 className="text-lg font-semibold text-white">Backend API Connectivity</h2>
        </div>
        <button
          onClick={fetchHealth}
          disabled={loading}
          className="p-2 rounded-lg bg-space-700 hover:bg-space-600 text-slate-300 transition-colors disabled:opacity-50"
          title="Refresh connection status"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading ? (
        <div className="py-6 text-center text-slate-400 font-mono text-sm">
          Checking backend health status...
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/50 text-red-300">
          <div className="flex items-center space-x-2 mb-2 font-medium">
            <XCircle className="w-5 h-5 text-red-400" />
            <span>Backend Offline or Unreachable</span>
          </div>
          <p className="text-xs text-red-400 font-mono">{error}</p>
          <p className="text-xs text-slate-400 mt-2">
            Ensure FastAPI server is running via <code className="bg-space-900 px-1.5 py-0.5 rounded text-slate-200">uvicorn app.main:app --reload</code> on port 8000.
          </p>
        </div>
      ) : health ? (
        <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/40 text-emerald-300">
          <div className="flex items-center space-x-2 mb-2 font-semibold">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span>{health.service}</span>
          </div>
          <div className="text-xs font-mono bg-space-900/80 p-3 rounded-lg border border-space-700 text-slate-300">
            <span className="text-slate-500">GET /api/health:</span> {JSON.stringify(health, null, 2)}
          </div>
        </div>
      ) : null}
    </div>
  );
};
