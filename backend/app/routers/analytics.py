from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Proposal, DecisionHistory, User
from ..schemas import BottleneckAnalyticsResponse, ProposalResponse
from ..auth import get_current_user
from ..engine import precedent_engine
from ..innovation import compute_bottleneck_analytics

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Dashboard"])

@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Computes all dashboard operational statistics, metrics, and chart series directly from the database.
    No hardcoded stats or mock data.
    """
    proposals = db.query(Proposal).all()
    
    total = len(proposals)
    approved = sum(1 for p in proposals if p.status == "Approved")
    rejected = sum(1 for p in proposals if p.status == "Rejected")
    pending = sum(1 for p in proposals if p.status in {"Submitted", "Under Review"})
    changes_requested = sum(1 for p in proposals if p.status == "Changes Requested")
    draft = sum(1 for p in proposals if p.status == "Draft")
    closed = sum(1 for p in proposals if p.status == "Closed")

    total_cost = sum(p.cost for p in proposals)
    approved_cost = sum(p.cost for p in proposals if p.status == "Approved")
    pending_cost = sum(p.cost for p in proposals if p.status in {"Submitted", "Under Review"})

    # Breakdown by Category
    category_map = {}
    for p in proposals:
        cat = p.category
        if cat not in category_map:
            category_map[cat] = {"category": cat, "count": 0, "total_cost": 0.0, "approved_count": 0}
        category_map[cat]["count"] += 1
        category_map[cat]["total_cost"] += p.cost
        if p.status == "Approved":
            category_map[cat]["approved_count"] += 1

    # Breakdown by Department
    dept_map = {}
    for p in proposals:
        dept = p.department
        if dept not in dept_map:
            dept_map[dept] = {"department": dept, "count": 0, "total_cost": 0.0}
        dept_map[dept]["count"] += 1
        dept_map[dept]["total_cost"] += p.cost

    # Recent proposals (last 6)
    recent = (
        db.query(Proposal)
        .order_by(Proposal.created_at.desc())
        .limit(6)
        .all()
    )
    recent_list = []
    for r in recent:
        item = ProposalResponse.model_validate(r)
        item.submitter_name = r.submitter.full_name if r.submitter else "Unknown"
        recent_list.append(item)

    return {
        "summary": {
            "total_proposals": total,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "changes_requested": changes_requested,
            "draft": draft,
            "closed": closed,
            "total_funding_requested": round(total_cost, 2),
            "approved_funding": round(approved_cost, 2),
            "pending_funding": round(pending_cost, 2),
            "approval_rate_percent": round((approved / (approved + rejected) * 100), 1) if (approved + rejected) > 0 else 0.0
        },
        "by_category": list(category_map.values()),
        "by_department": list(dept_map.values()),
        "recent_proposals": recent_list,
        "engine_telemetry": {
            "active_engine": precedent_engine.active_engine,
            "is_semantic": precedent_engine.is_semantic,
            "model_name": precedent_engine.model_name
        }
    }

@router.get("/bottlenecks", response_model=BottleneckAnalyticsResponse)
def get_bottlenecks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """INNOVATION H: Bottleneck analytics (time per status, SLA breaches)."""
    return compute_bottleneck_analytics(db)

@router.get("/engine-status")
def get_engine_status():
    """Returns active AI precedent retrieval engine status."""
    return {
        "active_engine": precedent_engine.active_engine,
        "is_semantic": precedent_engine.is_semantic,
        "model_name": precedent_engine.model_name,
        "status": "Healthy & Online"
    }
