import pytest
from backend.app.auth import create_access_token

def test_missing_reason_rejected(client, reviewer_headers):
    """Workflow decision without mandatory rationale returns 400 or 422 error."""
    payload = {
        "action": "Rejected",
        "reason": "   "  # Empty whitespace
    }
    # Proposal 1 is authored by officer_chen, so reviewer captain_miller can review it
    resp = client.post("/api/workflow/1/decide", json=payload, headers=reviewer_headers)
    assert resp.status_code in {400, 422}

def test_submitter_cannot_make_decisions(client, submitter_headers):
    """Enforce RBAC: Submitter cannot decide/approve/reject proposals (returns 403 Forbidden)."""
    payload = {
        "action": "Approved",
        "reason": "I am approving this proposal myself."
    }
    resp = client.post("/api/workflow/1/decide", json=payload, headers=submitter_headers)
    assert resp.status_code == 403
    assert "Forbidden" in resp.json()["detail"]

def test_reviewer_cannot_review_own_proposal(client, db_session):
    """Enforce RBAC: Reviewer cannot evaluate their own proposal (returns 403 Forbidden)."""
    from backend.app.models import User, Proposal

    # Get captain_miller (Reviewer)
    reviewer = db_session.query(User).filter(User.username == "captain_miller").first()
    rev_token = create_access_token({"sub": reviewer.username, "user_id": reviewer.id, "role": reviewer.role})
    headers = {"Authorization": f"Bearer {rev_token}"}

    # Create a proposal where submitter_id is captain_miller
    own_prop = Proposal(
        proposal_code="PROP-TEST-SELF",
        title="Reviewer Self-Authored Initiative",
        description="Initiative written by reviewer themselves.",
        category="Administrative",
        department="Internal Affairs & Oversight",
        cost=15000.0,
        justification="Test conflict of interest prevention.",
        status="Submitted",
        submitter_id=reviewer.id
    )
    db_session.add(own_prop)
    db_session.commit()
    db_session.refresh(own_prop)

    # Attempt to self-approve
    payload = {
        "action": "Approved",
        "reason": "Approving my own proposal without secondary oversight."
    }
    resp = client.post(f"/api/workflow/{own_prop.id}/decide", json=payload, headers=headers)
    assert resp.status_code == 403
    assert "Conflict of Interest" in resp.json()["detail"]

def test_reviewer_cannot_author_proposals(client, reviewer_headers):
    """Reviewers cannot author new proposals directly (enforces separation of duty)."""
    payload = {
        "title": "Reviewer Attempting To Author",
        "description": "Separation of concerns policy forbids reviewers from authoring.",
        "category": "Operational",
        "department": "Internal Affairs & Oversight",
        "cost": 25000.0,
        "justification": "Testing role restriction.",
        "status": "Draft"
    }
    resp = client.post("/api/proposals", json=payload, headers=reviewer_headers)
    assert resp.status_code == 403

def test_reviewer_can_decide_other_officer_proposal(client, reviewer_headers, db_session):
    """Reviewer successfully approves an eligible proposal from another officer with mandatory reason."""
    from backend.app.models import Proposal, User
    chen = db_session.query(User).filter(User.username == "officer_chen").first()
    
    # Create submitted proposal by officer_chen
    prop = Proposal(
        proposal_code="PROP-TEST-REVIEW-OK",
        title="Valid Proposal Eligible For Captain Review",
        description="Legitimate proposal awaiting review.",
        category="Operational",
        department="Patrol Operations",
        cost=18000.0,
        justification="Legitimate test justification.",
        status="Submitted",
        submitter_id=chen.id
    )
    db_session.add(prop)
    db_session.commit()
    db_session.refresh(prop)

    payload = {
        "action": "Approved",
        "reason": "Proposal satisfies departmental fiscal criteria and patrol operational safety."
    }
    resp = client.post(f"/api/workflow/{prop.id}/decide", json=payload, headers=reviewer_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["action"] == "Approved"
    assert data["new_status"] == "Approved"
