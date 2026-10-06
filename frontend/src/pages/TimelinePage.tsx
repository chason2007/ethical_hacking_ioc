import React, { useEffect, useState } from 'react';
import { Clock } from 'lucide-react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  Tooltip, CartesianGrid, Legend, AreaChart, Area
} from 'recharts';
import { api } from '../services/api';
import type { Capture, TimelinePoint } from '../types';

interface TimelinePageProps {
  capture: Capture | null;
}

export const TimelinePage: React.FC<TimelinePageProps> = ({ capture }) => {
  const [timelineData, setTimelineData] = useState<TimelinePoint[]>([]);
  const [metric, setMetric] = useState<'packets' | 'bytes'>('packets');
  const [selectedProtocols, setSelectedProtocols] = useState<Record<string, boolean>>({
    tcp: true,
    udp: true,
    icmp: true,
    dns: true,
    http: true,
  });

  useEffect(() => {
    if (!capture) return;
    api.getTimeline(capture.id)
      .then((data: TimelinePoint[]) => setTimelineData(data))
      .catch((err: any) => console.error('Failed to load timeline telemetry:', err));
  }, [capture]);

  if (!capture) {
    return <div className="p-8 text-center text-slate-500">No capture selected.</div>;
  }

  const toggleProto = (proto: string) => {
    setSelectedProtocols((prev) => ({ ...prev, [proto]: !prev[proto] }));
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Clock size={20} className="text-cyan-400" />
            Traffic Timeline & Telemetry Series
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Temporal packet distribution tracking throughput bursts, connection floods, and protocol concurrency.
          </p>
        </div>

        {/* Metric Selector (Packets vs Bytes) */}
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
            <button
              onClick={() => setMetric('packets')}
              className={`px-3 py-1 rounded transition-colors cursor-pointer ${
                metric === 'packets' ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Packet Counts
            </button>
            <button
              onClick={() => setMetric('bytes')}
              className={`px-3 py-1 rounded transition-colors cursor-pointer ${
                metric === 'bytes' ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Byte Volume
            </button>
          </div>
        </div>
      </div>

      {/* Protocol Toggle Buttons */}
      <div className="flex flex-wrap items-center gap-2 p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
        <span className="text-slate-400 font-semibold mr-1">Filter Series:</span>
        {[
          { id: 'tcp', label: 'TCP / TLS', color: '#06b6d4' },
          { id: 'udp', label: 'UDP', color: '#3b82f6' },
          { id: 'icmp', label: 'ICMP', color: '#f59e0b' },
          { id: 'dns', label: 'DNS', color: '#10b981' },
          { id: 'http', label: 'HTTP', color: '#ec4899' },
        ].map((p) => {
          const active = selectedProtocols[p.id];
          return (
            <button
              key={p.id}
              onClick={() => toggleProto(p.id)}
              className={`px-2.5 py-1 rounded-md font-mono text-[11px] transition-all flex items-center gap-1.5 border cursor-pointer ${
                active
                  ? 'bg-slate-950 text-slate-200 border-slate-700'
                  : 'bg-slate-950/40 text-slate-500 border-slate-800/60 line-through'
              }`}
            >
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: active ? p.color : '#475569' }} />
              <span>{p.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Timeline Chart */}
      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            {metric === 'bytes' ? (
              <AreaChart data={timelineData} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
                <defs>
                  <linearGradient id="colorBytes" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time_label" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: '#06b6d4' }}
                  formatter={(val: any) => [`${(val / 1024).toFixed(2)} KB`, 'Volume']}
                />
                <Area type="monotone" dataKey="byte_count" stroke="#06b6d4" fillOpacity={1} fill="url(#colorBytes)" />
              </AreaChart>
            ) : (
              <LineChart data={timelineData} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time_label" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                {selectedProtocols.tcp && (
                  <Line type="monotone" dataKey="tcp_count" name="TCP / TLS" stroke="#06b6d4" strokeWidth={2} dot={false} />
                )}
                {selectedProtocols.udp && (
                  <Line type="monotone" dataKey="udp_count" name="UDP" stroke="#3b82f6" strokeWidth={2} dot={false} />
                )}
                {selectedProtocols.icmp && (
                  <Line type="monotone" dataKey="icmp_count" name="ICMP" stroke="#f59e0b" strokeWidth={2} dot={false} />
                )}
                {selectedProtocols.dns && (
                  <Line type="monotone" dataKey="dns_count" name="DNS" stroke="#10b981" strokeWidth={2} dot={false} />
                )}
                {selectedProtocols.http && (
                  <Line type="monotone" dataKey="http_count" name="HTTP" stroke="#ec4899" strokeWidth={2} dot={false} />
                )}
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};
