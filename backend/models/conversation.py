from sqlalchemy import Column, Integer, Float, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(String(36), ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True)
    
    protocol = Column(String(32), nullable=False)
    endpoint_a = Column(String(64), nullable=False)
    endpoint_b = Column(String(64), nullable=False)
    port_a = Column(Integer, nullable=True)
    port_b = Column(Integer, nullable=True)
    
    packets_a_to_b = Column(Integer, default=0)
    packets_b_to_a = Column(Integer, default=0)
    bytes_a_to_b = Column(Integer, default=0)
    bytes_b_to_a = Column(Integer, default=0)
    total_packets = Column(Integer, default=0)
    total_bytes = Column(Integer, default=0)
    
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float, default=0.0)

    capture = relationship("Capture", back_populates="conversations")

    __table_args__ = (
        Index("idx_conv_capture_pair", "capture_id", "endpoint_a", "endpoint_b"),
    )
