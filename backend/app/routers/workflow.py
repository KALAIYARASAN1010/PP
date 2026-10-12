from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Proposal, User, DecisionHistory
from ..schemas import DecisionCreate, DecisionResponse, ProposalResponse
from ..auth import get_current_user, require_roles
from ..audit import log_audit_event

router = APIRouter(prefix="/api/workflow", tags=["Workflow & Decisions"])

@router.post("/{proposal_id}/decide", response_model=DecisionResponse)
def make_decision(
    proposal_id: int,
    decision_in: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reviewer or Admin action: Approve, Reject, or Request Changes.
    AI NEVER DECIDES — Human officers only.
    Enforces RBAC:
    - Reviewers cannot review their own proposals (403 Forbidden).
    - Submitters cannot make workflow decisions (403 Forbidden).
    - Mandatory reason required (400 Bad Request if missing/trivial).
    """
    # RBAC 1: Must be Reviewer or Admin
    if current_user.role not in {"Reviewer", "Admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Submitter role is not authorized to adjudicate proposals."
        )

    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # RBAC 2: Reviewer CANNOT decide on their own proposal!
    if current_user.role == "Reviewer" and proposal.submitter_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conflict of Interest Violation: Reviewers are strictly prohibited from evaluating or deciding their own proposals."
        )

    # Mandatory Reason validation
    clean_reason = decision_in.reason.strip()
    if not clean_reason or len(clean_reason) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision rationale is mandatory. Please provide a substantive written justification (minimum 5 characters)."
        )

    # Valid state transition checks
    if proposal.status in {"Approved", "Rejected", "Closed"} and current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Proposal has already reached final determination status '{proposal.status}'. Further workflow actions require Admin override."
        )

    previous_status = proposal.status
    new_status = decision_in.action

    now = datetime.now(timezone.utc)

    # Append to append-only decision history
    decision = DecisionHistory(
        proposal_id=proposal.id,
        reviewer_id=current_user.id,
        action=decision_in.action,
        reason=clean_reason,
        previous_status=previous_status,
        new_status=new_status,
        created_at=now
    )
    db.add(decision)

    # Update proposal status
    proposal.status = new_status
    proposal.updated_at = now
    db.commit()
    db.refresh(decision)

    # SHA-256 chained audit event
    log_audit_event(
        db=db,
        user_name=current_user.username,
        action=f"DECISION_{decision_in.action.upper().replace(' ', '_')}",
        entity_type="Decision",
        entity_id=proposal.proposal_code,
        details={
            "proposal_id": proposal.id,
            "proposal_code": proposal.proposal_code,
            "previous_status": previous_status,
            "new_status": new_status,
            "decision_id": decision.id,
            "reason": clean_reason,
            "reviewer_badge": current_user.badge_number
        },
        user_id=current_user.id
    )

    resp = DecisionResponse.model_validate(decision)
    resp.reviewer_name = current_user.full_name
    return resp

@router.post("/{proposal_id}/under-review", response_model=ProposalResponse)
def mark_under_review(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Reviewer", "Admin"]))
):
    """Transitions a submitted proposal into Under Review."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if current_user.role == "Reviewer" and proposal.submitter_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conflict of Interest: You cannot review your own proposal."
        )

    if proposal.status != "Submitted":
        raise HTTPException(
            status_code=400,
            detail=f"Only proposals in 'Submitted' status can be moved to 'Under Review'. Current status is '{proposal.status}'."
        )

    proposal.status = "Under Review"
    proposal.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(proposal)

    log_audit_event(
        db=db,
        user_name=current_user.username,
        action="STATUS_UNDER_REVIEW",
        entity_type="Proposal",
        entity_id=proposal.proposal_code,
        details={"previous_status": "Submitted", "new_status": "Under Review"},
        user_id=current_user.id
    )

    resp = ProposalResponse.model_validate(proposal)
    resp.submitter_name = proposal.submitter.full_name if proposal.submitter else "Unknown"
    return resp
