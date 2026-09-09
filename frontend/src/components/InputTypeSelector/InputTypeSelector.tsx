import React from 'react';
import { InputType } from '../../types/analysis';
import { Image as ImageIcon, Layers, Compass } from 'lucide-react';

interface InputTypeSelectorProps {
  selectedType: InputType;
  onChange: (type: InputType) => void;
}

export const InputTypeSelector: React.FC<InputTypeSelectorProps> = ({ selectedType, onChange }) => {
  const modes: { type: InputType; label: string; icon: React.ReactNode; desc: string }[] = [
    {
      type: 'single',
      label: 'Single Image',
      icon: <ImageIcon className="w-4 h-4" />,
      desc: 'Scene VQA & Description'
    },
    {
      type: 'bitemporal',
      label: 'Bi-Temporal',
      icon: <Layers className="w-4 h-4" />,
      desc: 'Change Detection (T1 / T2)'
    },
    {
      type: 'optical-sar',
      label: 'Optical + SAR',
      icon: <Compass className="w-4 h-4" />,
      desc: 'Joint Multimodal Fusion'
    },
  ];

  return (
    <div className="space-y-2">
      <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
        Analysis Mode
      </label>
      <div className="grid grid-cols-3 gap-2 p-1 bg-space-900 rounded-xl border border-space-700">
        {modes.map((mode) => {
          const isSelected = selectedType === mode.type;
          return (
            <button
              key={mode.type}
              type="button"
              onClick={() => onChange(mode.type)}
              className={`flex flex-col items-center justify-center p-2.5 rounded-lg text-xs font-medium transition-all ${
                isSelected
                  ? 'bg-satellite-cyan text-space-900 font-bold shadow-md'
                  : 'text-slate-400 hover:text-white hover:bg-space-800'
              }`}
            >
              <div className="flex items-center space-x-1.5 mb-1">
                {mode.icon}
                <span>{mode.label}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
