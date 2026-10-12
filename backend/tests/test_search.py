import pytest

def test_precedent_search_structure_and_disclaimer(client, submitter_headers):
    """Test search response fields, top results, highlighted matches, and disclaimer."""
    query_payload = {
        "query": "Body worn camera procurement for patrol squad",
        "top_k": 5,
        "threshold": 0.35
    }
    response = client.post("/api/precedents/search", json=query_payload, headers=submitter_headers)
    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert "active_engine" in data
    assert "similarity_disclaimer" in data
    # Legal policy disclaimer asserting similarity != approval
    assert "NOT indicate approval probability" in data["similarity_disclaimer"]

    # Verify top result structure
    assert len(data["results"]) > 0
    top = data["results"][0]
    assert "id" in top
    assert "proposal_code" in top
    assert "title" in top
    assert "category" in top
    assert "department" in top
    assert "cost" in top
    assert "date" in top
    assert "source_link" in top
    assert "similarity_score" in top
    assert "highlighted_matches" in top
    assert "why_matched" in top
    assert isinstance(top["similarity_score"], float)

def test_search_never_invents_missing_decisions(client, submitter_headers):
    """Verify that proposals without decisions return decision=None and reason=None (never hallucinated)."""
    # Create proposal with NO decision
    new_prop = {
        "title": "Undecided Specialized Testing Asset Proposal",
        "description": "Brand new exploratory proposal with zero decisions recorded.",
        "category": "Technical",
        "department": "Forensics & Cyber Crimes",
        "cost": 15000.0,
        "justification": "Testing that retrieval never invents missing decisions.",
        "status": "Submitted"
    }
    create_resp = client.post("/api/proposals", json=new_prop, headers=submitter_headers)
    assert create_resp.status_code == 201

    search_payload = {
        "query": "Undecided Specialized Testing Asset Proposal",
        "top_k": 5
    }
    resp = client.post("/api/precedents/search", json=search_payload, headers=submitter_headers)
    assert resp.status_code == 200
    results = resp.json()["results"]
    matched = next((r for r in results if r["id"] == create_resp.json()["id"]), None)
    assert matched is not None
    # Must be None, never invented!
    assert matched["decision"] is None
    assert matched["reason"] is None

def test_paraphrased_query_semantic_retrieval(client, submitter_headers):
    """Test that paraphrased queries retrieve conceptually related precedents."""
    # Paraphrased terms: "uncrewed rotorcraft aerial FLIR night optics" for Drones
    query_payload = {
        "query": "uncrewed rotorcraft aerial infrared night optic surveillance",
        "top_k": 5,
        "threshold": 0.25
    }
    response = client.post("/api/precedents/search", json=query_payload, headers=submitter_headers)
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) > 0
    # At least one drone/aerial proposal in top matches
    drone_titles = [r["title"] for r in results if "Drone" in r["title"] or "Aerial" in r["title"] or "Quadcopters" in r["title"]]
    assert len(drone_titles) > 0

def test_irrelevant_query_low_similarity_and_warning(client, submitter_headers):
    """Test that completely irrelevant query has low similarity and triggers 'no strong precedent' warning."""
    query_payload = {
        "query": "strawberry shortcake baking pastry oven dessert recipe with whipped cream",
        "top_k": 5,
        "threshold": 0.50
    }
    response = client.post("/api/precedents/search", json=query_payload, headers=submitter_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["strong_precedent_count"] == 0
    # Must provide the explicit warning
    assert data["warning_message"] is not None
    assert "No strong precedent found" in data["warning_message"]

def test_pre_submission_duplicate_warning(client, submitter_headers):
    """Test Innovation A: Pre-submission check flags duplicate drone proposal."""
    dup_check = client.post(
        "/api/precedents/check-duplicates",
        params={
            "title": "Unmanned Aerial Surveillance Quadcopters for Tactical Operations",
            "description": "Acquisition of 4 high-end commercial quadcopters with 4K zoom cameras for barricaded suspects",
            "category": "Operational"
        },
        headers=submitter_headers
    )
    assert dup_check.status_code == 200
    data = dup_check.json()
    assert data["has_potential_duplicate"] is True
    assert data["highest_similarity"] >= 0.50
    assert len(data["duplicates"]) > 0
    assert "CRITICAL WARNING" in data["recommendation"] or "ADVISORY" in data["recommendation"]
