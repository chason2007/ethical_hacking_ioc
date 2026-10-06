import React, { useEffect, useState } from 'react';
import { Network, Lock } from 'lucide-react';
import { api } from '../services/api';
import type { Capture, ProtocolStat, DNSAnalysis, HTTPAnalysis, DNSRecord, HTTPRecord } from '../types';
import { Badge } from '../components/common/Badge';
import { EduCard } from '../components/common/EduCard';

interface ProtocolsPageProps {
  capture: Capture | null;
}

export const ProtocolsPage: React.FC<ProtocolsPageProps> = ({ capture }) => {
  const [protocols, setProtocols] = useState<ProtocolStat[]>([]);
  const [dnsData, setDnsData] = useState<DNSAnalysis | null>(null);
  const [httpData, setHttpData] = useState<HTTPAnalysis | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'dns' | 'http'>('overview');

  useEffect(() => {
    if (!capture) return;

    Promise.all([
      api.getProtocols(capture.id),
      api.getDNS(capture.id),
      api.getHTTP(capture.id),
    ])
      .then(([protos, dns, http]) => {
        setProtocols(protos);
        setDnsData(dns);
        setHttpData(http);
      })
      .catch((err) => console.error('Error fetching protocol data:', err));
  }, [capture]);

  if (!capture) {
    return <div className="p-8 text-center text-slate-500">No capture selected.</div>;
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Network size={20} className="text-cyan-400" />
            Protocol-Specific Analysis
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Detailed layer breakdown for Ethernet, IPv4, TCP, UDP, ICMP, DNS, and HTTP/TLS inspection.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1 rounded-lg text-xs">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-3 py-1.5 rounded-md transition-colors cursor-pointer ${
              activeTab === 'overview' ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Protocol Hierarchy
          </button>
          <button
            onClick={() => setActiveTab('dns')}
            className={`px-3 py-1.5 rounded-md transition-colors cursor-pointer ${
              activeTab === 'dns' ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            DNS Forensics
          </button>
          <button
            onClick={() => setActiveTab('http')}
            className={`px-3 py-1.5 rounded-md transition-colors cursor-pointer ${
              activeTab === 'http' ? 'bg-cyan-600 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            HTTP & TLS
          </button>
        </div>
      </div>

      {/* VIEW 1: Hierarchy Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          
          {/* Protocol Distribution Table */}
          <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Protocol Breakdown & Traffic Volume</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                    <th className="py-2.5 px-3">Protocol</th>
                    <th className="py-2.5 px-3">OSI Layer</th>
                    <th className="py-2.5 px-3 text-right">Packets Count</th>
                    <th className="py-2.5 px-3 text-right">Byte Volume</th>
                    <th className="py-2.5 px-3 text-right">Share (%)</th>
                    <th className="py-2.5 px-4">Bandwidth Proportion</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {protocols.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-2.5 px-3 font-bold text-cyan-400">{p.protocol_name}</td>
                      <td className="py-2.5 px-3 text-slate-400">{p.layer}</td>
                      <td className="py-2.5 px-3 text-right">{p.packet_count.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right text-slate-300">{(p.byte_count / 1024).toFixed(1)} KB</td>
                      <td className="py-2.5 px-3 text-right font-semibold text-slate-200">{p.percentage.toFixed(1)}%</td>
                      <td className="py-2.5 px-4 w-48">
                        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                            style={{ width: `${Math.min(p.percentage, 100)}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Educational Protocol Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <EduCard title="TCP (Transmission Control Protocol)" category="Transport Layer 4" icon="book">
              <p>
                Connection-oriented, reliable protocol providing ordered flow control via sequence/acknowledgment numbers. Uses flags (SYN, ACK, FIN, RST, PSH, URG) to manage sessions.
              </p>
            </EduCard>

            <EduCard title="UDP (User Datagram Protocol)" category="Transport Layer 4" icon="book">
              <p>
                Connectionless, lightweight protocol without delivery guarantees or retransmission. Commonly utilized by latency-sensitive services like DNS (53), DHCP (67/68), and NTP (123).
              </p>
            </EduCard>

            <EduCard title="ICMP (Diagnostics & Control)" category="Network Layer 3" icon="book">
              <p>
                Used for network operational feedback (Echo Request Type 8, Echo Reply Type 0, Destination Unreachable Type 3). Exploited in reconnaissance via ping sweeps.
              </p>
            </EduCard>
          </div>

        </div>
      )}

      {/* VIEW 2: DNS Forensics */}
      {activeTab === 'dns' && (
        <div className="space-y-6">
          
          {/* Top DNS Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-xs text-slate-400">Total Queries</div>
              <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
                {dnsData?.total_queries ?? 0}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-xs text-slate-400">Total Responses</div>
              <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                {dnsData?.total_responses ?? 0}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-xs text-slate-400">Unique Queried Domains</div>
              <div className="text-xl font-bold font-mono text-indigo-400 mt-1">
                {dnsData?.unique_domains ?? 0}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-xs text-slate-400">Anomalous Queries</div>
              <div className="text-xl font-bold font-mono text-amber-400 mt-1">
                {dnsData?.anomalous_queries.length ?? 0}
              </div>
            </div>
          </div>

          {/* Queried Domains & Anomalies */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Top Domains */}
            <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-5 space-y-3">
              <h3 className="text-sm font-semibold text-slate-200">Most Frequently Queried Hostnames</h3>
              <div className="divide-y divide-slate-800/60 font-mono text-xs">
                {dnsData?.top_domains.map((td: { domain: string; count: number }, idx: number) => (
                  <div key={idx} className="py-2.5 flex items-center justify-between">
                    <span className="text-cyan-400 truncate max-w-[80%]">{td.domain}</span>
                    <Badge variant="protocol">{td.count} queries</Badge>
                  </div>
                ))}
                {dnsData?.top_domains.length === 0 && (
                  <div className="py-8 text-center text-slate-500 italic">No DNS queries recorded in capture.</div>
                )}
              </div>
            </div>

            {/* Anomalous DNS Records */}
            <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-5 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-200">Flagged DNS Inquiries</h3>
                <span className="text-[10px] text-amber-400 font-mono uppercase">Tunneling & DGA Heuristics</span>
              </div>
              
              <div className="space-y-2.5 font-mono text-xs">
                {dnsData?.anomalous_queries.map((aq: DNSRecord) => (
                  <div key={aq.id} className="p-3 rounded-lg bg-amber-950/20 border border-amber-800/40 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-amber-300 font-bold truncate max-w-[70%]">{aq.query_name}</span>
                      <Badge variant="medium">{aq.query_type}</Badge>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Reason: <span className="text-slate-300">{aq.anomaly_reason}</span>
                    </div>
                  </div>
                ))}

                {dnsData?.anomalous_queries.length === 0 && (
                  <div className="py-8 text-center text-slate-500 italic">No suspicious DNS queries flagged.</div>
                )}
              </div>
            </div>

          </div>

          <EduCard title="DNS Tunneling & DGA Educational Context" category="Threat Analysis" icon="shield">
            <p>
              DNS relies primarily on UDP port 53. Because corporate egress firewalls typically permit outbound DNS to resolve IP addresses, threat actors frequently weaponize DNS queries to encode exfiltrated data or command-and-control beacons inside oversized subdomains (e.g. Base64 chunks).
            </p>
          </EduCard>

        </div>
      )}

      {/* VIEW 3: HTTP & TLS */}
      {activeTab === 'http' && (
        <div className="space-y-6">
          
          <div className="p-4 rounded-xl border border-cyan-900/30 bg-cyan-950/20 text-xs text-slate-300 flex items-start gap-3">
            <Lock size={18} className="text-cyan-400 mt-0.5 shrink-0" />
            <div>
              <span className="font-semibold text-cyan-300">HTTPS / TLS Cryptographic Boundary Notice:</span>
              <p className="mt-0.5 text-slate-400">
                In modern network security, HTTPS encrypts application-layer HTTP payloads using TLS session keys. Defensive packet analysis can safely inspect unencrypted handshake metadata (SNI server names, cipher suites, TLS version) without attempting unauthorized decryption. Cleartext HTTP (port 80) exposes complete headers and URIs.
              </p>
            </div>
          </div>

          {/* HTTP Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <h3 className="text-sm font-semibold text-slate-200">HTTP Methods Observed</h3>
              <div className="flex flex-wrap gap-2">
                {httpData && Object.entries(httpData.methods).map(([method, count]) => (
                  <div key={method} className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs">
                    <span className="text-cyan-400 font-bold">{method}:</span> <span className="text-slate-200">{Number(count)}</span>
                  </div>
                ))}
                {httpData && Object.keys(httpData.methods).length === 0 && (
                  <span className="text-xs text-slate-500 italic">No cleartext HTTP request methods recorded.</span>
                )}
              </div>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <h3 className="text-sm font-semibold text-slate-200">Observed Web Hosts & SNI Identifiers</h3>
              <div className="space-y-1.5 font-mono text-xs">
                {httpData?.top_hosts.map((th: { host: string; count: number }, idx: number) => (
                  <div key={idx} className="flex items-center justify-between py-1 border-b border-slate-800/40">
                    <span className="text-slate-200 truncate max-w-[80%]">{th.host}</span>
                    <Badge variant="protocol">{th.count}</Badge>
                  </div>
                ))}
                {httpData?.top_hosts.length === 0 && (
                  <span className="text-xs text-slate-500 italic">No HTTP hosts or TLS SNI names observed.</span>
                )}
              </div>
            </div>

          </div>

          {/* HTTP / TLS Records Table */}
          <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-5 space-y-3">
            <h3 className="text-sm font-semibold text-slate-200">HTTP & TLS Session Log</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                    <th className="py-2 px-3">Packet #</th>
                    <th className="py-2 px-3">Type</th>
                    <th className="py-2 px-3">Method / Code</th>
                    <th className="py-2 px-3">Host / SNI</th>
                    <th className="py-2 px-3">URI / Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {httpData?.records.map((r: HTTPRecord) => (
                    <tr key={r.id} className="hover:bg-slate-800/40">
                      <td className="py-2 px-3 text-slate-500">#{r.packet_number}</td>
                      <td className="py-2 px-3">
                        <Badge variant="protocol">{r.traffic_type}</Badge>
                      </td>
                      <td className="py-2 px-3 font-bold text-cyan-400">
                        {r.method || r.status_code || r.tls_version || '-'}
                      </td>
                      <td className="py-2 px-3 text-slate-200 truncate max-w-[200px]">{r.host || r.tls_sni || '-'}</td>
                      <td className="py-2 px-3 text-slate-400 truncate max-w-[320px]">{r.uri || r.status_phrase || '-'}</td>
                    </tr>
                  ))}
                  {httpData?.records.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-slate-500 italic">No web records recorded.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
