import io
import pytest
from pypdf import PdfWriter

def test_empty_pdf_upload_rejected(client, submitter_headers):
    """Test that a 0-byte empty file is rejected with 400 Bad Request."""
    empty_content = b""
    files = {"file": ("empty.pdf", empty_content, "application/pdf")}
    resp = client.post("/api/proposals/1/upload-pdf", files=files, headers=submitter_headers)
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"].lower()

def test_corrupt_pdf_upload_rejected(client, submitter_headers):
    """Test that corrupted non-PDF bytes are rejected with 400 Bad Request."""
    corrupt_content = b"This is clearly not a real PDF file header."
    files = {"file": ("fake.pdf", corrupt_content, "application/pdf")}
    resp = client.post("/api/proposals/1/upload-pdf", files=files, headers=submitter_headers)
    assert resp.status_code == 400
    assert "valid pdf header" in resp.json()["detail"].lower()

def test_valid_pdf_text_extraction_and_indexing(client, submitter_headers, db_session):
    """Test that a valid PDF is successfully parsed, text extracted, and indexed."""
    from backend.app.models import Proposal, User
    chen = db_session.query(User).filter(User.username == "officer_chen").first()
    
    # Create proposal owned by officer_chen
    prop = Proposal(
        proposal_code="PROP-TEST-PDF",
        title="PDF Attachment Ingestion Test",
        description="Testing PDF document text extraction and vector indexing.",
        category="Technical",
        department="Patrol Operations",
        cost=15000.0,
        justification="Legitimate test justification.",
        status="Draft",
        submitter_id=chen.id
    )
    db_session.add(prop)
    db_session.commit()
    db_session.refresh(prop)

    # Generate a genuine minimal PDF in memory using pypdf PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    # Write page with text
    stream = io.BytesIO()
    writer.write(stream)
    valid_pdf_bytes = stream.getvalue()

    files = {"file": ("specifications.pdf", valid_pdf_bytes, "application/pdf")}
    resp = client.post(f"/api/proposals/{prop.id}/upload-pdf", files=files, headers=submitter_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["document_ref"] is not None
    assert "specifications.pdf" in data["document_ref"]
