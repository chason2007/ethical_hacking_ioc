import shutil
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.config import settings
from backend.database import get_db
from backend.models import (
    Capture, Packet, Endpoint, Conversation, ProtocolStat,
    DNSRecord, HTTPRecord, SecurityFinding
)
from backend.schemas import CaptureResponse, CaptureSummary
from backend.services.pcap_parser import parse_pcap_file
from backend.services.analysis_engine import AnalysisEngine
from backend.services.security_analyzer import SecurityAnalyzer
from backend.services.synthetic_pcap_generator import generate_demo_pcap

router = APIRouter(prefix="/captures", tags=["Captures"])

def process_and_save_capture(db: Session, filepath: Path, original_filename: str, is_demo: int = 0) -> Capture:
    # 1. Parse packets
    parsed_packets, summary = parse_pcap_file(str(filepath))
    
    # 2. Run analysis engine
    analysis_res = AnalysisEngine.analyze_capture(
        parsed_packets, summary["total_bytes"], summary["duration_seconds"]
    )
    
    # 3. Run defensive security rules
    security_findings = SecurityAnalyzer.analyze(parsed_packets, summary)
    
    # 4. Create Capture DB record
    capture_id = str(uuid.uuid4())
    capture = Capture(
        id=capture_id,
        filename=original_filename,
        filepath=str(filepath),
        file_size_bytes=filepath.stat().st_size if filepath.exists() else 0,
        packet_count=summary["packet_count"],
        total_bytes=summary["total_bytes"],
        duration_seconds=summary["duration_seconds"],
        start_time=summary["start_time"],
        end_time=summary["end_time"],
        status="analyzed",
        is_demo=is_demo,
    )
    db.add(capture)
    
    # 5. Insert packets
    packet_objs = []
    dns_objs = []
    http_objs = []
    for p in parsed_packets:
        pkt_obj = Packet(
            capture_id=capture_id,
            packet_number=p.packet_number,
            timestamp=p.timestamp,
            relative_time=p.relative_time,
            source_mac=p.source_mac,
            destination_mac=p.destination_mac,
            eth_type=p.eth_type,
            ip_version=p.ip_version,
            source_ip=p.source_ip,
            destination_ip=p.destination_ip,
            ip_ttl=p.ip_ttl,
            ip_id=p.ip_id,
            protocol=p.protocol,
            source_port=p.source_port,
            destination_port=p.destination_port,
            tcp_flags=p.tcp_flags,
            tcp_seq=p.tcp_seq,
            tcp_ack=p.tcp_ack,
            tcp_window=p.tcp_window,
            length=p.length,
            info=p.info,
            layers_json=p.layers_json,
            payload_preview=p.payload_preview,
        )
        packet_objs.append(pkt_obj)
        
        if p.dns_record:
            dr = p.dns_record
            dns_objs.append(DNSRecord(
                capture_id=capture_id,
                packet_number=p.packet_number,
                timestamp=p.timestamp,
                query_id=dr.get("query_id"),
                record_type=dr.get("record_type", "QUERY"),
                query_name=dr.get("query_name", ""),
                query_type=dr.get("query_type", "A"),
                rcode=dr.get("rcode"),
                response_data=dr.get("response_data"),
                is_suspicious=dr.get("is_suspicious", False),
                anomaly_reason=dr.get("anomaly_reason"),
            ))
            
        if p.http_record:
            hr = p.http_record
            http_objs.append(HTTPRecord(
                capture_id=capture_id,
                packet_number=p.packet_number,
                timestamp=p.timestamp,
                traffic_type=hr.get("traffic_type", "REQUEST"),
                method=hr.get("method"),
                host=hr.get("host"),
                uri=hr.get("uri"),
                status_code=hr.get("status_code"),
                status_phrase=hr.get("status_phrase"),
                user_agent=hr.get("user_agent"),
                content_type=hr.get("content_type"),
                server=hr.get("server"),
                tls_version=hr.get("tls_version"),
                tls_sni=hr.get("tls_sni"),
            ))

    db.bulk_save_objects(packet_objs)
    if dns_objs:
        db.bulk_save_objects(dns_objs)
    if http_objs:
        db.bulk_save_objects(http_objs)

    # 6. Insert endpoints
    endpoint_objs = [
        Endpoint(
            capture_id=capture_id,
            address=ep["address"],
            address_type=ep["address_type"],
            packets_sent=ep["packets_sent"],
            packets_received=ep["packets_received"],
            bytes_sent=ep["bytes_sent"],
            bytes_received=ep["bytes_received"],
            total_packets=ep["total_packets"],
            total_bytes=ep["total_bytes"],
            is_private=ep["is_private"],
            hostname=ep["hostname"],
        )
        for ep in analysis_res["endpoints"]
    ]
    db.bulk_save_objects(endpoint_objs)

    # 7. Insert conversations
    conversation_objs = [
        Conversation(
            capture_id=capture_id,
            protocol=c["protocol"],
            endpoint_a=c["endpoint_a"],
            endpoint_b=c["endpoint_b"],
            port_a=c["port_a"],
            port_b=c["port_b"],
            packets_a_to_b=c["packets_a_to_b"],
            packets_b_to_a=c["packets_b_to_a"],
            bytes_a_to_b=c["bytes_a_to_b"],
            bytes_b_to_a=c["bytes_b_to_a"],
            total_packets=c["total_packets"],
            total_bytes=c["total_bytes"],
            start_time=c["start_time"],
            end_time=c["end_time"],
            duration=c["duration"],
        )
        for c in analysis_res["conversations"]
    ]
    db.bulk_save_objects(conversation_objs)

    # 8. Insert protocol statistics
    proto_objs = [
        ProtocolStat(
            capture_id=capture_id,
            protocol_name=ps["protocol_name"],
            layer=ps["layer"],
            packet_count=ps["packet_count"],
            byte_count=ps["byte_count"],
            percentage=ps["percentage"],
        )
        for ps in analysis_res["protocol_stats"]
    ]
    db.bulk_save_objects(proto_objs)

    # 9. Insert security findings
    finding_objs = [
        SecurityFinding(
            capture_id=capture_id,
            title=f["title"],
            severity=f["severity"],
            category=f["category"],
            evidence=f["evidence"],
            packets_involved=f.get("packets_involved"),
            packet_count=f.get("packet_count", 1),
            why_it_matters=f["why_it_matters"],
            recommendation=f["recommendation"],
            source_ip=f.get("source_ip"),
            destination_ip=f.get("destination_ip"),
        )
        for f in security_findings
    ]
    db.bulk_save_objects(finding_objs)

    db.commit()
    db.refresh(capture)
    return capture

@router.post("/upload", response_model=CaptureResponse)
async def upload_capture(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and analyze a .pcap or .pcapng file."""
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    unique_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    saved_path = settings.UPLOAD_DIR / unique_name
    
    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = saved_path.stat().st_size
        if file_size == 0:
            saved_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")
            
        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            saved_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum upload size limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
            
        capture = process_and_save_capture(db, saved_path, file.filename, is_demo=0)
        return capture
        
    except HTTPException:
        raise
    except Exception as e:
        if saved_path.exists():
            saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Packet parsing or analysis failed: {str(e)}")

@router.post("/demo", response_model=CaptureResponse)
def load_demo_capture(db: Session = Depends(get_db)):
    """Loads or creates synthetic demonstration capture dataset."""
    demo_path = settings.SAMPLE_DATA_DIR / "demo_capture.pcap"
    if not demo_path.exists() or demo_path.stat().st_size == 0:
        demo_path = generate_demo_pcap(demo_path)
        
    # Check if demo capture already exists in db
    existing = db.query(Capture).filter(Capture.is_demo == 1).first()
    if existing:
        return existing
        
    capture = process_and_save_capture(db, demo_path, "demo_capture.pcap", is_demo=1)
    return capture

@router.get("", response_model=List[CaptureSummary])
def list_captures(db: Session = Depends(get_db)):
    """Lists all analyzed captures with summary statistics."""
    captures = db.query(Capture).order_by(Capture.created_at.desc()).all()
    results = []
    for c in captures:
        findings_count = db.query(func.count(SecurityFinding.id)).filter(SecurityFinding.capture_id == c.id).scalar() or 0
        proto_count = db.query(func.count(ProtocolStat.id)).filter(ProtocolStat.capture_id == c.id).scalar() or 0
        results.append(CaptureSummary(
            id=c.id,
            filename=c.filename,
            file_size_bytes=c.file_size_bytes,
            packet_count=c.packet_count,
            total_bytes=c.total_bytes,
            duration_seconds=c.duration_seconds,
            status=c.status,
            is_demo=c.is_demo,
            findings_count=findings_count,
            protocols_count=proto_count,
            created_at=c.created_at,
        ))
    return results

@router.get("/{capture_id}", response_model=CaptureResponse)
def get_capture(capture_id: str, db: Session = Depends(get_db)):
    """Get capture metadata by ID."""
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found.")
    return capture

@router.delete("/{capture_id}")
def delete_capture(capture_id: str, db: Session = Depends(get_db)):
    """Deletes capture and cascades deletion of associated data."""
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found.")
    
    # Remove file if not demo
    if capture.is_demo == 0 and Path(capture.filepath).exists():
        try:
            Path(capture.filepath).unlink()
        except Exception:
            pass
            
    db.delete(capture)
    db.commit()
    return {"message": "Capture deleted successfully", "id": capture_id}
