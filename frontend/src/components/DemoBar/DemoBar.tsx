import React, { useState } from 'react';
import { InputType, ImageFileMetadata } from '../../types/analysis';
import { formatFileSize } from '../../utils/formatters';
import { getApiBaseUrl } from '../../utils/config';
import { PlayCircle, Loader2, AlertCircle, X } from 'lucide-react';

const BASE_URL = getApiBaseUrl();

interface DemoBarProps {
  onLoadDemo: (
    type: InputType,
    img1: ImageFileMetadata,
    img2: ImageFileMetadata | null,
    query: string
  ) => void;
  disabled?: boolean;
}

export const DemoBar: React.FC<DemoBarProps> = ({ onLoadDemo, disabled }) => {
  const [loadingDemo, setLoadingDemo] = useState<string | null>(null);
  const [setupInstruction, setSetupInstruction] = useState<string | null>(null);

  const fetchSampleFile = async (urlPath: string, filename: string): Promise<ImageFileMetadata> => {
    const fullUrl = `${BASE_URL}${urlPath}`;
    const response = await fetch(fullUrl);
    if (!response.ok) {
      throw new Error(
        `Demo data file not found at ${urlPath}.\n\n` +
        `To configure Quick Demo Mode, please place real satellite images in the demo-data/ directory:\n` +
        `• demo-data/single/sample.png\n` +
        `• demo-data/temporal/before/sample.png\n` +
        `• demo-data/temporal/after/sample.png\n` +
        `• demo-data/optical-sar/optical/sample.png\n` +
        `• demo-data/optical-sar/sar/sample.png\n\n` +
        `Refer to demo-data/README.md for detailed instructions.`
      );
    }
    const blob = await response.blob();
    const file = new File([blob], filename, { type: blob.type || 'image/png' });
    const previewUrl = URL.createObjectURL(file);

    return {
      fileName: filename,
      format: 'PNG',
      width: 300,
      height: 300,
      sizeBytes: file.size,
      formattedSize: formatFileSize(file.size),
      previewUrl: previewUrl,
      rawFile: file,
      satellite: 'Sentinel-2 / Sentinel-1 Swatch',
      sensor: 'MSI / SAR GRD',
      resolution: '10m',
      crs: 'EPSG:4326 (WGS84)',
      isDemo: true,
    };
  };

  const handleDemo1 = async () => {
    setLoadingDemo('single');
    setSetupInstruction(null);
    try {
      const img1 = await fetchSampleFile('/demo-data/single/sample.png', 'sample_single_vqa.png');
      onLoadDemo('single', img1, null, 'Is there a water body in this image?');
    } catch (err) {
      console.error(err);
      setSetupInstruction(err instanceof Error ? err.message : 'Failed to load Single Image VQA demo dataset.');
    } finally {
      setLoadingDemo(null);
    }
  };

  const handleDemo2 = async () => {
    setLoadingDemo('bitemporal');
    setSetupInstruction(null);
    try {
      const img1 = await fetchSampleFile('/demo-data/temporal/before/sample.png', 't1_before_sample.png');
      const img2 = await fetchSampleFile('/demo-data/temporal/after/sample.png', 't2_after_sample.png');
      onLoadDemo('bitemporal', img1, img2, 'Has the built-up area increased between these two dates?');
    } catch (err) {
      console.error(err);
      setSetupInstruction(err instanceof Error ? err.message : 'Failed to load Bi-Temporal Change demo dataset.');
    } finally {
      setLoadingDemo(null);
    }
  };

  const handleDemo3 = async () => {
    setLoadingDemo('optical-sar');
    setSetupInstruction(null);
    try {
      const img1 = await fetchSampleFile('/demo-data/optical-sar/optical/sample.png', 'optical_sample.png');
      const img2 = await fetchSampleFile('/demo-data/optical-sar/sar/sample.png', 'sar_sample.png');
      onLoadDemo('optical-sar', img1, img2, 'Use both images to identify built-up and water-covered regions.');
    } catch (err) {
      console.error(err);
      setSetupInstruction(err instanceof Error ? err.message : 'Failed to load Optical + SAR demo dataset.');
    } finally {
      setLoadingDemo(null);
    }
  };

  return (
    <div className="bg-space-900/90 border border-space-700/80 rounded-xl p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-slate-300">
          <PlayCircle className="w-4 h-4 text-satellite-cyan" />
          <span>QUICK PRESENTATION DEMO MODE</span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-space-800 text-satellite-cyan border border-space-700 font-semibold">
          1-CLICK PRESETS
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        <button
          type="button"
          onClick={handleDemo1}
          disabled={disabled || loadingDemo !== null}
          className="flex items-center justify-center space-x-1.5 p-2 rounded-lg bg-space-800 hover:bg-space-700 text-slate-200 hover:text-white border border-space-700 text-xs font-medium transition-all disabled:opacity-50"
        >
          {loadingDemo === 'single' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin text-satellite-cyan" />
          ) : (
            <span className="font-mono text-satellite-cyan text-[11px] font-bold">[ SINGLE IMAGE VQA ]</span>
          )}
        </button>

        <button
          type="button"
          onClick={handleDemo2}
          disabled={disabled || loadingDemo !== null}
          className="flex items-center justify-center space-x-1.5 p-2 rounded-lg bg-space-800 hover:bg-space-700 text-slate-200 hover:text-white border border-space-700 text-xs font-medium transition-all disabled:opacity-50"
        >
          {loadingDemo === 'bitemporal' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin text-satellite-cyan" />
          ) : (
            <span className="font-mono text-satellite-cyan text-[11px] font-bold">[ BI-TEMPORAL CHANGE ]</span>
          )}
        </button>

        <button
          type="button"
          onClick={handleDemo3}
          disabled={disabled || loadingDemo !== null}
          className="flex items-center justify-center space-x-1.5 p-2 rounded-lg bg-space-800 hover:bg-space-700 text-slate-200 hover:text-white border border-space-700 text-xs font-medium transition-all disabled:opacity-50"
        >
          {loadingDemo === 'optical-sar' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin text-satellite-cyan" />
          ) : (
            <span className="font-mono text-satellite-cyan text-[11px] font-bold">[ OPTICAL + SAR ]</span>
          )}
        </button>
      </div>

      {/* Clear Setup Instructions Banner if Demo Dataset File missing */}
      {setupInstruction && (
        <div className="mt-2 p-3 rounded-lg bg-amber-950/50 border border-amber-800/60 text-amber-200 text-xs space-y-2 relative">
          <button
            type="button"
            onClick={() => setSetupInstruction(null)}
            className="absolute top-2 right-2 p-1 text-amber-400 hover:text-amber-200"
          >
            <X className="w-4 h-4" />
          </button>
          <div className="flex items-center space-x-2 font-bold text-amber-300">
            <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <span>DEMO DATA SETUP REQUIRED</span>
          </div>
          <p className="whitespace-pre-line font-mono text-[11px] leading-relaxed text-amber-200">
            {setupInstruction}
          </p>
        </div>
      )}
    </div>
  );
};

