from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class SecurityFindingResponse(BaseModel):
    id: int
    capture_id: str
    title: str
    severity: str  # INFORMATIONAL, LOW, MEDIUM, HIGH
    category: str
    evidence: str
    packets_involved: Optional[str] = None
    packet_count: int
    why_it_matters: str
    recommendation: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SecurityOverviewResponse(BaseModel):
    total_findings: int
    severity_counts: Dict[str, int]
    category_counts: Dict[str, int]
    findings: List[SecurityFindingResponse]

class PortStat(BaseModel):
    port: int
    protocol: str
    packet_count: int
    byte_count: int
    common_service: str
    description: str

class TimelinePoint(BaseModel):
    timestamp: float
    time_label: str
    packet_count: int
    byte_count: int
    tcp_count: int
    udp_count: int
    icmp_count: int
    dns_count: int
    http_count: int

class CaptureStatisticsResponse(BaseModel):
    total_packets: int
    total_bytes: int
    duration_seconds: float
    unique_ips: int
    unique_conversations: int
    protocol_count: int
    findings_count: int
    avg_packet_size: float
    tcp_packet_count: int
    udp_packet_count: int
    icmp_packet_count: int
    other_packet_count: int
    packet_size_buckets: Dict[str, int]
