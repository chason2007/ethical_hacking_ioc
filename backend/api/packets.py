import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc

from backend.database import get_db
from backend.models import Packet
from backend.schemas import PacketResponse, PacketDetailResponse, PacketPageResponse

router = APIRouter(prefix="/captures/{capture_id}/packets", tags=["Packets"])

@router.get("", response_model=PacketPageResponse)
def get_packets(
    capture_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    protocol: Optional[str] = Query(None),
    source_ip: Optional[str] = Query(None),
    destination_ip: Optional[str] = Query(None),
    port: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("packet_number"),
    sort_dir: str = Query("asc"),
    db: Session = Depends(get_db),
):
    """
    Retrieves paginated packets for a capture with filtering, searching, and sorting.
    """
    query = db.query(Packet).filter(Packet.capture_id == capture_id)

    # Protocol filter
    if protocol and protocol.upper() != "ALL":
        query = query.filter(Packet.protocol.ilike(f"%{protocol}%"))

    # IP filters
    if source_ip:
        query = query.filter(Packet.source_ip == source_ip)
    if destination_ip:
        query = query.filter(Packet.destination_ip == destination_ip)

    # Port filter
    if port:
        query = query.filter(or_(Packet.source_port == port, Packet.destination_port == port))

    # Search filter (supports search string or structured key:value queries)
    if search:
        search = search.strip()
        # Parse filter key tokens like 'protocol:tcp', 'port:443', 'ip:192.168.1.1'
        if ":" in search:
            parts = search.split()
            for part in parts:
                if ":" in part:
                    k, v = part.split(":", 1)
                    k_lower = k.lower()
                    if k_lower in ("proto", "protocol"):
                        query = query.filter(Packet.protocol.ilike(f"%{v}%"))
                    elif k_lower in ("port", "p") and v.isdigit():
                        p_int = int(v)
                        query = query.filter(or_(Packet.source_port == p_int, Packet.destination_port == p_int))
                    elif k_lower in ("ip", "host"):
                        query = query.filter(or_(Packet.source_ip == v, Packet.destination_ip == v))
                    elif k_lower in ("src", "src_ip"):
                        query = query.filter(Packet.source_ip == v)
                    elif k_lower in ("dst", "dst_ip"):
                        query = query.filter(Packet.destination_ip == v)
                    elif k_lower in ("num", "packet"):
                        if v.isdigit():
                            query = query.filter(Packet.packet_number == int(v))
        else:
            # General text search across multiple fields
            query = query.filter(
                or_(
                    Packet.info.ilike(f"%{search}%"),
                    Packet.source_ip.ilike(f"%{search}%"),
                    Packet.destination_ip.ilike(f"%{search}%"),
                    Packet.protocol.ilike(f"%{search}%"),
                    Packet.source_mac.ilike(f"%{search}%"),
                    Packet.destination_mac.ilike(f"%{search}%"),
                    Packet.tcp_flags.ilike(f"%{search}%"),
                )
            )

    # Total count after filters
    total = query.count()

    # Sorting
    sort_column = getattr(Packet, sort_by, Packet.packet_number)
    if sort_dir.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Pagination
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PacketPageResponse(
        items=[PacketResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

@router.get("/{packet_number}", response_model=PacketDetailResponse)
def get_packet_detail(capture_id: str, packet_number: int, db: Session = Depends(get_db)):
    """
    Get complete details of a specific packet including protocol layers JSON hierarchy.
    """
    pkt = db.query(Packet).filter(
        Packet.capture_id == capture_id,
        Packet.packet_number == packet_number
    ).first()
    
    if not pkt:
        raise HTTPException(status_code=404, detail=f"Packet #{packet_number} not found.")
        
    return PacketDetailResponse.model_validate(pkt)
