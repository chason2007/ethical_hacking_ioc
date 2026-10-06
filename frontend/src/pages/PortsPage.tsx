import React, { useEffect, useState } from 'react';
import { Radio } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { api } from '../services/api';
import type { Capture, PortStat } from '../types';
import { Badge } from '../components/common/Badge';
import { EduCard } from '../components/common/EduCard';

interface PortsPageProps {
  capture: Capture | null;
}

export const PortsPage: React.FC<PortsPageProps> = ({ capture }) => {
  const [ports, setPorts] = useState<PortStat[]>([]);

  useEffect(() => {
    if (!capture) return;
    api.getPorts(capture.id)
      .then((data: PortStat[]) => setPorts(data))
      .catch((err: any) => console.error('Failed to load port stats:', err));
  }, [capture]);

  if (!capture) {
    return <div className="p-8 text-center text-slate-500">No capture selected.</div>;
  }

  const chartData = ports.slice(0, 10).map((p) => ({
    port: `Port ${p.port}`,
    packets: p.packet_count,
    service: p.common_service,
  }));

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Radio size={20} className="text-cyan-400" />
            Port Analysis & Service Correlation
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Transport port frequency mapping, standard IANA service associations, and reconnaissance detection.
          </p>
        </div>
      </div>

      {/* Top Ports Visualization */}
      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
        <h3 className="text-sm font-semibold text-slate-200">Top Contacted Ports</h3>
        <div className="h-60">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="port" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                itemStyle={{ color: '#06b6d4' }}
                formatter={(val: any, _, item: any) => [`${val} pkts (${item.payload.service})`, 'Traffic']}
              />
              <Bar dataKey="packets" fill="#06b6d4" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Ports Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-[11px]">
              <tr>
                <th className="py-2.5 px-4 w-28">Port Number</th>
                <th className="py-2.5 px-3 w-28">Protocol</th>
                <th className="py-2.5 px-4 w-44">Associated Service</th>
                <th className="py-2.5 px-3 text-right w-28">Packets</th>
                <th className="py-2.5 px-3 text-right w-32">Bytes</th>
                <th className="py-2.5 px-4">Service & Security Context</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {ports.map((p) => {
                const isCleartext = [21, 23, 80].includes(p.port);
                const isSensitive = [22, 443, 3389, 1433, 3306, 5432].includes(p.port);

                return (
                  <tr key={p.port} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-bold text-cyan-400">{p.port}</td>
                    <td className="py-3 px-3">
                      <Badge variant="protocol">{p.protocol}</Badge>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`font-semibold ${isCleartext ? 'text-amber-400' : isSensitive ? 'text-indigo-400' : 'text-slate-200'}`}>
                        {p.common_service}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">{p.packet_count.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right text-slate-400">
                      {(p.byte_count / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px] font-sans">
                      {p.description}
                    </td>
                  </tr>
                );
              })}

              {ports.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 italic">
                    No port telemetry recorded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <EduCard title="Defensive Service Identification Disclaimer" category="Academic Primer" icon="shield">
        <p>
          In network security, a port number does not definitively prove the underlying service is executing. Attackers frequently host malicious backdoors or command-and-control proxies on standard ports (e.g. 80, 443, 53) to blend in with legitimate traffic. Defensive protocol inspection requires verifying application layer handshakes, headers, and protocol compliance rather than trusting port numbers alone.
        </p>
      </EduCard>

    </div>
  );
};
