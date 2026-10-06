from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class DNSRecord(Base):
    __tablename__ = "dns_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(String(36), ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True)
    packet_number = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)
    
    query_id = Column(Integer, nullable=True)
    record_type = Column(String(16), default="QUERY")  # QUERY, RESPONSE
    query_name = Column(String(255), nullable=False)
    query_type = Column(String(16), default="A")  # A, AAAA, MX, TXT, PTR, etc.
    rcode = Column(String(32), nullable=True)  # NOERROR, NXDOMAIN, SERVFAIL
    response_data = Column(String(512), nullable=True)
    
    is_suspicious = Column(Boolean, default=False)
    anomaly_reason = Column(String(255), nullable=True)

    capture = relationship("Capture", back_populates="dns_records")
