from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import Capture, Packet, Endpoint, Conversation, ProtocolStat, SecurityFinding
from backend.schemas import CaptureStatisticsResponse, TimelinePoint

router = APIRouter(prefix="/captures/{capture_id}", tags=["Statistics & Timeline"])

@router.get("/statistics", response_model=CaptureStatisticsResponse)
def get_capture_statistics(capture_id: str, db: Session = Depends(get_db)):
    """
    Returns top-level metric cards data and packet size distribution.
    """
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found.")

    unique_ips = db.query(func.count(Endpoint.id)).filter(Endpoint.capture_id == capture_id).scalar() or 0
    unique_convs = db.query(func.count(Conversation.id)).filter(Conversation.capture_id == capture_id).scalar() or 0
    proto_count = db.query(func.count(ProtocolStat.id)).filter(ProtocolStat.capture_id == capture_id).scalar() or 0
    findings_count = db.query(func.count(SecurityFinding.id)).filter(SecurityFinding.capture_id == capture_id).scalar() or 0

    # Protocol breakdown counts
    tcp_count = db.query(func.count(Packet.id)).filter(Packet.capture_id == capture_id, Packet.protocol.in_(["TCP", "TLS"])).scalar() or 0
    udp_count = db.query(func.count(Packet.id)).filter(Packet.capture_id == capture_id, Packet.protocol.in_(["UDP", "DNS"])).scalar() or 0
    icmp_count = db.query(func.count(Packet.id)).filter(Packet.capture_id == capture_id, Packet.protocol.ilike("%ICMP%")).scalar() or 0
    other_count = max(capture.packet_count - (tcp_count + udp_count + icmp_count), 0)

    # Packet size buckets
    b_under_64 = db.query(func.count(Packet.id)).filter(Packet.capture_id == capture_id, Packet.length < 64).scalar() or 0
    b_64_128 = db.query(func.count(Packet.id)).filter(Packet.capture_id == capture_id, Packet.length >= 64, Packet.length <= 128).scalar() or 0
    b_129_512 = db.query(func.count(Packet.id)).filter(Packet.capture_id == capture_id, Packet.length > 128, Packet.length <= 512).scalar() or 0
    b_513_1024 = db.query(func.count(Packet.id)).filter(Packet.capture_id == capture_id, Packet.length > 512, Packet.length <= 1024).scalar() or 0
    b_1025_1518 = db.query(func.count(Packet.id)).filter(Packet.capture_id == capture_id, Packet.length > 1024, Packet.length <= 1518).scalar() or 0
    b_over_1518 = db.query(func.count(Packet.id)).filter(Packet.capture_id == capture_id, Packet.length > 1518).scalar() or 0

    avg_size = round(capture.total_bytes / capture.packet_count, 1) if capture.packet_count > 0 else 0.0

    return CaptureStatisticsResponse(
        total_packets=capture.packet_count,
        total_bytes=capture.total_bytes,
        duration_seconds=capture.duration_seconds,
        unique_ips=unique_ips,
        unique_conversations=unique_convs,
        protocol_count=proto_count,
        findings_count=findings_count,
        avg_packet_size=avg_size,
        tcp_packet_count=tcp_count,
        udp_packet_count=udp_count,
        icmp_packet_count=icmp_count,
        other_packet_count=other_count,
        packet_size_buckets={
            "<64 bytes": b_under_64,
            "64-128 bytes": b_64_128,
            "129-512 bytes": b_129_512,
            "513-1024 bytes": b_513_1024,
            "1025-1518 bytes": b_1025_1518,
            ">1518 bytes": b_over_1518,
        }
    )

@router.get("/timeline", response_model=List[TimelinePoint])
def get_timeline(capture_id: str, db: Session = Depends(get_db)):
    """
    Generates time-series buckets for traffic over time visualization.
    """
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found.")

    packets = db.query(
        Packet.timestamp, Packet.length, Packet.protocol
    ).filter(Packet.capture_id == capture_id).order_by(Packet.timestamp.asc()).all()

    if not packets:
        return []

    start_ts = packets[0].timestamp
    end_ts = packets[-1].timestamp
    span = max(end_ts - start_ts, 1.0)
    num_bins = min(max(int(span), 10), 50)
    bin_size = span / num_bins

    bins = [
        {
            "timestamp": round(start_ts + i * bin_size, 2),
            "time_label": f"{round(i * bin_size, 1)}s",
            "packet_count": 0,
            "byte_count": 0,
            "tcp_count": 0,
            "udp_count": 0,
            "icmp_count": 0,
            "dns_count": 0,
            "http_count": 0,
        }
        for i in range(num_bins)
    ]

    for p in packets:
        idx = min(int((p.timestamp - start_ts) / bin_size), num_bins - 1)
        b = bins[idx]
        b["packet_count"] += 1
        b["byte_count"] += p.length
        proto = p.protocol.upper()
        if proto in ("TCP", "TLS"):
            b["tcp_count"] += 1
        elif proto == "UDP":
            b["udp_count"] += 1
        elif "ICMP" in proto:
            b["icmp_count"] += 1
        elif proto == "DNS":
            b["dns_count"] += 1
        elif proto == "HTTP":
            b["http_count"] += 1

    return [TimelinePoint(**b) for b in bins]
