import React, { useEffect, useState } from 'react';
import { Server } from 'lucide-react';
import { api } from '../services/api';
import type { Capture, Endpoint } from '../types';
import { Badge } from '../components/common/Badge';

interface EndpointsPageProps {
  capture: Capture | null;
}

export const EndpointsPage: React.FC<EndpointsPageProps> = ({ capture }) => {
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [scopeFilter, setScopeFilter] = useState<string>('ALL');

  useEffect(() => {
    if (!capture) return;
    const addrType = typeFilter === 'ALL' ? undefined : typeFilter;
    const isPriv = scopeFilter === 'ALL' ? undefined : scopeFilter === 'PRIVATE';

    api.getEndpoints(capture.id, addrType, isPriv)
      .then((data) => setEndpoints(data))
      .catch((err) => console.error('Failed to load endpoints:', err));
  }, [capture, typeFilter, scopeFilter]);

  if (!capture) {
    return <div className="p-8 text-center text-slate-500">No capture selected.</div>;
  }

  const maxPackets = endpoints.length > 0 ? Math.max(...endpoints.map((e) => e.total_packets)) : 1;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Server size={20} className="text-cyan-400" />
            Network Endpoint Directory
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Active host endpoints classified by IP version, private RFC1918 scope, and directional packet volume.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Address Type */}
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
            {['ALL', 'IPv4', 'IPv6'].map((t) => (
              <button
                key={t}
                onClick={() => setTypeFilter(t)}
                className={`px-2.5 py-1 rounded transition-colors cursor-pointer ${
                  typeFilter === t ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Scope Filter */}
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
            {['ALL', 'PRIVATE', 'PUBLIC'].map((s) => (
              <button
                key={s}
                onClick={() => setScopeFilter(s)}
                className={`px-2.5 py-1 rounded transition-colors cursor-pointer ${
                  scopeFilter === s ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Endpoints Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-[11px]">
              <tr>
                <th className="py-2.5 px-4">Endpoint Address</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Network Scope</th>
                <th className="py-2.5 px-3 text-right">Packets Tx</th>
                <th className="py-2.5 px-3 text-right">Packets Rx</th>
                <th className="py-2.5 px-3 text-right">Total Bytes</th>
                <th className="py-2.5 px-4">Activity Share</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {endpoints.map((ep) => {
                const activityPct = Math.round((ep.total_packets / maxPackets) * 100);

                return (
                  <tr key={ep.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-bold text-cyan-400">
                      {ep.address}
                      {ep.hostname && <span className="text-[10px] text-slate-500 block">{ep.hostname}</span>}
                    </td>
                    <td className="py-3 px-3">
                      <Badge variant="default">{ep.address_type}</Badge>
                    </td>
                    <td className="py-3 px-3">
                      <Badge variant={ep.is_private ? 'info' : 'low'}>
                        {ep.is_private ? 'Internal / RFC1918' : 'Public Internet'}
                      </Badge>
                    </td>
                    <td className="py-3 px-3 text-right">{ep.packets_sent.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right">{ep.packets_received.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right font-medium text-slate-100">
                      {(ep.total_bytes / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-3 px-4 w-44">
                      <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                          style={{ width: `${activityPct}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}

              {endpoints.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 italic">
                    No matching network endpoints found.
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
