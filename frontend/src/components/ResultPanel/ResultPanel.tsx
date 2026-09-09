import React from 'react';
import { AnalysisResult } from '../../types/analysis';
import { EvidencePanel } from '../EvidencePanel/EvidencePanel';
import { ConfidenceCard } from '../ConfidenceCard/ConfidenceCard';
import { EmptyState } from '../EmptyState/EmptyState';
import { FileText, Cpu, Clock, CheckCircle, Award, Download, Loader2, AlertCircle } from 'lucide-react';

interface ResultPanelProps {
  result: AnalysisResult | null;
  isAnalyzing: boolean;
  onDownloadReport?: () => void;
  isDownloadingReport?: boolean;
  downloadError?: string | null;
}

export const ResultPanel: React.FC<ResultPanelProps> = ({
  result,
  isAnalyzing,
  onDownloadReport,
  isDownloadingReport = false,
  downloadError = null,
}) => {
  return (
    <div className="bg-space-800 border border-space-700 rounded-2xl p-6 shadow-xl space-y-6 mt-8">
      <div className="border-b border-space-700 pb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <Award className="w-5 h-5 text-satellite-cyan" />
          <h2 className="text-base font-bold uppercase tracking-wider text-white">
            ANALYSIS RESULT & EVIDENCE
          </h2>
        </div>

        <div className="flex items-center space-x-3">
          {result && !isAnalyzing && onDownloadReport && (
            <button
              type="button"
              onClick={onDownloadReport}
              disabled={isDownloadingReport}
              className="py-1.5 px-3 rounded-lg bg-satellite-cyan/10 hover:bg-satellite-cyan/20 text-satellite-cyan border border-satellite-cyan/40 text-xs font-bold font-mono tracking-wider flex items-center space-x-1.5 transition-all disabled:opacity-50"
              title="Download structured markdown analysis report"
            >
              {isDownloadingReport ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span>[ DOWNLOAD ANALYSIS REPORT ]</span>
            </button>
          )}

          <span className="text-[10px] font-mono px-2.5 py-0.5 rounded bg-space-900 text-satellite-cyan border border-space-700 font-semibold">
            OUTPUT AREA
          </span>
        </div>
      </div>

      {downloadError && (
        <div className="p-3 rounded-xl bg-red-950/40 border border-red-800/50 flex items-center space-x-2 text-red-300 text-xs">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span>Report download error: {downloadError}</span>
        </div>
      )}

      {isAnalyzing ? (
        <div className="py-12 text-center space-y-3">
          <div className="w-10 h-10 border-4 border-satellite-cyan border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs font-semibold text-white uppercase tracking-wider">
            Agent Orchestrator Executing Task Pipeline...
          </p>
          <p className="text-xs text-slate-400 font-mono">
            Validating input, classifying query, and collecting evidence.
          </p>
        </div>
      ) : !result ? (
        <EmptyState
          title="Run an analysis to view results."
          subtitle="Select input imagery, enter a natural language prompt, and click Analyze Imagery."
          icon={<FileText className="w-10 h-10 text-slate-600" />}
        />
      ) : (
        <div className="space-y-6">
          {/* Answer Banner */}
          <div className="p-5 rounded-2xl bg-space-900 border border-space-700 space-y-2">
            <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-satellite-cyan">
              <CheckCircle className="w-4 h-4 text-satellite-cyan" />
              <span>ANSWER</span>
            </div>
            <p className="text-sm sm:text-base font-semibold text-white leading-relaxed font-sans">
              {result.answer}
            </p>
          </div>

          {/* Key Metrics Grid: Model/Tool, Analysis Type, Processing Time */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-space-900 border border-space-700 space-y-1">
              <div className="flex items-center space-x-1.5 text-xs text-slate-400">
                <Cpu className="w-3.5 h-3.5 text-satellite-cyan" />
                <span>MODEL / TOOL</span>
              </div>
              <p className="text-xs font-bold text-white font-mono">{result.modelTool}</p>
            </div>

            <div className="p-4 rounded-xl bg-space-900 border border-space-700 space-y-1">
              <div className="flex items-center space-x-1.5 text-xs text-slate-400">
                <FileText className="w-3.5 h-3.5 text-satellite-indigo" />
                <span>ANALYSIS TYPE</span>
              </div>
              <p className="text-xs font-bold text-white font-mono">{result.analysisType}</p>
            </div>

            <div className="p-4 rounded-xl bg-space-900 border border-space-700 space-y-1">
              <div className="flex items-center space-x-1.5 text-xs text-slate-400">
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                <span>PROCESSING TIME</span>
              </div>
              <p className="text-xs font-bold text-white font-mono">{result.processingTimeMs} ms</p>
            </div>
          </div>

          {/* Confidence Meter */}
          <ConfidenceCard score={result.confidenceScore} rating={result.confidenceRating} />

          {/* Visual Evidence Section */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              VISUAL EVIDENCE
            </h3>
            <EvidencePanel evidence={result.evidence} />
          </div>

          {/* Execution Summary */}
          <div className="p-4 rounded-xl bg-space-900/90 border border-space-700 space-y-1.5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              EXECUTION SUMMARY
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed font-sans">
              {result.executionSummary}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

