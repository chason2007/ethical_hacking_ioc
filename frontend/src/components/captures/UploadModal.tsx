import React, { useState, useRef } from 'react';
import { Upload, X, FileCheck, AlertCircle, Loader2, CheckCircle2 } from 'lucide-react';
import { api } from '../../services/api';
import type { Capture } from '../../types';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (capture: Capture) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'parsing' | 'analyzing' | 'done' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileSelect = (file: File) => {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!['.pcap', '.pcapng', '.cap'].includes(ext)) {
      setErrorMessage(`Unsupported file format '${ext}'. Please select a valid .pcap or .pcapng file.`);
      setSelectedFile(null);
      return;
    }
    setErrorMessage('');
    setSelectedFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile) return;

    try {
      setStatus('uploading');
      setTimeout(() => setStatus('parsing'), 600);
      setTimeout(() => setStatus('analyzing'), 1200);

      const capture = await api.uploadCapture(selectedFile);

      setStatus('done');
      setTimeout(() => {
        onSuccess(capture);
        onClose();
      }, 800);
    } catch (err: any) {
      setStatus('error');
      setErrorMessage(err.message || 'Failed to process PCAP file.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          disabled={status !== 'idle' && status !== 'error' && status !== 'done'}
        >
          <X size={18} />
        </button>

        <h3 className="text-base font-semibold text-slate-100 mb-1 flex items-center gap-2">
          <Upload size={18} className="text-cyan-400" />
          Upload Network Packet Capture
        </h3>
        <p className="text-xs text-slate-400 mb-5">
          Select or drop a <code className="text-cyan-400">.pcap</code> or <code className="text-cyan-400">.pcapng</code> file for automated parsing and defensive analysis.
        </p>

        {/* Drag and Drop Zone */}
        {status === 'idle' || status === 'error' ? (
          <div>
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                dragOver
                  ? 'border-cyan-500 bg-cyan-950/20'
                  : selectedFile
                  ? 'border-emerald-700 bg-emerald-950/10'
                  : 'border-slate-800 hover:border-slate-700 bg-slate-950/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pcap,.pcapng,.cap"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileSelect(e.target.files[0]);
                  }
                }}
              />

              {selectedFile ? (
                <div className="space-y-2">
                  <div className="w-12 h-12 mx-auto rounded-full bg-emerald-950/60 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
                    <FileCheck size={24} />
                  </div>
                  <div className="font-medium text-slate-200 text-sm">{selectedFile.name}</div>
                  <div className="text-xs text-slate-500 font-mono">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </div>
                  <span className="inline-block text-[11px] text-cyan-400 underline pt-1">
                    Click to change file
                  </span>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="w-12 h-12 mx-auto rounded-full bg-slate-800 flex items-center justify-center text-slate-400">
                    <Upload size={22} />
                  </div>
                  <div className="text-sm font-medium text-slate-300">
                    Drag and drop your PCAP file here, or <span className="text-cyan-400">browse</span>
                  </div>
                  <div className="text-xs text-slate-500">
                    Supports .pcap, .pcapng, and .cap (up to 500MB)
                  </div>
                </div>
              )}
            </div>

            {errorMessage && (
              <div className="mt-3 p-3 bg-red-950/40 border border-red-800/60 rounded-lg text-xs text-red-300 flex items-center gap-2">
                <AlertCircle size={16} className="text-red-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <div className="mt-5 flex items-center justify-end gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-xs font-medium rounded-lg text-slate-300 hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUploadAndAnalyze}
                disabled={!selectedFile}
                className="px-5 py-2 text-xs font-semibold rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 transition-colors"
              >
                Analyze Capture
              </button>
            </div>
          </div>
        ) : (
          /* Processing Progress State */
          <div className="py-8 text-center space-y-4">
            <div className="w-14 h-14 mx-auto rounded-full bg-cyan-950/60 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
              {status === 'done' ? (
                <CheckCircle2 size={32} className="text-emerald-400" />
              ) : (
                <Loader2 size={32} className="animate-spin text-cyan-400" />
              )}
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-200">
                {status === 'uploading' && 'Uploading capture stream...'}
                {status === 'parsing' && 'Scapy Layer Parsing in Progress...'}
                {status === 'analyzing' && 'Executing Defensive Heuristic Rules...'}
                {status === 'done' && 'Capture Analysis Completed!'}
              </h4>
              <p className="text-xs text-slate-400 mt-1">
                {status === 'done'
                  ? 'Redirecting to analytical dashboard...'
                  : 'Normalizing packets, building conversation flows, and inspecting headers.'}
              </p>
            </div>

            {/* Stepper progress */}
            <div className="flex items-center justify-center gap-2 text-[10px] font-mono uppercase tracking-wider text-slate-500 pt-2">
              <span className="text-cyan-400 font-bold">Upload</span>
              <span>&rarr;</span>
              <span className={status === 'parsing' || status === 'analyzing' || status === 'done' ? 'text-cyan-400 font-bold' : ''}>Parse</span>
              <span>&rarr;</span>
              <span className={status === 'analyzing' || status === 'done' ? 'text-cyan-400 font-bold' : ''}>Analyze</span>
              <span>&rarr;</span>
              <span className={status === 'done' ? 'text-emerald-400 font-bold' : ''}>Ready</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
