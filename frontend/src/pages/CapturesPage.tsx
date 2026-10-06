import React, { useEffect, useState } from 'react';
import {
  FolderArchive, Trash2, Download
} from 'lucide-react';
import { api } from '../services/api';
import type { Capture } from '../types';
import { Badge } from '../components/common/Badge';

interface CapturesPageProps {
  currentCapture: Capture | null;
  onSelectCapture: (capture: Capture) => void;
  onCapturesUpdated: () => void;
}

export const CapturesPage: React.FC<CapturesPageProps> = ({
  currentCapture,
  onSelectCapture,
  onCapturesUpdated,
}) => {
  const [captures, setCaptures] = useState<Capture[]>([]);

  const fetchCaptures = () => {
    api.getCaptures()
      .then((data: Capture[]) => setCaptures(data))
      .catch((err: any) => console.error('Failed to load captures history:', err));
  };

  useEffect(() => {
    fetchCaptures();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this capture and all associated packets?')) {
      return;
    }
    try {
      await api.deleteCapture(id);
      fetchCaptures();
      onCapturesUpdated();
    } catch {
      alert('Failed to delete capture');
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FolderArchive size={20} className="text-cyan-400" />
            Analysis Capture History
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Archive of parsed network captures, stored analytical models, and security finding metrics.
          </p>
        </div>
      </div>

      {/* Captures Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-[11px]">
              <tr>
                <th className="py-3 px-4">Capture Target</th>
                <th className="py-3 px-3">File Size</th>
                <th className="py-3 px-3 text-right">Packets</th>
                <th className="py-3 px-3 text-right">Duration</th>
                <th className="py-3 px-3 text-center">Status</th>
                <th className="py-3 px-3 text-right">Security Findings</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {captures.map((c) => {
                const isActive = currentCapture?.id === c.id;

                return (
                  <tr
                    key={c.id}
                    onClick={() => onSelectCapture(c)}
                    className={`cursor-pointer transition-colors ${
                      isActive ? 'bg-cyan-950/60 border-l-2 border-cyan-400' : 'hover:bg-slate-800/40'
                    }`}
                  >
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-100 flex items-center gap-2">
                        <span>{c.filename}</span>
                        {isActive && <Badge variant="protocol">ACTIVE</Badge>}
                        {c.is_demo === 1 && <Badge variant="info">DEMO</Badge>}
                      </div>
                      <div className="text-[10px] text-slate-500 font-sans mt-0.5">
                        Uploaded: {new Date(c.created_at).toLocaleString()}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      {(c.file_size_bytes / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-3 px-3 text-right font-medium text-slate-200">
                      {c.packet_count.toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-right text-slate-400">
                      {c.duration_seconds.toFixed(2)}s
                    </td>
                    <td className="py-3 px-3 text-center">
                      <Badge variant="success">{c.status.toUpperCase()}</Badge>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <span className="font-bold text-amber-400">
                        {c.findings_count ?? 0}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                        <a
                          href={api.getReportUrl(c.id)}
                          download={`Report_${c.filename}.pdf`}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                          title="Download PDF Report"
                        >
                          <Download size={13} />
                        </a>
                        <button
                          onClick={(e) => handleDelete(c.id, e)}
                          className="p-1.5 rounded-lg bg-red-950/40 hover:bg-red-900/60 border border-red-800/40 text-red-400 transition-colors cursor-pointer"
                          title="Delete capture"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}

              {captures.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 italic">
                    No capture history recorded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
