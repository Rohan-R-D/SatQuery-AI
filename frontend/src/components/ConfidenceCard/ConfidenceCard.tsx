import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert } from 'lucide-react';

interface ConfidenceCardProps {
  score: number; // 0 - 100
  rating: 'High' | 'Medium' | 'Low';
}

export const ConfidenceCard: React.FC<ConfidenceCardProps> = ({ score, rating }) => {
  const getBadgeStyle = () => {
    switch (rating) {
      case 'High':
        return {
          bg: 'bg-emerald-950/40 border-emerald-800/50 text-emerald-400',
          bar: 'bg-emerald-500',
          icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />,
        };
      case 'Medium':
        return {
          bg: 'bg-amber-950/40 border-amber-800/50 text-amber-400',
          bar: 'bg-amber-500',
          icon: <AlertTriangle className="w-5 h-5 text-amber-400" />,
        };
      case 'Low':
      default:
        return {
          bg: 'bg-red-950/40 border-red-800/50 text-red-400',
          bar: 'bg-red-500',
          icon: <ShieldAlert className="w-5 h-5 text-red-400" />,
        };
    }
  };

  const style = getBadgeStyle();

  return (
    <div className={`p-4 rounded-xl border ${style.bg} space-y-2 shadow-lg`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {style.icon}
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            CONFIDENCE SCORE
          </span>
        </div>
        <span className="text-base font-extrabold font-mono">{score}% ({rating})</span>
      </div>

      {/* Visual Progress Meter */}
      <div className="w-full h-2 rounded-full bg-space-900 overflow-hidden border border-space-700">
        <div
          className={`h-full ${style.bar} transition-all duration-500`}
          style={{ width: `${Math.max(0, Math.min(100, score))}%` }}
        />
      </div>

      {/* Prototype Disclaimer Label */}
      <div className="pt-1 text-center">
        <span className="text-[11px] font-mono text-slate-400 italic">
          Prototype confidence — not a calibrated probability.
        </span>
      </div>
    </div>
  );
};
