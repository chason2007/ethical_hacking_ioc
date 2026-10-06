from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.database import Base

class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(String(36), ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True)
    address = Column(String(64), nullable=False)
    address_type = Column(String(16), nullable=False)  # "IPv4", "IPv6", "MAC"
    
    packets_sent = Column(Integer, default=0)
    packets_received = Column(Integer, default=0)
    bytes_sent = Column(Integer, default=0)
    bytes_received = Column(Integer, default=0)
    total_packets = Column(Integer, default=0)
    total_bytes = Column(Integer, default=0)
    
    is_private = Column(Boolean, default=False)
    hostname = Column(String(255), nullable=True)

    capture = relationship("Capture", back_populates="endpoints")

    __table_args__ = (
        Index("idx_endpoint_capture_addr", "capture_id", "address"),
    )
