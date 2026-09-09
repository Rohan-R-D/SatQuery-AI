import React from 'react';
import { AgentStep } from '../../types/analysis';
import { Circle, Loader2, CheckCircle2, XCircle } from 'lucide-react';

interface AgentStepItemProps {
  step: AgentStep;
  isLast?: boolean;
}

export const AgentStepItem: React.FC<AgentStepItemProps> = ({ step, isLast = false }) => {
  const getStatusBadge = () => {
    switch (step.status) {
      case 'RUNNING':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-satellite-cyan/10 text-satellite-cyan border border-satellite-cyan/30">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>RUNNING</span>
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950/50 text-emerald-400 border border-emerald-800/40">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>COMPLETED</span>
          </span>
        );
      case 'FAILED':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-red-950/50 text-red-400 border border-red-800/40">
            <XCircle className="w-3 h-3 text-red-400" />
            <span>FAILED</span>
          </span>
        );
      case 'PENDING':
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono text-slate-400 bg-space-900 border border-space-700">
            PENDING
          </span>
        );
    }
  };

  const getStepIcon = () => {
    switch (step.status) {
      case 'RUNNING':
        return <Loader2 className="w-4 h-4 text-satellite-cyan animate-spin" />;
      case 'COMPLETED':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'FAILED':
        return <XCircle className="w-4 h-4 text-red-400" />;
      case 'PENDING':
      default:
        return <Circle className="w-3.5 h-3.5 text-slate-600" />;
    }
  };

  return (
    <div className="relative flex items-start space-x-3 group">
      {/* Timeline Vertical Line Connector */}
      {!isLast && (
        <span
          className={`absolute left-3.5 top-6 bottom-0 w-0.5 -ml-px ${
            step.status === 'COMPLETED' ? 'bg-emerald-500/40' : 'bg-space-700'
          }`}
          aria-hidden="true"
        />
      )}

      {/* Step Icon Node */}
      <div
        className={`relative z-10 w-7 h-7 rounded-full flex items-center justify-center border transition-all ${
          step.status === 'RUNNING'
            ? 'bg-space-900 border-satellite-cyan ring-4 ring-satellite-cyan/20'
            : step.status === 'COMPLETED'
            ? 'bg-space-900 border-emerald-500'
            : step.status === 'FAILED'
            ? 'bg-space-900 border-red-500'
            : 'bg-space-900 border-space-700'
        }`}
      >
        {getStepIcon()}
      </div>

      {/* Step Text & Info */}
      <div className="flex-1 min-w-0 pb-4">
        <div className="flex items-center justify-between space-x-2">
          <span className="text-xs font-semibold text-slate-200 group-hover:text-white transition-colors">
            {step.id}. {step.title}
          </span>
          {getStatusBadge()}
        </div>
        {step.description && (
          <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed font-sans">
            {step.description}
          </p>
        )}
      </div>
    </div>
  );
};
