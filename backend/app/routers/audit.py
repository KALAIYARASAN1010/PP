from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuditLog, User
from ..schemas import AuditLogResponse, AuditVerifyResponse
from ..auth import require_roles
from ..audit import verify_audit_chain, calculate_audit_hash, GENESIS_HASH

router = APIRouter(prefix="/api/audit", tags=["Audit Trail"])

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Reviewer"]))
):
    """Retrieves all append-only audit entries sorted newest first."""
    return db.query(AuditLog).order_by(AuditLog.id.desc()).limit(100).all()

@router.get("/verify", response_model=AuditVerifyResponse)
def verify_integrity(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    """
    Cryptographically verifies the SHA-256 hash chain of all audit entries.
    Detects any database tampering, altered timestamps, or forged records.
    """
    is_valid, total_records, tampered_id, err_msg = verify_audit_chain(db)
    return AuditVerifyResponse(
        is_valid=is_valid,
        total_records=total_records,
        verified_at=datetime.now(timezone.utc),
        tampered_record_id=tampered_id,
        error_message=err_msg
    )

@router.post("/simulate-tamper")
def simulate_tamper(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    """
    ADMIN DEMO/TEST UTILITY: Intentionally mutates the content of an audit record
    without updating its cryptographic hash, to prove the SHA-256 chain detects tampering.
    """
    record = db.query(AuditLog).filter(AuditLog.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Audit record not found")

    # Tamper with details_json
    record.details_json = '{"FORGED_BY_UNAUTHORIZED_ACTOR": true, "tampered": "ALTERED_RECORD"}'
    db.commit()
    db.refresh(record)

    return {
        "status": "tampered",
        "record_id": record.id,
        "message": f"Record #{record.id} details have been intentionally altered. Run /api/audit/verify to observe cryptographic detection."
    }
