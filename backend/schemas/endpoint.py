from typing import Optional, List
from pydantic import BaseModel

class EndpointResponse(BaseModel):
    id: int
    capture_id: str
    address: str
    address_type: str
    packets_sent: int
    packets_received: int
    bytes_sent: int
    bytes_received: int
    total_packets: int
    total_bytes: int
    is_private: bool
    hostname: Optional[str] = None

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    capture_id: str
    protocol: str
    endpoint_a: str
    endpoint_b: str
    port_a: Optional[int] = None
    port_b: Optional[int] = None
    packets_a_to_b: int
    packets_b_to_a: int
    bytes_a_to_b: int
    bytes_b_to_a: int
    total_packets: int
    total_bytes: int
    start_time: float
    end_time: float
    duration: float

    class Config:
        from_attributes = True

class ProtocolStatResponse(BaseModel):
    id: int
    capture_id: str
    protocol_name: str
    layer: str
    packet_count: int
    byte_count: int
    percentage: float

    class Config:
        from_attributes = True
