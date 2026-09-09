import React from 'react';
import { AgentStep } from '../../types/analysis';
import { AgentStepItem } from '../AgentStep/AgentStepItem';
import { Cpu } from 'lucide-react';

interface AgentExecutionProps {
  steps: AgentStep[];
}

export const AgentExecution: React.FC<AgentExecutionProps> = ({ steps }) => {
  return (
    <div className="bg-space-800 border border-space-700 rounded-2xl p-5 shadow-xl flex flex-col space-y-4">
      <div className="border-b border-space-700 pb-3 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-satellite-cyan" />
          <h2 className="text-sm font-bold uppercase tracking-wider text-white">
            AGENT EXECUTION
          </h2>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-space-900 text-satellite-cyan border border-space-700">
          ORCHESTRATOR
        </span>
      </div>

      <p className="text-xs text-slate-400">
        Autonomous agent decision trace and tool execution workflow.
      </p>

      {/* 8-Step Timeline */}
      <div className="pt-2 space-y-1">
        {steps.map((step, index) => (
          <AgentStepItem
            key={step.id}
            step={step}
            isLast={index === steps.length - 1}
          />
        ))}
      </div>
    </div>
  );
};
