import React, { useState } from 'react';
import { InputType, ImageFileMetadata, AnalysisResult } from '../../types/analysis';
import { EmptyState } from '../EmptyState/EmptyState';
import { ZoomIn, ZoomOut, RotateCcw, Maximize, Maximize2, Layers, Info } from 'lucide-react';

interface ImageViewerProps {
  inputType: InputType;
  image1: ImageFileMetadata | null;
  image2: ImageFileMetadata | null;
  analysisResult?: AnalysisResult | null;
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  inputType,
  image1,
  image2,
  analysisResult,
}) => {
  const [zoom, setZoom] = useState<number>(1);
  const [activeTab, setActiveTab] = useState<'default' | 'before' | 'after' | 'change' | 'optical' | 'sar' | 'analysis'>('default');
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 3));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));
  const handleResetZoom = () => setZoom(1);

  // Determine current active image/artifact based on tab
  const getDisplayedContent = (): { url: string; label: string; isArtifact?: boolean } | null => {
    if (inputType === 'single') {
      return image1 ? { url: image1.previewUrl, label: image1.fileName } : null;
    }

    if (inputType === 'bitemporal') {
      if (activeTab === 'after' && image2) {
        return { url: image2.previewUrl, label: image2.fileName };
      }
      if (activeTab === 'change') {
        // Check if real change artifacts exist from backend execution
        const overlayArtifact = analysisResult?.artifacts?.find(a => a.name === 'change_overlay' || a.name === 'difference_map');
        if (overlayArtifact) {
          return { url: overlayArtifact.url, label: 'OpenCV Change Overlay', isArtifact: true };
        }
        return null; // Awaiting pipeline run
      }
      return image1 ? { url: image1.previewUrl, label: image1.fileName } : null;
    }

    if (inputType === 'optical-sar') {
      if (activeTab === 'sar' && image2) {
        return { url: image2.previewUrl, label: image2.fileName };
      }
      if (activeTab === 'analysis') {
        const sarArtifact = analysisResult?.artifacts?.find(a => a.name === 'change_overlay');
        if (sarArtifact) {
          return { url: sarArtifact.url, label: 'Optical + SAR Multimodal Analysis', isArtifact: true };
        }
        return null;
      }
      return image1 ? { url: image1.previewUrl, label: image1.fileName } : null;
    }

    return image1 ? { url: image1.previewUrl, label: image1.fileName } : null;
  };

  const displayedContent = getDisplayedContent();

  return (
    <div className="bg-space-800 border border-space-700 rounded-2xl p-5 shadow-xl flex flex-col space-y-4">
      {/* Header & Mode Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-space-700 pb-3">
        <div className="flex items-center space-x-2">
          <h2 className="text-sm font-bold uppercase tracking-wider text-white">
            VISUAL ANALYSIS
          </h2>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-space-900 text-satellite-cyan border border-space-700">
            {inputType === 'optical-sar' ? 'OPTICAL + SAR MULTIMODAL PROTOTYPE' : inputType.toUpperCase()}
          </span>
        </div>

        {/* Dynamic Mode Tabs for Bi-Temporal */}
        {inputType === 'bitemporal' && (image1 || image2) && (
          <div className="flex items-center space-x-1 p-1 bg-space-900 rounded-lg border border-space-700 text-xs">
            <button
              onClick={() => setActiveTab('before')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                activeTab !== 'after' && activeTab !== 'change'
                  ? 'bg-satellite-cyan text-space-900 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              BEFORE (T1)
            </button>
            <button
              onClick={() => setActiveTab('after')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                activeTab === 'after'
                  ? 'bg-satellite-cyan text-space-900 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              AFTER (T2)
            </button>
            <button
              onClick={() => setActiveTab('change')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                activeTab === 'change'
                  ? 'bg-amber-500 text-space-900 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              CHANGE MAP
            </button>
          </div>
        )}

        {/* Dynamic Mode Tabs for Optical + SAR */}
        {inputType === 'optical-sar' && (image1 || image2) && (
          <div className="flex items-center space-x-1 p-1 bg-space-900 rounded-lg border border-space-700 text-xs">
            <button
              onClick={() => setActiveTab('optical')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                activeTab !== 'sar' && activeTab !== 'analysis'
                  ? 'bg-satellite-cyan text-space-900 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              OPTICAL
            </button>
            <button
              onClick={() => setActiveTab('sar')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                activeTab === 'sar'
                  ? 'bg-satellite-cyan text-space-900 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              SAR
            </button>
            <button
              onClick={() => setActiveTab('analysis')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                activeTab === 'analysis'
                  ? 'bg-amber-500 text-space-900 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              ANALYSIS
            </button>
          </div>
        )}
      </div>

      {/* Main Canvas Viewer */}
      <div
        className={`relative bg-space-900 border border-space-700 rounded-xl overflow-hidden min-h-[320px] flex items-center justify-center ${
          isFullscreen ? 'fixed inset-4 z-50 shadow-2xl border-satellite-cyan' : ''
        }`}
      >
        {!image1 && !image2 ? (
          <EmptyState
            title="Upload satellite imagery to begin analysis."
            subtitle="Supported formats: PNG, JPG, JPEG, TIFF, GeoTIFF"
            icon={<Layers className="w-10 h-10 text-satellite-cyan" />}
          />
        ) : (activeTab === 'change' || activeTab === 'analysis') && !displayedContent ? (
          <div className="p-8 text-center space-y-2">
            <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold uppercase bg-amber-500/10 text-amber-400 border border-amber-500/30">
              Awaiting Pipeline Execution
            </span>
            <p className="text-xs text-slate-300 font-medium max-w-md mx-auto">
              Click &quot;ANALYZE IMAGERY&quot; to run the backend pipeline and generate visual change maps and overlay artifacts.
            </p>
          </div>
        ) : displayedContent ? (
          <div className="w-full h-full p-4 flex items-center justify-center overflow-auto">
            <img
              src={displayedContent.url}
              alt={displayedContent.label}
              style={{ transform: `scale(${zoom})`, transition: 'transform 0.15s ease-out' }}
              className="max-h-[360px] w-auto object-contain rounded shadow-lg"
            />
          </div>
        ) : null}

        {/* Floating Zoom & Control Toolbar */}
        {displayedContent && (
          <div className="absolute bottom-3 right-3 flex items-center space-x-1.5 p-1.5 bg-space-800/90 backdrop-blur border border-space-700 rounded-xl shadow-lg text-xs">
            <button
              onClick={handleZoomOut}
              className="p-1.5 rounded-lg hover:bg-space-700 text-slate-300 hover:text-white"
              title="Zoom out (-)"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="font-mono text-[11px] px-1 text-slate-300 font-semibold min-w-[36px] text-center">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={handleZoomIn}
              className="p-1.5 rounded-lg hover:bg-space-700 text-slate-300 hover:text-white"
              title="Zoom in (+)"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <div className="w-px h-4 bg-space-700 mx-0.5" />
            <button
              onClick={handleResetZoom}
              className="p-1.5 rounded-lg hover:bg-space-700 text-slate-300 hover:text-white"
              title="Reset zoom"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-1.5 rounded-lg hover:bg-space-700 text-slate-300 hover:text-white"
              title="Toggle Fullscreen"
            >
              {isFullscreen ? <Maximize2 className="w-3.5 h-3.5" /> : <Maximize className="w-3.5 h-3.5" />}
            </button>
          </div>
        )}
      </div>

      {/* Image Metadata Info Table */}
      <div className="bg-space-900/80 border border-space-700 rounded-xl p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-space-800 pb-2">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-300">
            <Info className="w-4 h-4 text-satellite-cyan" />
            <span>IMAGE INFORMATION</span>
          </div>
          {image1 && (
            <span className="text-[10px] font-mono text-slate-400">
              Loaded Metadata
            </span>
          )}
        </div>

        {image1 ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-sans">File Name</span>
              <span className="text-white truncate block font-medium" title={image1.fileName}>
                {image1.fileName}
              </span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-sans">Format</span>
              <span className="text-satellite-cyan font-bold">{image1.format}</span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-sans">Dimensions</span>
              <span className="text-white">
                {image1.width && image1.height
                  ? `${image1.width} × ${image1.height} px`
                  : 'N/A'}
              </span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-sans">File Size</span>
              <span className="text-white">{image1.formattedSize}</span>
            </div>

            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-sans">Satellite</span>
              <span className="text-slate-400 font-sans italic">{image1.satellite || '-'}</span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-sans">Sensor</span>
              <span className="text-slate-400 font-sans italic">{image1.sensor || '-'}</span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-sans">Resolution</span>
              <span className="text-slate-400 font-sans italic">{image1.resolution || '-'}</span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-sans">CRS</span>
              <span className="text-slate-400 font-sans italic">{image1.crs || '-'}</span>
            </div>
          </div>
        ) : (
          <p className="text-xs text-slate-400 font-mono py-1">
            No image loaded. Metadata will display upon upload.
          </p>
        )}
      </div>
    </div>
  );
};
