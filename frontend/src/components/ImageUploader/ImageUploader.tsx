import React, { useRef, useState } from 'react';
import { ImageFileMetadata } from '../../types/analysis';
import { formatFileSize, getFileExtension } from '../../utils/formatters';
import { UploadCloud, X, FileCheck, AlertCircle } from 'lucide-react';

interface ImageUploaderProps {
  label: string;
  image: ImageFileMetadata | null;
  onImageSelect: (fileMeta: ImageFileMetadata) => void;
  onImageRemove: () => void;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  label,
  image,
  onImageSelect,
  onImageRemove,
}) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const processFile = (file: File) => {
    setError(null);
    const validExtensions = ['png', 'jpg', 'jpeg', 'tif', 'tiff'];
    const ext = file.name.split('.').pop()?.toLowerCase() || '';

    if (!validExtensions.includes(ext)) {
      setError(`Unsupported file format (.${ext}). Supported: PNG, JPG, JPEG, TIFF, GeoTIFF.`);
      return;
    }

    const previewUrl = URL.createObjectURL(file);
    const format = getFileExtension(file.name);

    // Extract image dimensions if standard format
    if (['png', 'jpg', 'jpeg'].includes(ext)) {
      const img = new Image();
      img.src = previewUrl;
      img.onload = () => {
        onImageSelect({
          fileName: file.name,
          format: format,
          width: img.naturalWidth,
          height: img.naturalHeight,
          sizeBytes: file.size,
          formattedSize: formatFileSize(file.size),
          previewUrl: previewUrl,
          rawFile: file,
          crs: ext.includes('tif') ? 'EPSG:4326 (WGS84)' : undefined,
        });
      };
      img.onerror = () => {
        onImageSelect({
          fileName: file.name,
          format: format,
          sizeBytes: file.size,
          formattedSize: formatFileSize(file.size),
          previewUrl: previewUrl,
          rawFile: file,
        });
      };
    } else {
      // GeoTIFF / TIFF format
      onImageSelect({
        fileName: file.name,
        format: format.includes('TIF') ? 'GeoTIFF' : format,
        sizeBytes: file.size,
        formattedSize: formatFileSize(file.size),
        previewUrl: previewUrl,
        rawFile: file,
        resolution: '10m (Sentinel-2 standard)',
        crs: 'EPSG:4326 (WGS84)',
      });
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
        {label}
      </label>

      {image ? (
        <div className="relative group bg-space-900 border border-space-700 rounded-xl p-3 flex items-center space-x-3 shadow-inner">
          <div className="w-14 h-14 rounded-lg bg-space-800 border border-space-700 overflow-hidden flex items-center justify-center flex-shrink-0 relative">
            {image.format === 'GeoTIFF' || image.format === 'TIFF' || image.format === 'TIF' ? (
              <div className="flex flex-col items-center text-satellite-cyan">
                <FileCheck className="w-6 h-6" />
                <span className="text-[9px] font-mono uppercase mt-0.5">{image.format}</span>
              </div>
            ) : (
              <img
                src={image.previewUrl}
                alt={image.fileName}
                className="w-full h-full object-cover"
              />
            )}
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-white truncate" title={image.fileName}>
              {image.fileName}
            </p>
            <div className="flex items-center space-x-2 mt-1 text-[11px] text-slate-400 font-mono flex-wrap gap-y-1">
              {image.isDemo && (
                <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold font-mono">
                  DEMO DATA
                </span>
              )}
              <span className="px-1.5 py-0.5 rounded bg-space-800 text-satellite-cyan border border-space-700">
                {image.format}
              </span>
              <span>{image.formattedSize}</span>
              {image.width && image.height && (
                <span>{image.width}×{image.height}px</span>
              )}
            </div>
          </div>

          <button
            type="button"
            onClick={onImageRemove}
            className="p-1.5 rounded-lg bg-space-800 hover:bg-red-950/60 hover:text-red-400 text-slate-400 transition-colors border border-space-700"
            title="Remove image"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all ${
            isDragging
              ? 'border-satellite-cyan bg-satellite-cyan/10'
              : 'border-space-700 bg-space-900/60 hover:border-space-600 hover:bg-space-900'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".png,.jpg,.jpeg,.tif,.tiff"
            onChange={handleFileChange}
            className="hidden"
          />
          <UploadCloud className="w-7 h-7 mx-auto text-slate-400 mb-1" />
          <p className="text-xs font-medium text-slate-200">
            Click to upload or drag & drop
          </p>
          <p className="text-[10px] text-slate-400 mt-1 font-mono">
            Supported: PNG, JPG, JPEG, TIFF, GeoTIFF
          </p>
        </div>
      )}

      {error && (
        <div className="flex items-center space-x-1.5 text-xs text-red-400 mt-1">
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
