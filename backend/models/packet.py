from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.database import Base

class Packet(Base):
    __tablename__ = "packets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(String(36), ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True)
    packet_number = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)
    relative_time = Column(Float, default=0.0)
    
    # Layer 2 / MAC
    source_mac = Column(String(32), nullable=True)
    destination_mac = Column(String(32), nullable=True)
    eth_type = Column(String(32), nullable=True)

    # Layer 3 / IP
    ip_version = Column(Integer, nullable=True)
    source_ip = Column(String(64), nullable=True, index=True)
    destination_ip = Column(String(64), nullable=True, index=True)
    ip_ttl = Column(Integer, nullable=True)
    ip_id = Column(Integer, nullable=True)

    # Layer 4 / Transport
    protocol = Column(String(32), nullable=False, index=True)  # TCP, UDP, ICMP, ARP, etc.
    source_port = Column(Integer, nullable=True, index=True)
    destination_port = Column(Integer, nullable=True, index=True)
    tcp_flags = Column(String(32), nullable=True)  # "SYN", "ACK", "SYN-ACK", etc.
    tcp_seq = Column(Integer, nullable=True)
    tcp_ack = Column(Integer, nullable=True)
    tcp_window = Column(Integer, nullable=True)

    # Size & Summary
    length = Column(Integer, default=0)
    info = Column(String(512), nullable=True)
    
    # Rich packet inspector data
    layers_json = Column(Text, nullable=True)  # JSON-encoded hierarchical protocol layers
    payload_preview = Column(Text, nullable=True)  # ASCII/Hex safe representation

    capture = relationship("Capture", back_populates="packets")

    __table_args__ = (
        Index("idx_capture_packet_num", "capture_id", "packet_number"),
        Index("idx_capture_proto_src_dst", "capture_id", "protocol", "source_ip", "destination_ip"),
    )
