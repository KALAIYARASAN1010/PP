import os
import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Proposal, User, DecisionHistory
from ..schemas import (
    ProposalCreate, ProposalUpdate, ProposalResponse,
    LineageGraphResponse, ReviewerBriefResponse
)
from ..auth import get_current_user, require_roles
from ..audit import log_audit_event
from ..engine import precedent_engine
from ..pdf_utils import extract_text_from_pdf
from ..innovation import build_lineage_graph, generate_reviewer_brief
from ..config import settings

router = APIRouter(prefix="/api/proposals", tags=["Proposals"])

def generate_next_proposal_code(db: Session) -> str:
    current_year = datetime.now(timezone.utc).year
    prefix = f"PROP-{current_year}-"
    # Find max existing sequence for current year
    proposals = db.query(Proposal).filter(Proposal.proposal_code.like(f"{prefix}%")).all()
    max_seq = 0
    for p in proposals:
        try:
            seq = int(p.proposal_code.split("-")[-1])
            if seq > max_seq:
                max_seq = seq
        except ValueError:
            continue
    return f"{prefix}{max_seq + 1:04d}"

@router.get("", response_model=List[ProposalResponse])
def get_proposals(
    category: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    department: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Proposal)

    # Submitter can see all published/submitted proposals, but for drafts, only see own drafts
    if current_user.role == "Submitter":
        query = query.filter((Proposal.status != "Draft") | (Proposal.submitter_id == current_user.id))

    if category:
        query = query.filter(Proposal.category == category)
    if status_filter:
        query = query.filter(Proposal.status == status_filter)
    if department:
        query = query.filter(Proposal.department == department)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Proposal.title.ilike(search_fmt)) |
            (Proposal.proposal_code.ilike(search_fmt)) |
            (Proposal.description.ilike(search_fmt)) |
            (Proposal.justification.ilike(search_fmt))
        )

    proposals = query.order_by(Proposal.created_at.desc()).all()
    
    # Enrich submitter name & decisions reviewer name
    results = []
    for p in proposals:
        p_dict = ProposalResponse.model_validate(p)
        p_dict.submitter_name = p.submitter.full_name if p.submitter else "Unknown"
        for idx, dec in enumerate(p.decisions):
            if idx < len(p_dict.decisions):
                p_dict.decisions[idx].reviewer_name = dec.reviewer.full_name if dec.reviewer else "Unknown"
        results.append(p_dict)
    return results

@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
def create_proposal(
    prop_in: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only Submitter and Admin can create proposals
    if current_user.role not in {"Submitter", "Admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewers cannot directly author new proposals. Switch to a Submitter or Admin account."
        )

    code = generate_next_proposal_code(db)
    now = datetime.now(timezone.utc)

    # Parent proposal check if specified
    if prop_in.parent_proposal_id:
        parent = db.query(Proposal).filter(Proposal.id == prop_in.parent_proposal_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Specified parent proposal does not exist.")

    new_prop = Proposal(
        proposal_code=code,
        title=prop_in.title,
        description=prop_in.description,
        category=prop_in.category,
        department=prop_in.department,
        cost=prop_in.cost,
        justification=prop_in.justification,
        status=prop_in.status or "Draft",
        date=now,
        submitter_id=current_user.id,
        parent_proposal_id=prop_in.parent_proposal_id,
        document_ref=prop_in.document_ref,
        created_at=now,
        updated_at=now
    )
    db.add(new_prop)
    db.commit()
    db.refresh(new_prop)

    # Pre-index embedding vector
    corpus_text = f"{new_prop.title}. {new_prop.category} {new_prop.department}. {new_prop.description} {new_prop.justification}"
    emb = precedent_engine.encode(corpus_text)
    if emb:
        new_prop.embedding_json = json.dumps(emb)
        db.commit()

    # Immutable Audit Log
    log_audit_event(
        db=db,
        user_name=current_user.username,
        action="CREATE_PROPOSAL",
        entity_type="Proposal",
        entity_id=new_prop.proposal_code,
        details={
            "proposal_code": new_prop.proposal_code,
            "title": new_prop.title,
            "category": new_prop.category,
            "cost": new_prop.cost,
            "status": new_prop.status
        },
        user_id=current_user.id
    )

    resp = ProposalResponse.model_validate(new_prop)
    resp.submitter_name = current_user.full_name
    return resp

@router.get("/{id}", response_model=ProposalResponse)
def get_proposal(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prop = db.query(Proposal).filter(Proposal.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # If it's a draft and user is a Submitter who does not own it, disallow
    if prop.status == "Draft" and current_user.role == "Submitter" and prop.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to view other officers' unsubmitted drafts.")

    resp = ProposalResponse.model_validate(prop)
    resp.submitter_name = prop.submitter.full_name if prop.submitter else "Unknown"
    for idx, dec in enumerate(prop.decisions):
        if idx < len(resp.decisions):
            resp.decisions[idx].reviewer_name = dec.reviewer.full_name if dec.reviewer else "Unknown"
    return resp

@router.put("/{id}", response_model=ProposalResponse)
def update_proposal(
    id: int,
    prop_update: ProposalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prop = db.query(Proposal).filter(Proposal.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # RBAC & Status transition constraints:
    # Only submitter who authored it (or Admin) can edit, AND only if status is 'Draft' or 'Changes Requested'
    if current_user.role != "Admin":
        if prop.submitter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only edit your own proposals.")
        if prop.status not in {"Draft", "Changes Requested"}:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot edit proposal in '{prop.status}' status. Editing is only permitted for 'Draft' or 'Changes Requested'."
            )

    update_dict = prop_update.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(prop, field, val)

    prop.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(prop)

    # Re-index embedding if content changed
    corpus_text = f"{prop.title}. {prop.category} {prop.department}. {prop.description} {prop.justification}"
    emb = precedent_engine.encode(corpus_text)
    if emb:
        prop.embedding_json = json.dumps(emb)
        db.commit()

    log_audit_event(
        db=db,
        user_name=current_user.username,
        action="UPDATE_PROPOSAL",
        entity_type="Proposal",
        entity_id=prop.proposal_code,
        details={"updated_fields": list(update_dict.keys()), "proposal_code": prop.proposal_code},
        user_id=current_user.id
    )

    resp = ProposalResponse.model_validate(prop)
    resp.submitter_name = prop.submitter.full_name
    return resp

@router.post("/{id}/submit", response_model=ProposalResponse)
def submit_proposal(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prop = db.query(Proposal).filter(Proposal.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if current_user.role != "Admin" and prop.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only submit your own proposal.")

    if prop.status not in {"Draft", "Changes Requested"}:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: Cannot submit proposal with status '{prop.status}'. Must be 'Draft' or 'Changes Requested'."
        )

    previous_status = prop.status
    prop.status = "Submitted"
    prop.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(prop)

    log_audit_event(
        db=db,
        user_name=current_user.username,
        action="SUBMIT_PROPOSAL",
        entity_type="Proposal",
        entity_id=prop.proposal_code,
        details={"previous_status": previous_status, "new_status": "Submitted"},
        user_id=current_user.id
    )

    resp = ProposalResponse.model_validate(prop)
    resp.submitter_name = prop.submitter.full_name
    return resp

@router.post("/{id}/upload-pdf", response_model=ProposalResponse)
async def upload_pdf(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validates PDF, extracts text using pypdf, updates document reference,
    and updates indexed vector search corpus.
    """
    prop = db.query(Proposal).filter(Proposal.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if current_user.role != "Admin" and prop.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only attach documents to your own proposal.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files (.pdf) are supported.")

    file_bytes = await file.read()
    
    # Extract text with rigorous validation
    extracted_text = extract_text_from_pdf(file_bytes, filename=file.filename)

    # Save to uploads directory
    safe_filename = f"{prop.proposal_code}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    prop.document_ref = safe_filename
    prop.document_text = extracted_text
    prop.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(prop)

    # Recompute embedding including PDF extracted text
    augmented_corpus = f"{prop.title}. {prop.category} {prop.department}. {prop.description} {prop.justification} Document text: {extracted_text[:1500]}"
    emb = precedent_engine.encode(augmented_corpus)
    if emb:
        prop.embedding_json = json.dumps(emb)
        db.commit()

    log_audit_event(
        db=db,
        user_name=current_user.username,
        action="PDF_UPLOAD",
        entity_type="Proposal",
        entity_id=prop.proposal_code,
        details={
            "filename": file.filename,
            "file_size_bytes": len(file_bytes),
            "extracted_text_length": len(extracted_text)
        },
        user_id=current_user.id
    )

    resp = ProposalResponse.model_validate(prop)
    resp.submitter_name = prop.submitter.full_name
    return resp

@router.get("/{id}/lineage", response_model=LineageGraphResponse)
def get_proposal_lineage(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return build_lineage_graph(id, db)

@router.get("/{id}/brief", response_model=ReviewerBriefResponse)
def get_proposal_brief(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return generate_reviewer_brief(id, db)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
