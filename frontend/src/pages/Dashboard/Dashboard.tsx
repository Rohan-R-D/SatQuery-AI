import React, { useState } from 'react';
import { InputType, ImageFileMetadata, AgentStep, AnalysisResult } from '../../types/analysis';
import { validateAnalysisInput } from '../../utils/validation';
import { analyzeImages, downloadAnalysisReport } from '../../services/api';
import { InputPanel } from '../../components/InputPanel/InputPanel';
import { ImageViewer } from '../../components/ImageViewer/ImageViewer';
import { AgentExecution } from '../../components/AgentExecution/AgentExecution';
import { ResultPanel } from '../../components/ResultPanel/ResultPanel';

const INITIAL_AGENT_STEPS: AgentStep[] = [
  { id: 1, title: 'Query Understanding', description: 'Parse query intent and domain entity extraction.', status: 'PENDING' },
  { id: 2, title: 'Input Validation', description: 'Validate raster formats, dimensions, and spatial alignment.', status: 'PENDING' },
  { id: 3, title: 'Task Classification', description: 'Categorize task (Single Scene VQA / Bi-Temporal / Multimodal Fusion).', status: 'PENDING' },
  { id: 4, title: 'Model Selection', description: 'Select optimal VLM backbone & Earth observation tools.', status: 'PENDING' },
  { id: 5, title: 'Analysis Execution', description: 'Process satellite bands and infer spatial features.', status: 'PENDING' },
  { id: 6, title: 'Evidence Generation', description: 'Extract visual bounding boxes, change masks, and spectral metrics.', status: 'PENDING' },
  { id: 7, title: 'Confidence Calculation', description: 'Calculate analytical certainty and cross-sensor agreement.', status: 'PENDING' },
  { id: 8, title: 'Response Generation', description: 'Synthesize structured response with execution trace.', status: 'PENDING' },
];

export const Dashboard: React.FC = () => {
  const [inputType, setInputType] = useState<InputType>('single');
  const [image1, setImage1] = useState<ImageFileMetadata | null>(null);
  const [image2, setImage2] = useState<ImageFileMetadata | null>(null);
  const [query, setQuery] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>(INITIAL_AGENT_STEPS);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  const [isDownloadingReport, setIsDownloadingReport] = useState<boolean>(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  // Handle Input Mode Switch (clears images if mode changes)
  const handleInputTypeChange = (newType: InputType) => {
    setInputType(newType);
    setError(null);
  };

  // Clear all form state
  const handleClear = () => {
    setImage1(null);
    setImage2(null);
    setQuery('');
    setError(null);
    setAgentSteps(INITIAL_AGENT_STEPS);
    setAnalysisResult(null);
    setIsAnalyzing(false);
    setDownloadError(null);
  };

  // Load Quick Demo Preset
  const handleLoadDemo = (
    demoType: InputType,
    img1: ImageFileMetadata,
    img2: ImageFileMetadata | null,
    demoQuery: string
  ) => {
    setInputType(demoType);
    setImage1(img1);
    setImage2(img2);
    setQuery(demoQuery);
    setError(null);
    setAgentSteps(INITIAL_AGENT_STEPS);
    setAnalysisResult(null);
    setDownloadError(null);
  };

  // Download Report handler
  const handleDownloadReport = async () => {
    if (!analysisResult) return;
    setIsDownloadingReport(true);
    setDownloadError(null);
    try {
      await downloadAnalysisReport(inputType, query, analysisResult, agentSteps);
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Failed to download report.';
      setDownloadError(errMsg);
    } finally {
      setIsDownloadingReport(false);
    }
  };

  // Analyze Button handler - End-to-end integration flow
  const handleAnalyze = async () => {
    // 1. Client-side input validation
    const validation = validateAnalysisInput(inputType, image1, image2, query);
    if (!validation.isValid) {
      setError(validation.errorMessage);
      return;
    }

    if (!image1) {
      setError("No image selected.");
      return;
    }

    // 2. Reset result & set Step 1 to RUNNING
    setError(null);
    setDownloadError(null);
    setIsAnalyzing(true);
    setAnalysisResult(null);

    setAgentSteps(
      INITIAL_AGENT_STEPS.map((s) =>
        s.id === 1 ? { ...s, status: 'RUNNING' } : { ...s, status: 'PENDING' }
      )
    );

    try {
      // 3. Dispatch multipart POST request to FastAPI backend
      const { result, executionTrace } = await analyzeImages(inputType, image1, image2, query);

      // 4. Map backend execution trace steps to UI timeline
      if (executionTrace && executionTrace.length > 0) {
        setAgentSteps(executionTrace);
      } else {
        setAgentSteps(INITIAL_AGENT_STEPS.map((s) => ({ ...s, status: 'COMPLETED' })));
      }

      // 5. Display analysis result in ResultPanel & ImageViewer
      setAnalysisResult(result);
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'An unexpected network error occurred.';
      setError(errMsg);

      // Mark running/pending steps as FAILED
      setAgentSteps((prevSteps) =>
        prevSteps.map((step) =>
          step.status === 'RUNNING' || (step.status === 'PENDING' && step.id <= 2)
            ? { ...step, status: 'FAILED' }
            : step
        )
      );
    } finally {
      // Guarantee loading state is always reset
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Main 3-Column Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Input Imagery & Query */}
        <div className="lg:col-span-4">
          <InputPanel
            inputType={inputType}
            setInputType={handleInputTypeChange}
            image1={image1}
            setImage1={setImage1}
            image2={image2}
            setImage2={setImage2}
            query={query}
            setQuery={setQuery}
            error={error}
            onAnalyze={handleAnalyze}
            onClear={handleClear}
            onLoadDemo={handleLoadDemo}
            isAnalyzing={isAnalyzing}
          />
        </div>

        {/* Center Column: Visual Analysis Canvas */}
        <div className="lg:col-span-5">
          <ImageViewer
            inputType={inputType}
            image1={image1}
            image2={image2}
            analysisResult={analysisResult}
          />
        </div>

        {/* Right Column: Agent Execution Timeline */}
        <div className="lg:col-span-3">
          <AgentExecution steps={agentSteps} />
        </div>
      </div>

      {/* Result & Evidence Area (Full Width Below) */}
      <ResultPanel
        result={analysisResult}
        isAnalyzing={isAnalyzing}
        onDownloadReport={handleDownloadReport}
        isDownloadingReport={isDownloadingReport}
        downloadError={downloadError}
      />
    </div>
  );
};

