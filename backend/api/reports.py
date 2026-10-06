import io
import csv
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import (
    Capture, Packet, Endpoint, Conversation, ProtocolStat, SecurityFinding
)
from backend.services.report_generator import ReportGenerator

router = APIRouter(prefix="/captures/{capture_id}", tags=["Reporting & Export"])

@router.get("/report")
def download_pdf_report(capture_id: str, db: Session = Depends(get_db)):
    """
    Generates and returns an executive cybersecurity PDF analysis report.
    """
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found.")

    # Gather data
    endpoints = db.query(Endpoint).filter(Endpoint.capture_id == capture_id).order_by(Endpoint.total_packets.desc()).all()
    conversations = db.query(Conversation).filter(Conversation.capture_id == capture_id).order_by(Conversation.total_packets.desc()).all()
    protocol_stats = db.query(ProtocolStat).filter(ProtocolStat.capture_id == capture_id).order_by(ProtocolStat.packet_count.desc()).all()
    findings = db.query(SecurityFinding).filter(SecurityFinding.capture_id == capture_id).all()

    capture_meta = {
        "id": capture.id,
        "filename": capture.filename,
        "created_at": capture.created_at,
    }

    stats = {
        "total_packets": capture.packet_count,
        "total_bytes": capture.total_bytes,
        "duration_seconds": capture.duration_seconds,
        "unique_ips": len(endpoints),
        "unique_conversations": len(conversations),
    }

    pdf_path = settings.REPORTS_DIR / f"Report_{capture.filename}_{capture.id[:8]}.pdf"
    ReportGenerator.generate_pdf_report(
        capture_meta=capture_meta,
        stats=stats,
        protocol_stats=[{"protocol_name": p.protocol_name, "layer": p.layer, "packet_count": p.packet_count, "byte_count": p.byte_count, "percentage": p.percentage} for p in protocol_stats],
        endpoints=[{"address": e.address, "address_type": e.address_type, "is_private": e.is_private, "packets_sent": e.packets_sent, "packets_received": e.packets_received, "total_bytes": e.total_bytes} for e in endpoints],
        conversations=[{"endpoint_a": c.endpoint_a, "endpoint_b": c.endpoint_b, "protocol": c.protocol, "total_packets": c.total_packets, "total_bytes": c.total_bytes, "duration": c.duration} for c in conversations],
        findings=[{"title": f.title, "severity": f.severity, "category": f.category, "evidence": f.evidence, "why_it_matters": f.why_it_matters, "recommendation": f.recommendation} for f in findings],
        output_filepath=pdf_path
    )

    return FileResponse(
        path=str(pdf_path),
        filename=f"Security_Report_{capture.filename}.pdf",
        media_type="application/pdf"
    )

@router.get("/export/csv")
def export_packets_csv(
    capture_id: str,
    protocol: str = Query(None),
    limit: int = Query(5000, ge=1, le=50000),
    db: Session = Depends(get_db)
):
    """
    Exports captured packets as a CSV spreadsheet.
    """
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found.")

    query = db.query(Packet).filter(Packet.capture_id == capture_id)
    if protocol and protocol.upper() != "ALL":
        query = query.filter(Packet.protocol.ilike(f"%{protocol}%"))

    packets = query.order_by(Packet.packet_number.asc()).limit(limit).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Packet_No", "Timestamp", "Relative_Time_Sec", "Source_IP", "Destination_IP",
        "Protocol", "Source_Port", "Destination_Port", "Length", "TCP_Flags",
        "Source_MAC", "Destination_MAC", "Info"
    ])

    for p in packets:
        writer.writerow([
            p.packet_number, p.timestamp, p.relative_time, p.source_ip or "", p.destination_ip or "",
            p.protocol, p.source_port or "", p.destination_port or "", p.length, p.tcp_flags or "",
            p.source_mac or "", p.destination_mac or "", p.info or ""
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="packets_{capture.filename}.csv"'}
    )

@router.get("/export/json")
def export_capture_json(capture_id: str, db: Session = Depends(get_db)):
    """
    Exports the complete structured analysis as JSON.
    """
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found.")

    endpoints = db.query(Endpoint).filter(Endpoint.capture_id == capture_id).all()
    conversations = db.query(Conversation).filter(Conversation.capture_id == capture_id).all()
    protocol_stats = db.query(ProtocolStat).filter(ProtocolStat.capture_id == capture_id).all()
    findings = db.query(SecurityFinding).filter(SecurityFinding.capture_id == capture_id).all()

    data = {
        "capture": {
            "id": capture.id,
            "filename": capture.filename,
            "packet_count": capture.packet_count,
            "total_bytes": capture.total_bytes,
            "duration_seconds": capture.duration_seconds,
            "created_at": capture.created_at.isoformat() if capture.created_at else None,
        },
        "protocol_stats": [
            {"protocol": p.protocol_name, "layer": p.layer, "packets": p.packet_count, "bytes": p.byte_count, "percentage": p.percentage}
            for p in protocol_stats
        ],
        "endpoints": [
            {"address": e.address, "type": e.address_type, "packets_sent": e.packets_sent, "packets_received": e.packets_received, "bytes": e.total_bytes, "is_private": e.is_private}
            for e in endpoints
        ],
        "conversations": [
            {"endpoint_a": c.endpoint_a, "endpoint_b": c.endpoint_b, "protocol": c.protocol, "port_a": c.port_a, "port_b": c.port_b, "packets": c.total_packets, "bytes": c.total_bytes, "duration": c.duration}
            for c in conversations
        ],
        "security_findings": [
            {"title": f.title, "severity": f.severity, "category": f.category, "evidence": f.evidence, "why_it_matters": f.why_it_matters, "recommendation": f.recommendation, "source_ip": f.source_ip}
            for f in findings
        ]
    }
    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="analysis_{capture.filename}.json"'}
    )
