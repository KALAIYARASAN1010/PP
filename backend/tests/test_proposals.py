import pytest

def test_proposal_creation_and_auto_id(client, submitter_headers):
    """Test proposal creation generates valid auto ID (PROP-YYYY-XXXX) and returns 201."""
    payload = {
        "title": "Automated Traffic Signal Priority for Emergency Response",
        "description": "Installation of optical and GPS-based preemption emitters on 30 frontline police cruisers.",
        "category": "Operational",
        "department": "Traffic Division",
        "cost": 45000.0,
        "justification": "Reduces critical emergency intersection transit time by an estimated 25 seconds per call.",
        "status": "Draft"
    }
    response = client.post("/api/proposals", json=payload, headers=submitter_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "Draft"
    assert data["cost"] == 45000.0
    assert "PROP-" in data["proposal_code"]
    assert len(data["proposal_code"].split("-")) == 3

def test_proposal_validation_negative_cost(client, submitter_headers):
    """Test that negative cost is rejected with validation error."""
    payload = {
        "title": "Invalid Negative Cost Proposal",
        "description": "Detailed description of a proposal with negative funding amount.",
        "category": "Administrative",
        "department": "Patrol Operations",
        "cost": -5000.0,
        "justification": "This should fail validation because funding cannot be negative."
    }
    response = client.post("/api/proposals", json=payload, headers=submitter_headers)
    assert response.status_code == 422

def test_proposal_validation_invalid_category(client, submitter_headers):
    """Test that disallowed category is rejected."""
    payload = {
        "title": "Invalid Category Proposal",
        "description": "Proposal with unsupported category name.",
        "category": "UnicornManagement",
        "department": "Patrol Operations",
        "cost": 10000.0,
        "justification": "Should fail because category is not in allowed enum."
    }
    response = client.post("/api/proposals", json=payload, headers=submitter_headers)
    assert response.status_code == 422

def test_proposal_persistence_and_retrieval(client, submitter_headers):
    """Test persistence: newly created proposal persists and is retrievable."""
    payload = {
        "title": "Persistent Surveillance Tower Test Proposal",
        "description": "Temporary deployment of solar-powered security observation platform.",
        "category": "Operational",
        "department": "Patrol Operations",
        "cost": 27500.0,
        "justification": "Testing data persistence across lifecycle requests in the SQLite database."
    }
    create_resp = client.post("/api/proposals", json=payload, headers=submitter_headers)
    assert create_resp.status_code == 201
    prop_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/proposals/{prop_id}", headers=submitter_headers)
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == prop_id
    assert fetched["title"] == payload["title"]
    assert fetched["cost"] == 27500.0

def test_proposal_submission_transition(client, submitter_headers):
    """Test transitioning a Draft proposal to Submitted status."""
    payload = {
        "title": "Draft Transition Ready Proposal",
        "description": "Draft proposal that will be submitted for command evaluation.",
        "category": "Administrative",
        "department": "Training Division",
        "cost": 12000.0,
        "justification": "Pre-submission state machine test.",
        "status": "Draft"
    }
    create_resp = client.post("/api/proposals", json=payload, headers=submitter_headers)
    prop_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "Draft"

    submit_resp = client.post(f"/api/proposals/{prop_id}/submit", headers=submitter_headers)
    assert submit_resp.status_code == 200
    assert submit_resp.json()["status"] == "Submitted"
