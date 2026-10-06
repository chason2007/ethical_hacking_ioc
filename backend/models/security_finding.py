import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base

class SecurityFinding(Base):
    __tablename__ = "security_findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(String(36), ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    severity = Column(String(32), nullable=False)  # INFORMATIONAL, LOW, MEDIUM, HIGH
    category = Column(String(64), nullable=False)
    
    evidence = Column(Text, nullable=False)
    packets_involved = Column(String(255), nullable=True)  # e.g., "Packets: #12, #15, #19" or count
    packet_count = Column(Integer, default=1)
    
    why_it_matters = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    
    source_ip = Column(String(64), nullable=True)
    destination_ip = Column(String(64), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    capture = relationship("Capture", back_populates="security_findings")
