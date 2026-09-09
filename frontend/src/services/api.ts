import { InputType, ImageFileMetadata, AnalysisResult, AgentStep, Evidence, AnalysisArtifact, RegionBoundingBox } from '../types/analysis';
import { getApiBaseUrl } from '../utils/config';

const BASE_URL = getApiBaseUrl();

export interface BackendTraceStep {
  id: number;
  title: string;
  description: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  timestamp?: string;
}

export interface BackendEvidenceItem {
  id: string;
  title: string;
  description: string;
  type: string;
  url?: string;
  metrics?: Record<string, string | number>;
}

export interface BackendAnalysisResponse {
  success: boolean;
  task: string;
  input_type: string;
  answer: string;
  confidence: number;
  confidence_explanation: string;
  model_used: string;
  evidence: BackendEvidenceItem[];
  execution_trace: BackendTraceStep[];
  processing_time: number;
  change_percentage?: number;
  regions?: RegionBoundingBox[];
  artifacts?: AnalysisArtifact[];
  built_up_regions?: { description: string }[];
  water_regions?: { description: string }[];
}

export const checkHealth = async (): Promise<{ status: string; service: string }> => {
  const response = await fetch(`${BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json();
};

export const analyzeImages = async (
  inputType: InputType,
  image1: ImageFileMetadata,
  image2: ImageFileMetadata | null,
  query: string
): Promise<{ result: AnalysisResult; executionTrace: AgentStep[] }> => {
  const formData = new FormData();

  const backendInputType =
    inputType === 'bitemporal'
      ? 'bi_temporal'
      : inputType === 'optical-sar'
      ? 'optical_sar'
      : 'single';

  formData.append('input_type', backendInputType);
  formData.append('query', query);
  formData.append('image', image1.rawFile, image1.fileName);

  if (image2 && image2.rawFile) {
    formData.append('second_image', image2.rawFile, image2.fileName);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(`${BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `Server notice (${response.status})`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          if (Array.isArray(errorJson.detail)) {
            errorMessage = errorJson.detail.map((err: { msg?: string }) => err.msg || 'Validation error').join(', ');
          } else {
            errorMessage = errorJson.detail;
          }
        }
      } catch {
        errorMessage = await response.text() || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const data: BackendAnalysisResponse = await response.json();

    const confidenceRating: 'High' | 'Medium' | 'Low' =
      data.confidence >= 85 ? 'High' : data.confidence >= 60 ? 'Medium' : 'Low';

    const mappedEvidence: Evidence[] = (data.evidence || []).map((item) => ({
      id: item.id,
      title: item.title,
      description: item.description,
      type: (item.type as 'image' | 'bbox' | 'mask' | 'metrics') || 'bbox',
      url: item.url,
      metrics: item.metrics,
    }));

    const mappedTrace: AgentStep[] = (data.execution_trace || []).map((step) => ({
      id: step.id,
      title: step.title,
      description: step.description,
      status: step.status,
      timestamp: step.timestamp,
    }));

    const result: AnalysisResult = {
      answer: data.answer,
      confidenceScore: Math.round(data.confidence),
      confidenceRating: confidenceRating,
      modelTool: data.model_used,
      analysisType: data.task,
      processingTimeMs: Math.round(data.processing_time * 1000),
      executionSummary: data.confidence_explanation,
      evidence: mappedEvidence,
      changePercentage: data.change_percentage,
      regions: data.regions,
      artifacts: data.artifacts,
      builtUpRegions: data.built_up_regions,
      waterRegions: data.water_regions,
    };

    return { result, executionTrace: mappedTrace };
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Analysis request timed out after 30 seconds.');
      }
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        throw new Error('Backend server unavailable. Please ensure FastAPI is running on http://localhost:8000.');
      }
      throw error;
    }
    throw new Error('An unexpected network error occurred.');
  }
};

export const downloadAnalysisReport = async (
  inputType: InputType,
  query: string,
  result: AnalysisResult,
  executionTrace: AgentStep[] = []
): Promise<void> => {
  const backendInputType =
    inputType === 'bitemporal'
      ? 'bi_temporal'
      : inputType === 'optical-sar'
      ? 'optical_sar'
      : 'single';

  const reportPayload = {
    query: query,
    input_type: backendInputType,
    task: result.analysisType,
    answer: result.answer,
    confidence: result.confidenceScore,
    confidence_explanation: result.executionSummary,
    model_used: result.modelTool,
    evidence: result.evidence,
    execution_trace: executionTrace,
    processing_time: result.processingTimeMs / 1000.0,
    change_percentage: result.changePercentage,
    timestamp: new Date().toISOString(),
  };

  const response = await fetch(`${BASE_URL}/api/report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(reportPayload),
  });

  if (!response.ok) {
    let errorMsg = `Report generation failed (${response.status})`;
    try {
      const errJson = await response.json();
      if (errJson.detail) errorMsg = errJson.detail;
    } catch {
      // fallback
    }
    throw new Error(errorMsg);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const contentDisposition = response.headers.get('content-disposition');
  let filename = 'satquery_analysis_report.md';
  if (contentDisposition && contentDisposition.includes('filename=')) {
    filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
  }

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

