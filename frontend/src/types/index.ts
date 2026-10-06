export interface Capture {
  id: string;
  filename: string;
  file_size_bytes: number;
  packet_count: number;
  total_bytes: number;
  duration_seconds: number;
  start_time?: number;
  end_time?: number;
  status: string;
  error_message?: string;
  is_demo: number;
  created_at: string;
  findings_count?: number;
  protocols_count?: number;
}

export interface Packet {
  id: number;
  capture_id: string;
  packet_number: number;
  timestamp: number;
  relative_time: number;
  source_mac?: string;
  destination_mac?: string;
  eth_type?: string;
  ip_version?: number;
  source_ip?: string;
  destination_ip?: string;
  ip_ttl?: number;
  protocol: string;
  source_port?: number;
  destination_port?: number;
  tcp_flags?: string;
  tcp_seq?: number;
  tcp_ack?: number;
  tcp_window?: number;
  length: number;
  info?: string;
  layers_json?: string;
  payload_preview?: string;
}

export interface PacketLayer {
  layer: string;
  summary: string;
  fields: Record<string, any>;
}

export interface PacketPage {
  items: Packet[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Endpoint {
  id: number;
  capture_id: string;
  address: string;
  address_type: string;
  packets_sent: number;
  packets_received: number;
  bytes_sent: number;
  bytes_received: number;
  total_packets: number;
  total_bytes: number;
  is_private: boolean;
  hostname?: string;
}

export interface Conversation {
  id: number;
  capture_id: string;
  protocol: string;
  endpoint_a: string;
  endpoint_b: string;
  port_a?: number;
  port_b?: number;
  packets_a_to_b: number;
  packets_b_to_a: number;
  bytes_a_to_b: number;
  bytes_b_to_a: number;
  total_packets: number;
  total_bytes: number;
  start_time: number;
  end_time: number;
  duration: number;
}

export interface ProtocolStat {
  id: number;
  capture_id: string;
  protocol_name: string;
  layer: string;
  packet_count: number;
  byte_count: number;
  percentage: number;
}

export interface PortStat {
  port: number;
  protocol: string;
  packet_count: number;
  byte_count: number;
  common_service: string;
  description: string;
}

export interface DNSRecord {
  id: number;
  capture_id: string;
  packet_number: number;
  timestamp: number;
  query_id?: number;
  record_type: string;
  query_name: string;
  query_type: string;
  rcode?: string;
  response_data?: string;
  is_suspicious: boolean;
  anomaly_reason?: string;
}

export interface DNSAnalysis {
  total_queries: number;
  total_responses: number;
  unique_domains: number;
  query_type_counts: Record<string, number>;
  top_domains: { domain: string; count: number }[];
  anomalous_queries: DNSRecord[];
}

export interface HTTPRecord {
  id: number;
  capture_id: string;
  packet_number: number;
  timestamp: number;
  traffic_type: string;
  method?: string;
  host?: string;
  uri?: string;
  status_code?: number;
  status_phrase?: string;
  user_agent?: string;
  content_type?: string;
  server?: string;
  tls_version?: string;
  tls_sni?: string;
}

export interface HTTPAnalysis {
  http_count: number;
  tls_count: number;
  methods: Record<string, number>;
  status_codes: Record<string, number>;
  top_hosts: { host: string; count: number }[];
  user_agents: string[];
  records: HTTPRecord[];
}

export interface SecurityFinding {
  id: number;
  capture_id: string;
  title: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW' | 'INFORMATIONAL';
  category: string;
  evidence: string;
  packets_involved?: string;
  packet_count: number;
  why_it_matters: string;
  recommendation: string;
  source_ip?: string;
  destination_ip?: string;
  created_at: string;
}

export interface SecurityOverview {
  total_findings: number;
  severity_counts: {
    HIGH: number;
    MEDIUM: number;
    LOW: number;
    INFORMATIONAL: number;
  };
  category_counts: Record<string, number>;
  findings: SecurityFinding[];
}

export interface TimelinePoint {
  timestamp: number;
  time_label: string;
  packet_count: number;
  byte_count: number;
  tcp_count: number;
  udp_count: number;
  icmp_count: number;
  dns_count: number;
  http_count: number;
}

export interface CaptureStatistics {
  total_packets: number;
  total_bytes: number;
  duration_seconds: number;
  unique_ips: number;
  unique_conversations: number;
  protocol_count: number;
  findings_count: number;
  avg_packet_size: number;
  tcp_packet_count: number;
  udp_packet_count: number;
  icmp_packet_count: number;
  other_packet_count: number;
  packet_size_buckets: Record<string, number>;
}
