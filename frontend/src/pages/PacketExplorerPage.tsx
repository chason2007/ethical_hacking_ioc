import React, { useEffect, useState } from 'react';
import {
  Search, ChevronLeft, ChevronRight, Layers,
  ArrowUpDown, SlidersHorizontal, RefreshCw, Eye
} from 'lucide-react';
import { api } from '../services/api';
import type { Capture, Packet, PacketPage } from '../types';
import { Badge } from '../components/common/Badge';
import { PacketInspectorModal } from '../components/packets/PacketInspectorModal';

interface PacketExplorerPageProps {
  capture: Capture | null;
}

export const PacketExplorerPage: React.FC<PacketExplorerPageProps> = ({ capture }) => {
  const [packetData, setPacketData] = useState<PacketPage | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [protocolFilter, setProtocolFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [srcIpFilter, setSrcIpFilter] = useState('');
  const [dstIpFilter, setDstIpFilter] = useState('');
  const [portFilter, setPortFilter] = useState('');
  const [sortBy, setSortBy] = useState('packet_number');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [loading, setLoading] = useState(false);
  const [selectedPacket, setSelectedPacket] = useState<Packet | null>(null);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  const fetchPackets = () => {
    if (!capture) return;
    setLoading(true);

    api.getPackets(capture.id, {
      page,
      page_size: pageSize,
      protocol: protocolFilter === 'ALL' ? undefined : protocolFilter,
      source_ip: srcIpFilter || undefined,
      destination_ip: dstIpFilter || undefined,
      port: portFilter ? parseInt(portFilter) : undefined,
      search: searchQuery || undefined,
      sort_by: sortBy,
      sort_dir: sortDir,
    })
      .then((data) => setPacketData(data))
      .catch((err) => console.error('Failed to load packets:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    setPage(1);
  }, [capture, protocolFilter, searchQuery, srcIpFilter, dstIpFilter, portFilter, sortBy, sortDir]);

  useEffect(() => {
    fetchPackets();
  }, [capture, page, pageSize, protocolFilter, searchQuery, srcIpFilter, dstIpFilter, portFilter, sortBy, sortDir]);

  const handlePacketClick = async (pkt: Packet) => {
    if (!capture) return;
    try {
      const fullPkt = await api.getPacketDetail(capture.id, pkt.packet_number);
      setSelectedPacket(fullPkt);
    } catch {
      setSelectedPacket(pkt);
    }
  };

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortDir('asc');
    }
  };

  const protocolsList = ['ALL', 'TCP', 'UDP', 'ICMP', 'DNS', 'HTTP', 'TLS', 'ARP'];

  return (
    <div className="p-6 space-y-4 max-w-7xl mx-auto flex flex-col h-[calc(100vh-3.5rem)]">
      
      {/* Title & Quick Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Layers size={20} className="text-cyan-400" />
            Packet Explorer
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Interactive packet grid with protocol decoding, header filtering, and Wireshark-compatible deep inspection.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border flex items-center gap-1.5 transition-colors cursor-pointer ${
              showAdvancedFilters
                ? 'bg-cyan-950/60 border-cyan-800 text-cyan-300'
                : 'bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800'
            }`}
          >
            <SlidersHorizontal size={13} />
            <span>Filter Builder</span>
          </button>

          <button
            onClick={fetchPackets}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors cursor-pointer"
            title="Refresh packet table"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3 shrink-0">
        <div className="flex flex-wrap items-center gap-2">
          
          {/* Global search */}
          <div className="relative flex-1 min-w-[240px]">
            <Search size={14} className="absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search info, IP, port, flags (e.g. protocol:tcp or 192.168.1.1)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 outline-hidden focus:border-cyan-500"
            />
          </div>

          {/* Quick Protocol Pills */}
          <div className="flex items-center gap-1 overflow-x-auto">
            {protocolsList.map((proto) => (
              <button
                key={proto}
                onClick={() => setProtocolFilter(proto)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-mono transition-colors cursor-pointer ${
                  protocolFilter === proto
                    ? 'bg-cyan-600 text-slate-950 font-bold'
                    : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {proto}
              </button>
            ))}
          </div>

        </div>

        {/* Visual Advanced Filter Builder */}
        {showAdvancedFilters && (
          <div className="pt-3 border-t border-slate-800/80 grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Source IP Address</label>
              <input
                type="text"
                placeholder="e.g. 192.168.1.50"
                value={srcIpFilter}
                onChange={(e) => setSrcIpFilter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono outline-hidden focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Destination IP Address</label>
              <input
                type="text"
                placeholder="e.g. 192.168.1.100"
                value={dstIpFilter}
                onChange={(e) => setDstIpFilter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono outline-hidden focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Port Number (Src or Dst)</label>
              <input
                type="number"
                placeholder="e.g. 80, 443, 53"
                value={portFilter}
                onChange={(e) => setPortFilter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono outline-hidden focus:border-cyan-500"
              />
            </div>
          </div>
        )}
      </div>

      {/* Packet Grid Table */}
      <div className="flex-1 rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden flex flex-col min-h-0">
        <div className="flex-1 overflow-auto">
          <table className="w-full text-left font-mono text-xs border-collapse">
            <thead className="sticky top-0 bg-slate-950 border-b border-slate-800 z-10 text-slate-400 text-[11px]">
              <tr>
                <th
                  onClick={() => handleSort('packet_number')}
                  className="py-2.5 px-3 cursor-pointer hover:text-slate-200 w-16 text-center"
                >
                  <div className="flex items-center justify-center gap-1">
                    <span>No.</span>
                    <ArrowUpDown size={11} />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('relative_time')}
                  className="py-2.5 px-3 cursor-pointer hover:text-slate-200 w-24"
                >
                  <div className="flex items-center gap-1">
                    <span>Time (s)</span>
                    <ArrowUpDown size={11} />
                  </div>
                </th>
                <th className="py-2.5 px-3 w-36">Source</th>
                <th className="py-2.5 px-3 w-36">Destination</th>
                <th
                  onClick={() => handleSort('protocol')}
                  className="py-2.5 px-3 cursor-pointer hover:text-slate-200 w-20 text-center"
                >
                  <div className="flex items-center justify-center gap-1">
                    <span>Protocol</span>
                    <ArrowUpDown size={11} />
                  </div>
                </th>
                <th className="py-2.5 px-2 w-20 text-right">Src Port</th>
                <th className="py-2.5 px-2 w-20 text-right">Dst Port</th>
                <th
                  onClick={() => handleSort('length')}
                  className="py-2.5 px-3 cursor-pointer hover:text-slate-200 w-20 text-right"
                >
                  <div className="flex items-center justify-end gap-1">
                    <span>Length</span>
                    <ArrowUpDown size={11} />
                  </div>
                </th>
                <th className="py-2.5 px-3 w-28">TCP Flags</th>
                <th className="py-2.5 px-3">Information Summary</th>
                <th className="py-2.5 px-2 w-12 text-center">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40 text-slate-300">
              {packetData?.items.map((pkt) => {
                const isSelected = selectedPacket?.packet_number === pkt.packet_number;
                const isScanSyn = pkt.tcp_flags === 'SYN';
                const isRst = pkt.tcp_flags?.includes('RST');

                return (
                  <tr
                    key={pkt.id}
                    onClick={() => handlePacketClick(pkt)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-cyan-950/70 border-l-2 border-cyan-400'
                        : isRst
                        ? 'hover:bg-amber-950/30'
                        : isScanSyn
                        ? 'hover:bg-slate-800/70'
                        : 'hover:bg-slate-800/40'
                    }`}
                  >
                    <td className="py-2 px-3 text-slate-500 text-center">{pkt.packet_number}</td>
                    <td className="py-2 px-3 text-slate-400">{pkt.relative_time.toFixed(4)}</td>
                    <td className="py-2 px-3 text-cyan-400/90 truncate max-w-[140px]">{pkt.source_ip || pkt.source_mac || '-'}</td>
                    <td className="py-2 px-3 text-slate-300 truncate max-w-[140px]">{pkt.destination_ip || pkt.destination_mac || '-'}</td>
                    <td className="py-2 px-3 text-center">
                      <Badge variant="protocol">{pkt.protocol}</Badge>
                    </td>
                    <td className="py-2 px-2 text-right text-slate-400">{pkt.source_port ?? '-'}</td>
                    <td className="py-2 px-2 text-right text-slate-400">{pkt.destination_port ?? '-'}</td>
                    <td className="py-2 px-3 text-right font-medium text-slate-300">{pkt.length}</td>
                    <td className="py-2 px-3">
                      {pkt.tcp_flags ? (
                        <span
                          className={`text-[11px] font-bold ${
                            pkt.tcp_flags.includes('RST')
                              ? 'text-amber-400'
                              : pkt.tcp_flags === 'SYN'
                              ? 'text-cyan-400'
                              : 'text-slate-400'
                          }`}
                        >
                          [{pkt.tcp_flags}]
                        </span>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>
                    <td className="py-2 px-3 text-slate-300 truncate max-w-[340px]" title={pkt.info}>
                      {pkt.info || '-'}
                    </td>
                    <td className="py-2 px-2 text-center text-slate-500 hover:text-cyan-400">
                      <Eye size={13} />
                    </td>
                  </tr>
                );
              })}

              {packetData?.items.length === 0 && (
                <tr>
                  <td colSpan={11} className="py-12 text-center text-slate-500 italic">
                    No packets match the current query or filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="px-4 py-2.5 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 shrink-0">
          <div className="flex items-center gap-4">
            <span>
              Showing packets <strong className="text-slate-200 font-mono">{packetData ? (page - 1) * pageSize + 1 : 0}</strong> -{' '}
              <strong className="text-slate-200 font-mono">
                {packetData ? Math.min(page * pageSize, packetData.total) : 0}
              </strong>{' '}
              of <strong className="text-cyan-400 font-mono">{packetData?.total.toLocaleString() ?? 0}</strong>
            </span>

            <div className="flex items-center gap-1.5 font-sans">
              <span>Per page:</span>
              <select
                aria-label="Packets per page"
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
                className="bg-slate-900 border border-slate-800 rounded px-2 py-0.5 text-xs text-slate-300 outline-hidden font-mono cursor-pointer"
              >
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
                <option value={200}>200</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(page - 1, 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 transition-colors cursor-pointer"
            >
              <ChevronLeft size={14} />
            </button>
            <span className="font-mono text-slate-300 px-2">
              Page {page} of {packetData?.total_pages || 1}
            </span>
            <button
              onClick={() => setPage(Math.min(page + 1, packetData?.total_pages || 1))}
              disabled={page >= (packetData?.total_pages || 1)}
              className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 transition-colors cursor-pointer"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>

      </div>

      {/* Packet Inspector Modal */}
      <PacketInspectorModal
        packet={selectedPacket}
        onClose={() => setSelectedPacket(null)}
      />

    </div>
  );
};
