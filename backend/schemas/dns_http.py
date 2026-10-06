from typing import Optional, List
from pydantic import BaseModel

class DNSRecordResponse(BaseModel):
    id: int
    capture_id: str
    packet_number: int
    timestamp: float
    query_id: Optional[int] = None
    record_type: str
    query_name: str
    query_type: str
    rcode: Optional[str] = None
    response_data: Optional[str] = None
    is_suspicious: bool
    anomaly_reason: Optional[str] = None

    class Config:
        from_attributes = True

class DNSAnalysisSummary(BaseModel):
    total_queries: int
    total_responses: int
    unique_domains: int
    query_type_counts: dict
    top_domains: List[dict]
    anomalous_queries: List[DNSRecordResponse]

class HTTPRecordResponse(BaseModel):
    id: int
    capture_id: str
    packet_number: int
    timestamp: float
    traffic_type: str
    method: Optional[str] = None
    host: Optional[str] = None
    uri: Optional[str] = None
    status_code: Optional[int] = None
    status_phrase: Optional[str] = None
    user_agent: Optional[str] = None
    content_type: Optional[str] = None
    server: Optional[str] = None
    tls_version: Optional[str] = None
    tls_sni: Optional[str] = None

    class Config:
        from_attributes = True

class HTTPAnalysisSummary(BaseModel):
    http_count: int
    tls_count: int
    methods: dict
    status_codes: dict
    top_hosts: List[dict]
    user_agents: List[str]
    records: List[HTTPRecordResponse]
