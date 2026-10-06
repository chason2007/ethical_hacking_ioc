import React from 'react';
import { Shield, Upload, Activity, Sparkles } from 'lucide-react';
import type { Capture } from '../../types';

interface NavbarProps {
  currentCapture: Capture | null;
  captures: Capture[];
  onSelectCapture: (capture: Capture) => void;
  onOpenUpload: () => void;
  onLoadDemo: () => void;
  isLoadingDemo: boolean;
  backendHealthy: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentCapture,
  captures,
  onSelectCapture,
  onOpenUpload,
  onLoadDemo,
  isLoadingDemo,
  backendHealthy,
}) => {
  return (
    <header className="h-14 border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md sticky top-0 z-40 px-4 flex items-center justify-between">
      
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-cyan-950/80 border border-cyan-800/80 flex items-center justify-center text-cyan-400 shadow-sm">
          <Shield size={18} />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-sm tracking-wide text-slate-100">
              NetProtocol <span className="text-cyan-400">Inspector</span>
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-950 border border-cyan-800/50 text-cyan-400 uppercase">
              DEFENSIVE DPI
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-sans hidden sm:block">
            Packet Analysis of Common Network Protocols
          </span>
        </div>
      </div>

      {/* Active Capture Selector & Actions */}
      <div className="flex items-center gap-3">
        
        {/* Capture Dropdown */}
        <div className="relative">
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
            <Activity size={14} className="text-cyan-400" />
            <select
              aria-label="Active Capture"
              value={currentCapture?.id || ''}
              onChange={(e) => {
                const found = captures.find((c) => c.id === e.target.value);
                if (found) onSelectCapture(found);
              }}
              className="bg-transparent text-slate-200 outline-hidden font-mono text-xs cursor-pointer max-w-[160px] sm:max-w-[220px] truncate"
            >
              {captures.length === 0 ? (
                <option value="">No Captures Loaded</option>
              ) : (
                captures.map((c) => (
                  <option key={c.id} value={c.id} className="bg-slate-900 text-slate-200">
                    {c.filename} ({c.packet_count} pkts)
                  </option>
                ))
              )}
            </select>
          </div>
        </div>

        {/* Load Demo CTA */}
        <button
          onClick={onLoadDemo}
          disabled={isLoadingDemo}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-cyan-400 transition-colors disabled:opacity-50"
          title="Instantly generate synthetic PCAP with TCP, UDP, ICMP, DNS, HTTP, and scans"
        >
          <Sparkles size={13} className="text-cyan-400" />
          <span className="hidden md:inline">Load Demo Capture</span>
        </button>

        {/* Upload Button */}
        <button
          onClick={onOpenUpload}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-slate-950 transition-colors shadow-xs"
        >
          <Upload size={13} />
          <span>Upload PCAP</span>
        </button>

        {/* Backend Status Pill */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-mono border ${
            backendHealthy
              ? 'bg-emerald-950/40 border-emerald-800/40 text-emerald-400'
              : 'bg-red-950/40 border-red-800/40 text-red-400'
          }`}
          title={backendHealthy ? 'Backend API connected and active' : 'Backend connection error'}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${backendHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
          <span className="hidden lg:inline">{backendHealthy ? 'FastAPI Online' : 'Offline'}</span>
        </div>

      </div>

    </header>
  );
};
