import React from 'react';
import { Layers } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  subtitle,
  icon = <Layers className="w-10 h-10 text-slate-600" />,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center h-full min-h-[240px] space-y-3">
      <div className="p-4 rounded-2xl bg-space-900 border border-space-700/60 shadow-inner">
        {icon}
      </div>
      <div>
        <h3 className="text-sm font-semibold text-slate-300">{title}</h3>
        {subtitle && <p className="text-xs text-slate-400 mt-1 max-w-sm">{subtitle}</p>}
      </div>
    </div>
  );
};
