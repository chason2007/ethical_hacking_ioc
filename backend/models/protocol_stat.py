from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class ProtocolStat(Base):
    __tablename__ = "protocol_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(String(36), ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True)
    
    protocol_name = Column(String(64), nullable=False)
    layer = Column(String(32), default="Transport")  # Link, Network, Transport, Application
    packet_count = Column(Integer, default=0)
    byte_count = Column(Integer, default=0)
    percentage = Column(Float, default=0.0)

    capture = relationship("Capture", back_populates="protocol_stats")
