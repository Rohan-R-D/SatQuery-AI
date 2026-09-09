import React from 'react';
import { InputType, ImageFileMetadata } from '../../types/analysis';
import { InputTypeSelector } from '../InputTypeSelector/InputTypeSelector';
import { ImageUploader } from '../ImageUploader/ImageUploader';
import { QueryInput } from '../QueryInput/QueryInput';
import { DemoBar } from '../DemoBar/DemoBar';
import { Play, Trash2, AlertCircle } from 'lucide-react';

interface InputPanelProps {
  inputType: InputType;
  setInputType: (type: InputType) => void;
  image1: ImageFileMetadata | null;
  setImage1: (img: ImageFileMetadata | null) => void;
  image2: ImageFileMetadata | null;
  setImage2: (img: ImageFileMetadata | null) => void;
  query: string;
  setQuery: (query: string) => void;
  error: string | null;
  onAnalyze: () => void;
  onClear: () => void;
  onLoadDemo: (
    type: InputType,
    img1: ImageFileMetadata,
    img2: ImageFileMetadata | null,
    query: string
  ) => void;
  isAnalyzing: boolean;
}

export const InputPanel: React.FC<InputPanelProps> = ({
  inputType,
  setInputType,
  image1,
  setImage1,
  image2,
  setImage2,
  query,
  setQuery,
  error,
  onAnalyze,
  onClear,
  onLoadDemo,
  isAnalyzing,
}) => {
  return (
    <div className="bg-space-800 border border-space-700 rounded-2xl p-5 shadow-xl flex flex-col space-y-5">
      <div className="border-b border-space-700 pb-3 flex items-center justify-between">
        <h2 className="text-sm font-bold uppercase tracking-wider text-white">
          INPUT IMAGERY & QUERY
        </h2>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-space-900 text-satellite-cyan border border-space-700">
          STEP 1
        </span>
      </div>

      {/* Presentation Demo Bar */}
      <DemoBar onLoadDemo={onLoadDemo} disabled={isAnalyzing} />

      {/* Input Mode Selector */}
      <InputTypeSelector selectedType={inputType} onChange={setInputType} />

      {/* Image Upload Area(s) */}
      <div className="space-y-4">
        {inputType === 'single' && (
          <ImageUploader
            label="Satellite Image"
            image={image1}
            onImageSelect={setImage1}
            onImageRemove={() => setImage1(null)}
          />
        )}

        {inputType === 'bitemporal' && (
          <>
            <ImageUploader
              label="Before / T1 Image"
              image={image1}
              onImageSelect={setImage1}
              onImageRemove={() => setImage1(null)}
            />
            <ImageUploader
              label="After / T2 Image"
              image={image2}
              onImageSelect={setImage2}
              onImageRemove={() => setImage2(null)}
            />
          </>
        )}

        {inputType === 'optical-sar' && (
          <>
            <ImageUploader
              label="Optical Image"
              image={image1}
              onImageSelect={setImage1}
              onImageRemove={() => setImage1(null)}
            />
            <ImageUploader
              label="SAR Image"
              image={image2}
              onImageSelect={setImage2}
              onImageRemove={() => setImage2(null)}
            />
          </>
        )}
      </div>

      {/* Natural Language Query Input */}
      <QueryInput query={query} onChange={setQuery} />

      {/* Error Message Display */}
      {error && (
        <div className="p-3 rounded-xl bg-red-950/40 border border-red-800/50 flex items-center space-x-2 text-red-300 text-xs animate-shake">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="pt-2 flex items-center space-x-3">
        <button
          type="button"
          onClick={onAnalyze}
          disabled={isAnalyzing}
          className="flex-1 py-3 px-4 rounded-xl bg-satellite-cyan hover:bg-cyan-400 text-space-900 font-bold text-xs uppercase tracking-wider shadow-lg shadow-satellite-cyan/20 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>{isAnalyzing ? 'Processing...' : 'ANALYZE IMAGERY'}</span>
        </button>

        <button
          type="button"
          onClick={onClear}
          disabled={isAnalyzing}
          className="py-3 px-4 rounded-xl bg-space-900 hover:bg-space-700 text-slate-300 hover:text-white border border-space-700 text-xs font-semibold uppercase tracking-wider flex items-center space-x-1.5 transition-colors disabled:opacity-50"
        >
          <Trash2 className="w-4 h-4 text-slate-400" />
          <span>CLEAR</span>
        </button>
      </div>
    </div>
  );
};
