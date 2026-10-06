from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import DNSRecord, HTTPRecord
from backend.schemas import (
    DNSRecordResponse, DNSAnalysisSummary,
    HTTPRecordResponse, HTTPAnalysisSummary
)

dns_router = APIRouter(prefix="/captures/{capture_id}/dns", tags=["DNS Analysis"])
http_router = APIRouter(prefix="/captures/{capture_id}/http", tags=["HTTP & TLS Analysis"])

@dns_router.get("", response_model=DNSAnalysisSummary)
def get_dns_analysis(capture_id: str, db: Session = Depends(get_db)):
    """
    Returns comprehensive DNS analysis including queries, responses, record types, and anomalous lookups.
    """
    records = db.query(DNSRecord).filter(DNSRecord.capture_id == capture_id).all()
    
    queries = [r for r in records if r.record_type == "QUERY"]
    responses = [r for r in records if r.record_type == "RESPONSE"]
    
    unique_domains = len(set(r.query_name for r in records if r.query_name))
    
    type_counts = Counter(r.query_type for r in records if r.query_type)
    
    domain_counts = Counter(r.query_name for r in queries if r.query_name)
    top_domains = [{"domain": d, "count": c} for d, c in domain_counts.most_common(10)]
    
    anomalous = [DNSRecordResponse.model_validate(r) for r in records if r.is_suspicious]
    
    return DNSAnalysisSummary(
        total_queries=len(queries),
        total_responses=len(responses),
        unique_domains=unique_domains,
        query_type_counts=dict(type_counts),
        top_domains=top_domains,
        anomalous_queries=anomalous,
    )

@http_router.get("", response_model=HTTPAnalysisSummary)
def get_http_analysis(capture_id: str, db: Session = Depends(get_db)):
    """
    Returns HTTP cleartext inspection and TLS metadata analysis.
    """
    records = db.query(HTTPRecord).filter(HTTPRecord.capture_id == capture_id).all()
    
    http_recs = [r for r in records if r.traffic_type in ("REQUEST", "RESPONSE")]
    tls_recs = [r for r in records if r.traffic_type in ("TLS_HANDSHAKE", "TLS_APPLICATION")]
    
    methods = Counter(r.method for r in records if r.method)
    status_codes = Counter(str(r.status_code) for r in records if r.status_code)
    
    hosts = Counter(r.host for r in records if r.host)
    top_hosts = [{"host": h, "count": c} for h, c in hosts.most_common(10)]
    
    uas = list(set(r.user_agent for r in records if r.user_agent))
    
    return HTTPAnalysisSummary(
        http_count=len(http_recs),
        tls_count=len(tls_recs),
        methods=dict(methods),
        status_codes=dict(status_codes),
        top_hosts=top_hosts,
        user_agents=uas,
        records=[HTTPRecordResponse.model_validate(r) for r in records[:100]],
    )
