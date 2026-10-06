from typing import Optional, List, Any
from pydantic import BaseModel

class PacketResponse(BaseModel):
    id: int
    capture_id: str
    packet_number: int
    timestamp: float
    relative_time: float
    source_mac: Optional[str] = None
    destination_mac: Optional[str] = None
    eth_type: Optional[str] = None
    ip_version: Optional[int] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    ip_ttl: Optional[int] = None
    protocol: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    tcp_flags: Optional[str] = None
    tcp_seq: Optional[int] = None
    tcp_ack: Optional[int] = None
    tcp_window: Optional[int] = None
    length: int
    info: Optional[str] = None

    class Config:
        from_attributes = True

class PacketDetailResponse(PacketResponse):
    layers_json: Optional[str] = None
    payload_preview: Optional[str] = None

class PacketPageResponse(BaseModel):
    items: List[PacketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
