import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Proposal, User
from ..schemas import (
    PrecedentSearchQuery, PrecedentSearchResponse, PrecedentResultItem,
    DuplicateCheckResponse, RiskChecklistResponse, CostBenchmarkResponse,
    ConflictAlertResponse, SideBySideResponse, SideBySideItem
)
from ..auth import get_current_user
from ..engine import precedent_engine, extract_keywords
from ..innovation import (
    check_pre_submission_duplicates, mine_rejection_risks,
    benchmark_cost_against_precedents, detect_precedent_conflicts
)

router = APIRouter(prefix="/api/precedents", tags=["Precedent Retrieval"])

@router.post("/search", response_model=PrecedentSearchResponse)
def search_precedents(
    search_query: PrecedentSearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Proposal)

    # Metadata filtering
    if search_query.category:
        query = query.filter(Proposal.category == search_query.category)
    if search_query.department:
        query = query.filter(Proposal.department == search_query.department)
    if search_query.status:
        query = query.filter(Proposal.status == search_query.status)
    if search_query.min_cost is not None:
        query = query.filter(Proposal.cost >= search_query.min_cost)
    if search_query.max_cost is not None:
        query = query.filter(Proposal.cost <= search_query.max_cost)

    candidates = query.all()
    if not candidates:
        return PrecedentSearchResponse(
            results=[],
            active_engine=precedent_engine.active_engine,
            total_candidates=0,
            query=search_query.query,
            strong_precedent_count=0,
            warning_message="No historical records match the applied metadata filters."
        )

    cand_dicts = []
    for c in candidates:
        last_decision = c.decisions[-1] if c.decisions else None
        # Never invent missing decisions or reasons!
        cand_dicts.append({
            "id": c.id,
            "proposal_code": c.proposal_code,
            "title": c.title,
            "category": c.category,
            "department": c.department,
            "cost": c.cost,
            "date": c.date,
            "decision": last_decision.action if last_decision else None,
            "reason": last_decision.reason if last_decision else None,
            "corpus_text": f"{c.title}. {c.category} {c.department}. {c.description} {c.justification} {c.document_text or ''}",
            "embedding": json.loads(c.embedding_json) if c.embedding_json else None,
            "implementation_outcome": c.implementation_outcome,
            "lessons_learned": c.lessons_learned
        })

    effective_threshold = search_query.threshold if search_query.threshold is not None else 0.35
    raw_results = precedent_engine.compute_similarity(
        query=search_query.query,
        proposals_data=cand_dicts,
        threshold=effective_threshold,
        top_k=search_query.top_k or 5
    )

    strong_count = sum(1 for r in raw_results if r["is_strong_precedent"])
    warning = None
    if strong_count == 0 and len(raw_results) > 0:
        warning = f"No strong precedent found matching query above similarity threshold ({int(effective_threshold*100)}%). Showing closest available institutional precedents."

    return PrecedentSearchResponse(
        results=[PrecedentResultItem(**r) for r in raw_results],
        active_engine=precedent_engine.active_engine,
        total_candidates=len(candidates),
        query=search_query.query,
        strong_precedent_count=strong_count,
        warning_message=warning
    )

@router.post("/check-duplicates", response_model=DuplicateCheckResponse)
def check_duplicates(
    title: str = Query(..., min_length=2),
    description: str = Query("", min_length=0),
    category: str = Query("Procurement"),
    current_proposal_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """INNOVATION A: Pre-submission live duplicate warning."""
    return check_pre_submission_duplicates(
        title=title,
        description=description,
        category=category,
        db=db,
        threshold=0.45,
        current_proposal_id=current_proposal_id
    )

@router.get("/risk-checklist", response_model=RiskChecklistResponse)
def get_risk_checklist(
    category: str = Query(..., min_length=2),
    description: str = Query("", min_length=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """INNOVATION C: Rejection-risk checklist mined from past rejections."""
    return mine_rejection_risks(category=category, description=description, db=db)

@router.get("/cost-benchmark", response_model=CostBenchmarkResponse)
def get_cost_benchmark(
    cost: float = Query(..., ge=0.0),
    category: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """INNOVATION D: Cost benchmark vs similar precedents."""
    return benchmark_cost_against_precedents(cost=cost, category=category, db=db)

@router.get("/conflicts", response_model=ConflictAlertResponse)
def get_conflicts(
    category: str = Query(..., min_length=2),
    description: str = Query("", min_length=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """INNOVATION E: Conflict detector for precedents with opposite outcomes."""
    return detect_precedent_conflicts(category=category, description=description, db=db)

@router.get("/side-by-side/{current_id}/{precedent_id}", response_model=SideBySideResponse)
def get_side_by_side_comparison(
    current_id: int,
    precedent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Side-by-side comparison between draft/proposal and a historical precedent."""
    p1 = db.query(Proposal).filter(Proposal.id == current_id).first()
    p2 = db.query(Proposal).filter(Proposal.id == precedent_id).first()

    if not p1 or not p2:
        raise HTTPException(status_code=404, detail="One or both proposals not found for comparison.")

    d1 = p1.decisions[-1] if p1.decisions else None
    d2 = p2.decisions[-1] if p2.decisions else None

    # Overlapping key terms
    kw1 = set(extract_keywords(f"{p1.title} {p1.description} {p1.justification}"))
    kw2 = set(extract_keywords(f"{p2.title} {p2.description} {p2.justification}"))
    overlap = sorted(list(kw1.intersection(kw2)))

    cost_diff = round(p1.cost - p2.cost, 2)
    ratio = round((p1.cost / p2.cost), 2) if p2.cost > 0 else 1.0

    return SideBySideResponse(
        current=SideBySideItem(
            proposal_code=p1.proposal_code,
            title=p1.title,
            category=p1.category,
            department=p1.department,
            cost=p1.cost,
            justification=p1.justification,
            description=p1.description,
            status=p1.status,
            decision=d1.action if d1 else None,
            reason=d1.reason if d1 else None,
            implementation_outcome=p1.implementation_outcome,
            lessons_learned=p1.lessons_learned
        ),
        precedent=SideBySideItem(
            proposal_code=p2.proposal_code,
            title=p2.title,
            category=p2.category,
            department=p2.department,
            cost=p2.cost,
            justification=p2.justification,
            description=p2.description,
            status=p2.status,
            decision=d2.action if d2 else None,
            reason=d2.reason if d2 else None,
            implementation_outcome=p2.implementation_outcome,
            lessons_learned=p2.lessons_learned
        ),
        cost_difference=cost_diff,
        cost_ratio=ratio,
        key_overlap_terms=overlap[:10],
        structural_comparison={
            "same_category": p1.category == p2.category,
            "same_department": p1.department == p2.department,
            "cost_delta_percentage": round(((p1.cost - p2.cost) / (p2.cost or 1.0)) * 100, 1),
            "precedent_outcome_badge": d2.action if d2 else "No Decision Recorded"
        }
    )
