export type InputType = 'single' | 'bitemporal' | 'optical-sar';

export type StepStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface ImageFileMetadata {
  fileName: string;
  format: string;
  width?: number;
  height?: number;
  sizeBytes: number;
  formattedSize: string;
  previewUrl: string;
  rawFile: File;
  acquisitionDate?: string;
  satellite?: string;
  sensor?: string;
  resolution?: string;
  crs?: string;
  isDemo?: boolean;
}

export interface AgentStep {
  id: number;
  title: string;
  description: string;
  status: StepStatus;
  timestamp?: string;
}

export interface Evidence {
  id: string;
  title: string;
  description: string;
  type: 'image' | 'bbox' | 'mask' | 'metrics';
  url?: string;
  metrics?: Record<string, string | number>;
}

export interface AnalysisArtifact {
  name: string;
  type: string;
  url: string;
}

export interface RegionBoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  area: number;
}

export interface AnalysisResult {
  answer: string;
  confidenceScore: number; // 0 to 100
  confidenceRating: 'High' | 'Medium' | 'Low';
  modelTool: string;
  analysisType: string;
  processingTimeMs: number;
  executionSummary: string;
  evidence: Evidence[];
  changePercentage?: number;
  regions?: RegionBoundingBox[];
  artifacts?: AnalysisArtifact[];
  builtUpRegions?: { description: string }[];
  waterRegions?: { description: string }[];
}

export interface AnalysisResponse {
  success: boolean;
  message?: string;
  data?: AnalysisResult;
  steps?: AgentStep[];
}
