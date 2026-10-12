import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from .models import AuditLog

GENESIS_HASH = "0" * 64

def calculate_audit_hash(
    previous_hash: str,
    timestamp_iso: str,
    user_name: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details_json: str
) -> str:
    """Computes deterministic SHA-256 hash for an audit log entry."""
    payload = f"{previous_hash}|{timestamp_iso}|{user_name}|{action}|{entity_type}|{entity_id}|{details_json}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def log_audit_event(
    db: Session,
    user_name: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict,
    user_id: Optional[int] = None
) -> AuditLog:
    """Creates and appends an immutable audit log entry chained to previous hash."""
    # Retrieve the most recent audit entry to get previous_hash
    last_entry = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    previous_hash = last_entry.current_hash if last_entry else GENESIS_HASH

    now = datetime.now(timezone.utc)
    timestamp_iso = now.isoformat()
    details_str = json.dumps(details, sort_keys=True)

    current_hash = calculate_audit_hash(
        previous_hash=previous_hash,
        timestamp_iso=timestamp_iso,
        user_name=user_name,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details_json=details_str
    )

    audit_entry = AuditLog(
        timestamp=timestamp_iso,
        user_id=user_id,
        user_name=user_name,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        details_json=details_str,
        previous_hash=previous_hash,
        current_hash=current_hash
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry

def verify_audit_chain(db: Session) -> Tuple[bool, int, Optional[int], Optional[str]]:
    """
    Verifies the cryptographic SHA-256 chain of all audit entries.
    Returns: (is_valid, total_records, tampered_record_id, error_message)
    """
    records = db.query(AuditLog).order_by(AuditLog.id.asc()).all()
    if not records:
        return True, 0, None, None

    expected_prev = GENESIS_HASH
    for record in records:
        # Check 1: verify linkage to previous hash
        if record.previous_hash != expected_prev:
            return (
                False,
                len(records),
                record.id,
                f"Broken hash chain at record #{record.id}: previous_hash '{record.previous_hash[:12]}...' does not match expected '{expected_prev[:12]}...'"
            )

        # Check 2: recompute current hash
        timestamp_iso = record.timestamp if isinstance(record.timestamp, str) else record.timestamp.isoformat()
        computed = calculate_audit_hash(
            previous_hash=record.previous_hash,
            timestamp_iso=timestamp_iso,
            user_name=record.user_name,
            action=record.action,
            entity_type=record.entity_type,
            entity_id=record.entity_id,
            details_json=record.details_json
        )

        if computed != record.current_hash:
            return (
                False,
                len(records),
                record.id,
                f"Tampered content at record #{record.id}: stored hash '{record.current_hash[:12]}...' does not match recomputed SHA-256 '{computed[:12]}...'"
            )

        expected_prev = record.current_hash

    return True, len(records), None, None
