import React, { useState } from 'react';
import { X, ChevronDown, ChevronRight, Layers, Binary, ShieldCheck } from 'lucide-react';
import type { Packet, PacketLayer } from '../../types';
import { Badge } from '../common/Badge';

interface PacketInspectorModalProps {
  packet: Packet | null;
  onClose: () => void;
}

export const PacketInspectorModal: React.FC<PacketInspectorModalProps> = ({ packet, onClose }) => {
  // Expanded layers state (all open by default)
  const [expanded, setExpanded] = useState<Record<number, boolean>>({
    0: true, 1: true, 2: true, 3: true, 4: true,
  });

  if (!packet) return null;

  let parsedLayers: PacketLayer[] = [];
  try {
    if (packet.layers_json) {
      parsedLayers = JSON.parse(packet.layers_json);
    }
  } catch {
    parsedLayers = [];
  }

  const toggleLayer = (idx: number) => {
    setExpanded(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4">
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-cyan-950/60 border border-cyan-800/50 text-cyan-400">
              <Layers size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-slate-100">
                  Packet #{packet.packet_number} Deep Inspector
                </h3>
                <Badge variant="protocol">{packet.protocol}</Badge>
                {packet.tcp_flags && (
                  <Badge variant="info">[{packet.tcp_flags}]</Badge>
                )}
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Timestamp: {packet.timestamp.toFixed(4)}s (Relative: +{packet.relative_time.toFixed(4)}s) | Length: {packet.length} bytes
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Summary Banner */}
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs text-slate-300">
            <span className="text-cyan-400 font-semibold">Summary Info:</span> {packet.info || 'No summary'}
          </div>

          {/* Protocol Hierarchy Tree */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Layers size={14} className="text-cyan-500" />
              Protocol Layer Hierarchy
            </h4>

            {parsedLayers.length > 0 ? (
              <div className="space-y-2 font-mono text-xs">
                {parsedLayers.map((layer, idx) => {
                  const isOpen = expanded[idx] ?? true;
                  return (
                    <div
                      key={idx}
                      className="border border-slate-800 rounded-lg bg-slate-950/70 overflow-hidden"
                    >
                      <button
                        onClick={() => toggleLayer(idx)}
                        className="w-full flex items-center justify-between px-4 py-2.5 bg-slate-900/90 hover:bg-slate-800/80 transition-colors text-left cursor-pointer"
                      >
                        <div className="flex items-center gap-2 font-medium text-slate-200">
                          {isOpen ? <ChevronDown size={14} className="text-cyan-400" /> : <ChevronRight size={14} className="text-slate-500" />}
                          <span className="text-cyan-400 font-bold">[{layer.layer}]</span>
                          <span className="text-slate-300 text-[11px] truncate">{layer.summary}</span>
                        </div>
                        <span className="text-[10px] text-slate-500 font-sans uppercase">
                          {Object.keys(layer.fields || {}).length} fields
                        </span>
                      </button>

                      {isOpen && layer.fields && (
                        <div className="p-3 border-t border-slate-800/80 grid grid-cols-1 sm:grid-cols-2 gap-2 bg-slate-950/40">
                          {Object.entries(layer.fields).map(([k, v]) => (
                            <div key={k} className="flex items-baseline justify-between p-1.5 rounded bg-slate-900/40 border border-slate-800/40">
                              <span className="text-slate-400 text-[11px]">{k}:</span>
                              <span className="text-slate-200 text-[11px] font-semibold truncate max-w-[65%] text-right">
                                {String(v)}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-xs text-slate-500 italic p-4 text-center border border-slate-800 rounded-lg">
                No hierarchical layer breakdown available.
              </div>
            )}
          </div>

          {/* Hex / ASCII Payload Preview */}
          {packet.payload_preview && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Binary size={14} className="text-cyan-500" />
                Raw Payload Inspection (Hex & ASCII Safe Representation)
              </h4>
              <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 font-mono text-[11px] text-emerald-400/90 whitespace-pre overflow-x-auto leading-relaxed">
                {packet.payload_preview}
              </div>
              <p className="text-[11px] text-slate-500">
                Safe defensive view: Non-printable bytes are represented as periods. Payloads are never executed.
              </p>
            </div>
          )}

          {/* Educational Note */}
          <div className="p-3 rounded-lg border border-cyan-900/30 bg-cyan-950/20 text-xs text-cyan-200/80 flex items-start gap-2.5">
            <ShieldCheck size={16} className="text-cyan-400 mt-0.5 shrink-0" />
            <div>
              <span className="font-semibold text-cyan-300">Defensive Packet Analysis Note:</span>
              <p className="mt-0.5 text-slate-400">
                Observing protocol headers allows security analysts to verify compliance with RFC standards, detect flag anomalies (e.g. orphan SYN or unusual TCP option sequences), and inspect payload structure without running malicious binaries.
              </p>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="flex items-center justify-end px-6 py-3 border-t border-slate-800 bg-slate-950/60">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors cursor-pointer"
          >
            Close Inspector
          </button>
        </div>

      </div>
    </div>
  );
};
