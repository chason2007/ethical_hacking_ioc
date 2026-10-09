import React, { useEffect, useState } from 'react';
import {
  Activity, Server, Users, Network, Clock, ShieldAlert,
  ArrowUpRight, HardDrive, Layers
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';
import { api } from '../services/api';
import type { Capture, CaptureStatistics, ProtocolStat, SecurityOverview, Endpoint } from '../types';
import { Badge } from '../components/common/Badge';
import { TimelinePage } from './TimelinePage';

interface DashboardPageProps {
  capture: Capture | null;
  onNavigateTab: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ capture, onNavigateTab }) => {
  const [viewMode, setViewMode] = useState<'overview' | 'timeline'>('overview');
  const [stats, setStats] = useState<CaptureStatistics | null>(null);
  const [protocols, setProtocols] = useState<ProtocolStat[]>([]);
  const [security, setSecurity] = useState<SecurityOverview | null>(null);
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);

  useEffect(() => {
    if (!capture) return;

    Promise.all([
      api.getStatistics(capture.id),
      api.getProtocols(capture.id),
      api.getSecurity(capture.id),
      api.getEndpoints(capture.id),
    ])
      .then(([s, p, sec, ep]) => {
        setStats(s);
        setProtocols(p);
        setSecurity(sec);
        setEndpoints(ep);
      })
      .catch((err) => console.error('Error loading dashboard data:', err));
  }, [capture]);

  if (!capture) {
    return (
      <div className="p-8 text-center text-slate-500">
        <Activity size={32} className="mx-auto mb-2 text-slate-600" />
        <p>No packet capture selected. Please upload or load a demo capture.</p>
      </div>
    );
  }

  const PROTO_COLORS = ['#06b6d4', '#0284c7', '#3b82f6', '#6366f1', '#8b5cf6', '#ec4899', '#10b981'];

  // Size distribution data for chart
  const sizeChartData = stats
    ? Object.entries(stats.packet_size_buckets).map(([bucket, count]) => ({
        bucket,
        count,
      }))
    : [];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-100">Forensics Security Dashboard</h1>
            <Badge variant="default">{capture.filename}</Badge>
            {capture.is_demo === 1 && <Badge variant="protocol">SYNTHETIC DEMO</Badge>}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Defensive deep packet inspection metrics, protocol hierarchy distribution, and heuristic security indicators.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs">
            <button
              onClick={() => setViewMode('overview')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                viewMode === 'overview'
                  ? 'bg-cyan-600 text-slate-950 font-semibold shadow-xs'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              📊 Overview
            </button>
            <button
              onClick={() => setViewMode('timeline')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                viewMode === 'timeline'
                  ? 'bg-cyan-600 text-slate-950 font-semibold shadow-xs'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              📈 Timeline
            </button>
          </div>

          <button
            onClick={() => onNavigateTab('packets')}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <Layers size={13} className="text-cyan-400" />
            <span>Packets</span>
          </button>
        </div>
      </div>

      {viewMode === 'timeline' ? (
        <TimelinePage capture={capture} />
      ) : (
        <>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Packets</span>
            <Activity size={14} className="text-cyan-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {stats ? stats.total_packets.toLocaleString() : '...'}
          </div>
          <div className="text-[10px] text-slate-500">Processed wire frames</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Volume</span>
            <HardDrive size={14} className="text-blue-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {stats ? `${(stats.total_bytes / 1024).toFixed(1)} KB` : '...'}
          </div>
          <div className="text-[10px] text-slate-500">
            Avg: {stats ? `${stats.avg_packet_size} B/pkt` : '...'}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Endpoints</span>
            <Server size={14} className="text-indigo-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {stats ? stats.unique_ips : '...'}
          </div>
          <div className="text-[10px] text-slate-500">Unique IP addresses</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Conversations</span>
            <Users size={14} className="text-emerald-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {stats ? stats.unique_conversations : '...'}
          </div>
          <div className="text-[10px] text-slate-500">Network flows</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Protocols</span>
            <Network size={14} className="text-cyan-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {stats ? stats.protocol_count : '...'}
          </div>
          <div className="text-[10px] text-slate-500">Distinct layer protocols</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Duration</span>
            <Clock size={14} className="text-amber-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {stats ? `${stats.duration_seconds.toFixed(2)}s` : '...'}
          </div>
          <div className="text-[10px] text-slate-500">Capture timeline</div>
        </div>
      </div>

      {/* Security Alerts Ribbon */}
      {security && security.findings.length > 0 && (
        <div className="p-4 rounded-xl border border-amber-900/40 bg-amber-950/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-950/80 border border-amber-800/80 text-amber-400">
              <ShieldAlert size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-amber-300">
                  {security.total_findings} Defensive Heuristic Indicator{security.total_findings > 1 ? 's' : ''} Detected
                </h3>
                <Badge variant="high">HIGH: {security.severity_counts.HIGH}</Badge>
                <Badge variant="medium">MED: {security.severity_counts.MEDIUM}</Badge>
                <Badge variant="low">LOW: {security.severity_counts.LOW}</Badge>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Top observation: <span className="text-slate-200">{security.findings[0]?.title}</span> &mdash; {security.findings[0]?.evidence}
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigateTab('security')}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 text-amber-300 transition-colors whitespace-nowrap cursor-pointer"
          >
            Review Evidence & Recommendations &rarr;
          </button>
        </div>
      )}

      {/* Main Visualizations: Protocols & Frame Sizes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Protocol Distribution Bar Chart */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Protocol Distribution</h3>
              <p className="text-[11px] text-slate-500">Packets breakdown by transport and application protocol</p>
            </div>
            <button
              onClick={() => onNavigateTab('protocols')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium cursor-pointer"
            >
              Details <ArrowUpRight size={13} />
            </button>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={protocols} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis dataKey="protocol_name" type="category" stroke="#94a3b8" tick={{ fontSize: 11, fontFamily: 'monospace' }} width={60} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: '#06b6d4' }}
                  formatter={(val: any) => [`${val} packets`, 'Count']}
                />
                <Bar dataKey="packet_count" radius={[0, 4, 4, 0]}>
                  {protocols.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={PROTO_COLORS[index % PROTO_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Packet Size Distribution */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Packet Size Distribution (MTU Profile)</h3>
            <p className="text-[11px] text-slate-500">Histogram of captured frame lengths in bytes</p>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sizeChartData} margin={{ top: 5, right: 20, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="bucket" stroke="#64748b" tick={{ fontSize: 10, angle: -15, textAnchor: 'end' }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: '#3b82f6' }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Top Active Endpoints Table */}
      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Most Active Network Endpoints</h3>
            <p className="text-[11px] text-slate-500">Top communication nodes ranked by total packets transferred</p>
          </div>
          <button
            onClick={() => onNavigateTab('traffic')}
            className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium cursor-pointer"
          >
            All Endpoints & Flows <ArrowUpRight size={13} />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="py-2.5 px-3">Endpoint Address</th>
                <th className="py-2.5 px-3">Scope</th>
                <th className="py-2.5 px-3 text-right">Packets Tx</th>
                <th className="py-2.5 px-3 text-right">Packets Rx</th>
                <th className="py-2.5 px-3 text-right">Total Volume</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {endpoints.slice(0, 6).map((ep) => (
                <tr key={ep.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-3 font-semibold text-cyan-400">{ep.address}</td>
                  <td className="py-2.5 px-3">
                    <Badge variant={ep.is_private ? 'info' : 'low'}>
                      {ep.is_private ? 'Private / RFC1918' : 'Public Internet'}
                    </Badge>
                  </td>
                  <td className="py-2.5 px-3 text-right">{ep.packets_sent.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right">{ep.packets_received.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right font-medium text-slate-200">
                    {(ep.total_bytes / 1024).toFixed(1)} KB
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      </>
      )}

    </div>
  );
};
