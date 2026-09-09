import React from 'react';
import { Evidence } from '../../types/analysis';
import { CheckCircle2 } from 'lucide-react';

interface EvidencePanelProps {
  evidence: Evidence[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ evidence }) => {
  if (!evidence || evidence.length === 0) {
    return (
      <div className="text-xs text-slate-400 font-mono py-2">
        No specific visual evidence markers generated for this query.
      </div>
    );
  }

  return (
    <div className="space-y-2 mt-2">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {evidence.map((item) => {
          const descText = item.description.startsWith('✓')
            ? item.description
            : `✓ ${item.description}`;

          return (
            <div
              key={item.id}
              className="bg-space-900 border border-space-700 rounded-xl p-3.5 flex flex-col space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-xs font-semibold text-white">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span className="truncate">{item.title}</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-space-800 text-satellite-cyan border border-space-700 uppercase">
                  {item.type}
                </span>
              </div>

              <p className="text-xs text-slate-300 font-medium leading-relaxed font-sans">
                {descText}
              </p>

              {item.metrics && (
                <div className="mt-1 p-2 rounded-lg bg-space-800/80 border border-space-700/80 grid grid-cols-2 gap-2 text-xs font-mono">
                  {Object.entries(item.metrics).map(([key, val]) => (
                    <div key={key}>
                      <span className="block text-[10px] text-slate-400 font-sans">{key}:</span>
                      <span className="text-satellite-cyan font-bold">{String(val)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
