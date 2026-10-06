from collections import Counter
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import SecurityFinding
from backend.schemas import SecurityFindingResponse, SecurityOverviewResponse

router = APIRouter(prefix="/captures/{capture_id}/security", tags=["Security Insights"])

@router.get("", response_model=SecurityOverviewResponse)
def get_security_findings(
    capture_id: str,
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Returns rule-based defensive security findings, anomaly evidence, and severity counts.
    """
    query = db.query(SecurityFinding).filter(SecurityFinding.capture_id == capture_id)
    all_findings = query.all()

    sev_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFORMATIONAL": 0}
    cat_counts = Counter()

    for f in all_findings:
        sev = f.severity.upper()
        if sev in sev_counts:
            sev_counts[sev] += 1
        cat_counts[f.category] += 1

    # Filter if requested
    filtered_findings = all_findings
    if severity and severity.upper() != "ALL":
        filtered_findings = [f for f in filtered_findings if f.severity.upper() == severity.upper()]
    if category and category.upper() != "ALL":
        filtered_findings = [f for f in filtered_findings if f.category.upper() == category.upper()]

    # Sort: HIGH, MEDIUM, LOW, INFORMATIONAL
    order_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFORMATIONAL": 3}
    filtered_findings.sort(key=lambda x: order_map.get(x.severity.upper(), 4))

    return SecurityOverviewResponse(
        total_findings=len(all_findings),
        severity_counts=sev_counts,
        category_counts=dict(cat_counts),
        findings=[SecurityFindingResponse.model_validate(f) for f in filtered_findings],
    )
