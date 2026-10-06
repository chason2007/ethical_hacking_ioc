import type {
  Capture, Packet, PacketPage,
  Endpoint, Conversation, ProtocolStat, PortStat,
  DNSAnalysis, HTTPAnalysis, SecurityOverview,
  TimelinePoint, CaptureStatistics
} from '../types';

const API_BASE = '/api';

export const api = {
  // Captures
  async getCaptures(): Promise<Capture[]> {
    const res = await fetch(`${API_BASE}/captures`);
    if (!res.ok) throw new Error('Failed to fetch captures');
    return res.json();
  },

  async getCapture(id: string): Promise<Capture> {
    const res = await fetch(`${API_BASE}/captures/${id}`);
    if (!res.ok) throw new Error('Failed to fetch capture metadata');
    return res.json();
  },

  async loadDemoCapture(): Promise<Capture> {
    const res = await fetch(`${API_BASE}/captures/demo`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to initialize demo capture');
    return res.json();
  },

  async uploadCapture(file: File): Promise<Capture> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/captures/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload error' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async deleteCapture(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/captures/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete capture');
  },

  // Packets
  async getPackets(
    captureId: string,
    params: {
      page?: number;
      page_size?: number;
      protocol?: string;
      source_ip?: string;
      destination_ip?: string;
      port?: number;
      search?: string;
      sort_by?: string;
      sort_dir?: string;
    } = {}
  ): Promise<PacketPage> {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page.toString());
    if (params.page_size) query.append('page_size', params.page_size.toString());
    if (params.protocol) query.append('protocol', params.protocol);
    if (params.source_ip) query.append('source_ip', params.source_ip);
    if (params.destination_ip) query.append('destination_ip', params.destination_ip);
    if (params.port) query.append('port', params.port.toString());
    if (params.search) query.append('search', params.search);
    if (params.sort_by) query.append('sort_by', params.sort_by);
    if (params.sort_dir) query.append('sort_dir', params.sort_dir);

    const res = await fetch(`${API_BASE}/captures/${captureId}/packets?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch packets');
    return res.json();
  },

  async getPacketDetail(captureId: string, packetNumber: number): Promise<Packet> {
    const res = await fetch(`${API_BASE}/captures/${captureId}/packets/${packetNumber}`);
    if (!res.ok) throw new Error(`Failed to fetch packet #${packetNumber}`);
    return res.json();
  },

  // Traffic Analysis
  async getStatistics(captureId: string): Promise<CaptureStatistics> {
    const res = await fetch(`${API_BASE}/captures/${captureId}/statistics`);
    if (!res.ok) throw new Error('Failed to fetch statistics');
    return res.json();
  },

  async getProtocols(captureId: string): Promise<ProtocolStat[]> {
    const res = await fetch(`${API_BASE}/captures/${captureId}/protocols`);
    if (!res.ok) throw new Error('Failed to fetch protocol breakdown');
    return res.json();
  },

  async getConversations(captureId: string, sortBy: string = 'packets'): Promise<Conversation[]> {
    const query = new URLSearchParams({ sort_by: sortBy });
    const res = await fetch(`${API_BASE}/captures/${captureId}/conversations?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch conversations');
    return res.json();
  },

  async getEndpoints(captureId: string, addressType?: string, isPrivate?: boolean): Promise<Endpoint[]> {
    const query = new URLSearchParams();
    if (addressType) query.append('address_type', addressType);
    if (isPrivate !== undefined) query.append('is_private', isPrivate.toString());

    const res = await fetch(`${API_BASE}/captures/${captureId}/endpoints?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch endpoints');
    return res.json();
  },

  async getPorts(captureId: string): Promise<PortStat[]> {
    const res = await fetch(`${API_BASE}/captures/${captureId}/ports`);
    if (!res.ok) throw new Error('Failed to fetch port statistics');
    return res.json();
  },

  // DNS & HTTP
  async getDNS(captureId: string): Promise<DNSAnalysis> {
    const res = await fetch(`${API_BASE}/captures/${captureId}/dns`);
    if (!res.ok) throw new Error('Failed to fetch DNS analysis');
    return res.json();
  },

  async getHTTP(captureId: string): Promise<HTTPAnalysis> {
    const res = await fetch(`${API_BASE}/captures/${captureId}/http`);
    if (!res.ok) throw new Error('Failed to fetch HTTP/TLS analysis');
    return res.json();
  },

  // Security Insights
  async getSecurity(captureId: string, severity?: string, category?: string): Promise<SecurityOverview> {
    const query = new URLSearchParams();
    if (severity) query.append('severity', severity);
    if (category) query.append('category', category);

    const res = await fetch(`${API_BASE}/captures/${captureId}/security?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch security insights');
    return res.json();
  },

  // Timeline
  async getTimeline(captureId: string): Promise<TimelinePoint[]> {
    const res = await fetch(`${API_BASE}/captures/${captureId}/timeline`);
    if (!res.ok) throw new Error('Failed to fetch timeline telemetry');
    return res.json();
  },

  // Health
  async getHealth(): Promise<{ status: string; uptime_seconds: number; version: string }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('System health check failed');
    return res.json();
  },

  // URLs for Direct Downloads
  getReportUrl(captureId: string): string {
    return `${API_BASE}/captures/${captureId}/report`;
  },

  getExportCsvUrl(captureId: string, protocol?: string): string {
    const q = protocol ? `?protocol=${encodeURIComponent(protocol)}` : '';
    return `${API_BASE}/captures/${captureId}/export/csv${q}`;
  },

  getExportJsonUrl(captureId: string): string {
    return `${API_BASE}/captures/${captureId}/export/json`;
  },
};
