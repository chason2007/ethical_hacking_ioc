from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from backend.database import get_db
from backend.models import ProtocolStat, Conversation, Endpoint, Packet
from backend.schemas import (
    ProtocolStatResponse, ConversationResponse, EndpointResponse, PortStat
)
from backend.services.pcap_parser import COMMON_PORTS

# ----------------- Protocols Router -----------------
protocols_router = APIRouter(prefix="/captures/{capture_id}/protocols", tags=["Protocols"])

@protocols_router.get("", response_model=List[ProtocolStatResponse])
def get_protocol_stats(capture_id: str, db: Session = Depends(get_db)):
    """Returns protocol breakdown and layer distribution."""
    stats = db.query(ProtocolStat).filter(
        ProtocolStat.capture_id == capture_id
    ).order_by(ProtocolStat.packet_count.desc()).all()
    return stats


# ----------------- Conversations Router -----------------
conversations_router = APIRouter(prefix="/captures/{capture_id}/conversations", tags=["Conversations"])

@conversations_router.get("", response_model=List[ConversationResponse])
def get_conversations(
    capture_id: str,
    sort_by: str = Query("packets"),  # packets, bytes, duration
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Returns bidirectional conversations between IP endpoints."""
    query = db.query(Conversation).filter(Conversation.capture_id == capture_id)
    if sort_by == "bytes":
        query = query.order_by(Conversation.total_bytes.desc())
    elif sort_by == "duration":
        query = query.order_by(Conversation.duration.desc())
    else:
        query = query.order_by(Conversation.total_packets.desc())
    return query.limit(limit).all()


# ----------------- Endpoints Router -----------------
endpoints_router = APIRouter(prefix="/captures/{capture_id}/endpoints", tags=["Endpoints"])

@endpoints_router.get("", response_model=List[EndpointResponse])
def get_endpoints(
    capture_id: str,
    address_type: str = Query(None),  # IPv4, IPv6, MAC
    is_private: bool = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Returns active network endpoints with sent/received volume."""
    query = db.query(Endpoint).filter(Endpoint.capture_id == capture_id)
    if address_type:
        query = query.filter(Endpoint.address_type.ilike(address_type))
    if is_private is not None:
        query = query.filter(Endpoint.is_private == is_private)
    return query.order_by(Endpoint.total_packets.desc()).limit(limit).all()


# ----------------- Ports Router -----------------
ports_router = APIRouter(prefix="/captures/{capture_id}/ports", tags=["Ports"])

@ports_router.get("", response_model=List[PortStat])
def get_port_stats(capture_id: str, limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    """
    Returns aggregated port usage with static service mapping and defensive descriptions.
    """
    # Group destination ports
    dst_ports = db.query(
        Packet.destination_port.label("port"),
        Packet.protocol.label("protocol"),
        func.count(Packet.id).label("packet_count"),
        func.sum(Packet.length).label("byte_count")
    ).filter(
        Packet.capture_id == capture_id,
        Packet.destination_port.isnot(None)
    ).group_by(Packet.destination_port, Packet.protocol).order_by(func.count(Packet.id).desc()).limit(limit).all()

    results = []
    seen_ports = set()
    for row in dst_ports:
        port_num = row.port
        if port_num in seen_ports:
            continue
        seen_ports.add(port_num)
        
        svc = COMMON_PORTS.get(port_num, "Dynamic / Unassigned")
        desc = (
            f"Port {port_num} is commonly associated with {svc}."
            if port_num in COMMON_PORTS
            else f"Port {port_num} is an ephemeral, unassigned, or custom application port."
        )
        results.append(PortStat(
            port=port_num,
            protocol=row.protocol,
            packet_count=row.packet_count,
            byte_count=row.byte_count or 0,
            common_service=svc,
            description=desc,
        ))
    return results
