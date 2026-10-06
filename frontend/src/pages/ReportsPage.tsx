import React, { useEffect, useState } from 'react';
import {
  FileText, Download, FileSpreadsheet, Code2, ArrowDownToLine
} from 'lucide-react';
import { api } from '../services/api';
import type { Capture, CaptureStatistics, SecurityOverview } from '../types';
import { Badge } from '../components/common/Badge';

interface ReportsPageProps {
  capture: Capture | null;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ capture }) => {
  const [stats, setStats] = useState<CaptureStatistics | null>(null);
  const [security, setSecurity] = useState<SecurityOverview | null>(null);
  const [generatingPdf, setGeneratingPdf] = useState(false);

  useEffect(() => {
    if (!capture) return;
    Promise.all([
      api.getStatistics(capture.id),
      api.getSecurity(capture.id),
    ])
      .then(([s, sec]) => {
        setStats(s);
        setSecurity(sec);
      })
      .catch((err) => console.error('Failed to load report data:', err));
  }, [capture]);

  if (!capture) {
    return <div className="p-8 text-center text-slate-500">No capture selected.</div>;
  }

  const handleDownloadPdf = () => {
    setGeneratingPdf(true);
    const link = document.createElement('a');
    link.href = api.getReportUrl(capture.id);
    link.download = `Security_Report_${capture.filename}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => setGeneratingPdf(false), 1200);
  };

  const handleDownloadCsv = () => {
    const link = document.createElement('a');
    link.href = api.getExportCsvUrl(capture.id);
    link.download = `packets_${capture.filename}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadJson = () => {
    const link = document.createElement('a');
    link.href = api.getExportJsonUrl(capture.id);
    link.download = `analysis_${capture.filename}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileText size={20} className="text-cyan-400" />
            Security Audit Report & Data Export
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Produce formal academic / SOC forensic audit deliverables in PDF, CSV, and JSON formats.
          </p>
        </div>
      </div>

      {/* Export Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* PDF Report Card */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-800/80 flex items-center justify-center text-cyan-400">
              <FileText size={20} />
            </div>
            <h3 className="text-sm font-semibold text-slate-100">Official Forensic PDF Report</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Complete publication-grade security audit document containing executive summary, protocol distribution, top endpoints, and security findings with analyst recommendations.
            </p>
          </div>

          <button
            onClick={handleDownloadPdf}
            disabled={generatingPdf}
            className="w-full py-2.5 px-4 rounded-lg text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-slate-950 transition-colors flex items-center justify-center gap-2 shadow-xs cursor-pointer"
          >
            <Download size={14} />
            <span>{generatingPdf ? 'Generating PDF...' : 'Download PDF Audit Report'}</span>
          </button>
        </div>

        {/* CSV Export Card */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-emerald-950/80 border border-emerald-800/80 flex items-center justify-center text-emerald-400">
              <FileSpreadsheet size={20} />
            </div>
            <h3 className="text-sm font-semibold text-slate-100">Raw Packets CSV Spreadsheet</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Tabular export of all captured packet records including relative timestamps, layer headers, TCP flags, port tuples, and frame length values.
            </p>
          </div>

          <button
            onClick={handleDownloadCsv}
            className="w-full py-2.5 px-4 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <ArrowDownToLine size={14} />
            <span>Export Packets CSV</span>
          </button>
        </div>

        {/* JSON Export Card */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-indigo-950/80 border border-indigo-800/80 flex items-center justify-center text-indigo-400">
              <Code2 size={20} />
            </div>
            <h3 className="text-sm font-semibold text-slate-100">Full Structured JSON Analysis</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Normalized hierarchical JSON schema representing endpoints, conversations, security anomalies, and protocol statistics for integration with external SIEM/SOC platforms.
            </p>
          </div>

          <button
            onClick={handleDownloadJson}
            className="w-full py-2.5 px-4 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <ArrowDownToLine size={14} />
            <span>Export Analysis JSON</span>
          </button>
        </div>

      </div>

      {/* Report Preview Document */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <span className="text-[10px] font-mono tracking-wider text-cyan-400 uppercase font-semibold">
              Deliverable Preview
            </span>
            <h2 className="text-base font-bold text-slate-100 mt-0.5">
              Executive Security Audit Summary
            </h2>
          </div>
          <Badge variant="default">Capture: {capture.filename}</Badge>
        </div>

        {/* Metadata summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-lg bg-slate-950/80 border border-slate-800 text-xs font-mono">
          <div>
            <span className="text-slate-500 block">Capture Target:</span>
            <span className="text-slate-200 font-bold">{capture.filename}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Total Wire Packets:</span>
            <span className="text-cyan-400 font-bold">{stats?.total_packets.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Timeline Duration:</span>
            <span className="text-slate-200 font-bold">{stats?.duration_seconds.toFixed(2)}s</span>
          </div>
          <div>
            <span className="text-slate-500 block">Flagged Findings:</span>
            <span className="text-amber-400 font-bold">{security?.total_findings} detected</span>
          </div>
        </div>

        {/* Executive Text */}
        <div className="space-y-3 text-xs text-slate-300 leading-relaxed font-sans">
          <p>
            An automated defensive protocol inspection was conducted on <strong>{capture.filename}</strong>. The capture encompasses <strong>{stats?.total_packets.toLocaleString()} frames</strong> across a duration of <strong>{stats?.duration_seconds.toFixed(2)} seconds</strong>, involving {stats?.unique_ips} distinct IP endpoints and {stats?.unique_conversations} conversation flows.
          </p>
          <p>
            The analytical engine identified <strong>{security?.total_findings} heuristic anomaly indicator{security?.total_findings !== 1 ? 's' : ''}</strong>. All observations have been contextualized with root cause rationale and recommended defensive remediations.
          </p>
        </div>

        {/* Recommendations list */}
        <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 space-y-2">
          <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
            Summary Defensive Action Items
          </h4>
          <ul className="text-xs text-slate-400 space-y-1.5 list-disc list-inside">
            <li>Review internal firewalls to rate-limit incomplete TCP SYN probes and deploy SYN cookies.</li>
            <li>Enforce migration of legacy plaintext transport (HTTP port 80, FTP port 21) to encrypted TLS/HTTPS and SFTP.</li>
            <li>Enable DNS RPZ (Response Policy Zones) and entropy auditing on recursive internal resolvers.</li>
            <li>Continuously baseline layer 3/4 traffic patterns to rapidly detect horizontal and vertical port enumeration.</li>
          </ul>
        </div>
      </div>

    </div>
  );
};
