from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class HTTPRecord(Base):
    __tablename__ = "http_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(String(36), ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True)
    packet_number = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)
    
    traffic_type = Column(String(16), default="REQUEST")  # REQUEST, RESPONSE, TLS_CLIENT_HELLO, TLS_SERVER_HELLO
    method = Column(String(16), nullable=True)  # GET, POST, PUT, DELETE, etc.
    host = Column(String(255), nullable=True)
    uri = Column(String(512), nullable=True)
    status_code = Column(Integer, nullable=True)
    status_phrase = Column(String(64), nullable=True)
    user_agent = Column(String(255), nullable=True)
    content_type = Column(String(128), nullable=True)
    server = Column(String(128), nullable=True)
    
    # TLS metadata
    tls_version = Column(String(32), nullable=True)
    tls_sni = Column(String(255), nullable=True)

    capture = relationship("Capture", back_populates="http_records")
