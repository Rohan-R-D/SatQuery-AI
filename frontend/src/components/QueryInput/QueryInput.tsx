import React from 'react';
import { HelpCircle, MessageSquare } from 'lucide-react';

interface QueryInputProps {
  query: string;
  onChange: (query: string) => void;
}

export const QueryInput: React.FC<QueryInputProps> = ({ query, onChange }) => {
  const exampleQueries = [
    "Is there a water body in this image?",
    "What changed between these two dates?",
    "Has the built-up area increased?",
    "Use both images to identify built-up and water-covered regions.",
  ];

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
          Natural Language Query
        </label>
        <span className="text-[10px] text-slate-400 font-mono">Multimodal VLM Prompt</span>
      </div>

      <div className="relative">
        <textarea
          rows={3}
          value={query}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Ask a question about the satellite imagery..."
          className="w-full bg-space-900 border border-space-700 rounded-xl p-3 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-satellite-cyan focus:ring-1 focus:ring-satellite-cyan transition-colors resize-none"
        />
        <MessageSquare className="w-4 h-4 text-slate-400 absolute right-3 bottom-3 pointer-events-none" />
      </div>

      {/* Example Queries */}
      <div className="space-y-1.5">
        <div className="flex items-center space-x-1 text-[11px] text-slate-400 font-medium">
          <HelpCircle className="w-3 h-3 text-satellite-cyan" />
          <span>Example Queries:</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {exampleQueries.map((ex, index) => (
            <button
              key={index}
              type="button"
              onClick={() => onChange(ex)}
              className="text-[11px] px-2.5 py-1 rounded-lg bg-space-900 border border-space-700 text-slate-300 hover:text-white hover:border-satellite-cyan/50 hover:bg-space-800 transition-all text-left"
            >
              &quot;{ex}&quot;
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
