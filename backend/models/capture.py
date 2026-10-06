import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class Capture(Base):
    __tablename__ = "captures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    packet_count = Column(Integer, default=0)
    total_bytes = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    start_time = Column(Float, nullable=True)
    end_time = Column(Float, nullable=True)
    status = Column(String(32), default="pending")  # pending, parsing, analyzed, error
    error_message = Column(Text, nullable=True)
    is_demo = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    packets = relationship("Packet", back_populates="capture", cascade="all, delete-orphan")
    endpoints = relationship("Endpoint", back_populates="capture", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="capture", cascade="all, delete-orphan")
    protocol_stats = relationship("ProtocolStat", back_populates="capture", cascade="all, delete-orphan")
    security_findings = relationship("SecurityFinding", back_populates="capture", cascade="all, delete-orphan")
    dns_records = relationship("DNSRecord", back_populates="capture", cascade="all, delete-orphan")
    http_records = relationship("HTTPRecord", back_populates="capture", cascade="all, delete-orphan")
