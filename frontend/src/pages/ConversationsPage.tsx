import React, { useEffect, useState } from 'react';
import { Users, ArrowRightLeft } from 'lucide-react';
import { api } from '../services/api';
import type { Capture, Conversation } from '../types';
import { Badge } from '../components/common/Badge';

interface ConversationsPageProps {
  capture: Capture | null;
}

export const ConversationsPage: React.FC<ConversationsPageProps> = ({ capture }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [sortBy, setSortBy] = useState('packets');

  useEffect(() => {
    if (!capture) return;
    api.getConversations(capture.id, sortBy)
      .then((data) => setConversations(data))
      .catch((err) => console.error('Failed to load conversations:', err));
  }, [capture, sortBy]);

  if (!capture) {
    return <div className="p-8 text-center text-slate-500">No capture selected.</div>;
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Title & Sorting */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Users size={20} className="text-cyan-400" />
            Network Conversations & Flow Analysis
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Bidirectional endpoint flows aggregated by 5-tuple IP pairs, protocol, and port numbers.
          </p>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Sort by:</span>
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
            <button
              onClick={() => setSortBy('packets')}
              className={`px-2.5 py-1 rounded transition-colors cursor-pointer ${
                sortBy === 'packets' ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Packets
            </button>
            <button
              onClick={() => setSortBy('bytes')}
              className={`px-2.5 py-1 rounded transition-colors cursor-pointer ${
                sortBy === 'bytes' ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Bytes
            </button>
            <button
              onClick={() => setSortBy('duration')}
              className={`px-2.5 py-1 rounded transition-colors cursor-pointer ${
                sortBy === 'duration' ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Duration
            </button>
          </div>
        </div>
      </div>

      {/* Conversations Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-[11px]">
              <tr>
                <th className="py-2.5 px-3">Protocol</th>
                <th className="py-2.5 px-3">Endpoint A (Port)</th>
                <th className="py-2.5 px-2 text-center text-slate-600">&harr;</th>
                <th className="py-2.5 px-3">Endpoint B (Port)</th>
                <th className="py-2.5 px-3 text-right">Packets (A &rarr; B / B &rarr; A)</th>
                <th className="py-2.5 px-3 text-right">Total Packets</th>
                <th className="py-2.5 px-3 text-right">Total Bytes</th>
                <th className="py-2.5 px-3 text-right">Duration (s)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {conversations.map((c) => {
                const ratioA = c.total_packets > 0 ? (c.packets_a_to_b / c.total_packets) * 100 : 50;

                return (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2.5 px-3">
                      <Badge variant="protocol">{c.protocol}</Badge>
                    </td>
                    <td className="py-2.5 px-3 text-cyan-400 font-semibold">
                      {c.endpoint_a} {c.port_a ? <span className="text-slate-500 text-[11px]">:{c.port_a}</span> : ''}
                    </td>
                    <td className="py-2.5 px-2 text-center text-slate-500">
                      <ArrowRightLeft size={12} />
                    </td>
                    <td className="py-2.5 px-3 text-slate-200 font-semibold">
                      {c.endpoint_b} {c.port_b ? <span className="text-slate-500 text-[11px]">:{c.port_b}</span> : ''}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <div className="text-[11px] text-slate-400">
                        {c.packets_a_to_b} / {c.packets_b_to_a}
                      </div>
                      <div className="w-24 h-1.5 ml-auto mt-1 rounded-full bg-slate-800 overflow-hidden flex">
                        <div className="bg-cyan-500 h-full" style={{ width: `${ratioA}%` }} />
                        <div className="bg-blue-500 h-full" style={{ width: `${100 - ratioA}%` }} />
                      </div>
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-slate-100">
                      {c.total_packets.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-300">
                      {(c.total_bytes / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-slate-400">
                      {c.duration.toFixed(3)}s
                    </td>
                  </tr>
                );
              })}

              {conversations.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500 italic">
                    No conversation flows detected.
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
