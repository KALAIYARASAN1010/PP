import pytest
from backend.app.models import AuditLog
from backend.app.audit import verify_audit_chain

def test_initial_audit_chain_validity(client, admin_headers, db_session):
    """Test that all seeded audit trail records pass SHA-256 cryptographic hash chain verification."""
    response = client.get("/api/audit/verify", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["total_records"] > 0
    assert data["tampered_record_id"] is None

def test_audit_chain_tamper_detection(client, admin_headers, db_session):
    """
    CRITICAL SECURITY TEST:
    Simulate database row tampering and verify that the SHA-256 chain detects corruption.
    """
    # 1. Verify chain is initially valid
    is_valid_before, total, _, _ = verify_audit_chain(db_session)
    assert is_valid_before is True
    assert total > 0

    # 2. Pick a middle audit record and illegally tamper with its stored content
    target_record = db_session.query(AuditLog).filter(AuditLog.id == 2).first()
    assert target_record is not None
    original_details = target_record.details_json

    # Tamper with the row directly in database
    target_record.details_json = '{"UNAUTHORIZED_SQL_INJECTION_TAMPER": "MODIFIED_PAYLOAD"}'
    db_session.commit()

    # 3. Verify that the verifier catches the tampering
    verify_resp = client.get("/api/audit/verify", headers=admin_headers)
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert data["is_valid"] is False
    assert data["tampered_record_id"] == 2
    assert "Tampered content at record #2" in data["error_message"]

    # Revert to prevent cascading test contamination
    target_record.details_json = original_details
    db_session.commit()

def test_submitter_cannot_access_audit_verify(client, submitter_headers):
    """Enforce RBAC: Non-admin users cannot access cryptographic verification endpoint."""
    resp = client.get("/api/audit/verify", headers=submitter_headers)
    assert resp.status_code == 403
