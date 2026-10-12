# IPMPRS (Intelligent Proposal Management & Precedent Retrieval System)

An AI-enabled municipal proposal lifecycle management and institutional knowledge retrieval platform built specifically for police and law enforcement departments.

---

## 🚔 System Overview

Police departments routinely face recurring proposal submissions, lost institutional memory from personnel turnover, inconsistent committee determinations, and unbenchmarked capital expenditures. 

**IPMPRS** solves this by providing:
- **Instant Precedent Retrieval**: Blends dense semantic vector embeddings (`all-MiniLM-L6-v2`) with lexical TF-IDF token matching and departmental metadata filtering.
- **Fail-Safe AI Telemetry**: Loads Sentence Transformers once on startup with zero-latency caching, with automatic fallback to Scikit-Learn TF-IDF vectorizer if offline.
- **Strict Role-Based Access Control (RBAC)**: Enforces separation of duties—reviewers cannot review their own proposals; submitters cannot decide; and AI never adjudicates.
- **Cryptographic Auditability**: Every proposal event, document upload, and adjudication action is appended to a SHA-256 chained ledger with one-click cryptographic tamper detection.
- **Proactive Innovations**: Live pre-submission duplicate warning, one-page printable reviewer briefings, rejection-risk mining, cost outlier benchmarking, and resubmission lineage trees.

---

## 🛠 Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18 / 19, Vite, Lucide-React icons, responsive institutional CSS theme (Dark Green `#1b4332`, Deep Navy `#0f172a`, White `#ffffff`, Light Gray `#f8fafc`). |
| **Backend** | FastAPI (Python 3.13), SQLAlchemy ORM, Pydantic v2, PyJWT for authentication. |
| **Database** | SQLite with auto-seeded dataset of 28 fictional police proposals. |
| **AI / NLP** | `sentence-transformers/all-MiniLM-L6-v2` with Scikit-Learn TF-IDF vectorizer fallback. |
| **Document Processing** | `pypdf` for parsing, page-by-page text extraction, magic-byte header validation, and corruption handling. |
| **Cryptography** | SHA-256 append-only chained audit log (`GENESIS_HASH` &rarr; record `n`). |

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13.1)
- Node.js 18+ (tested on Node.js v24.14.0)

### 2. Backend Setup
```bash
# Clone / navigate to project root
cd kvn

# Install Python backend dependencies
pip install -r backend/requirements.txt

# Run pytest test suite to verify all 21 tests pass
python -m pytest backend/tests -v

# Start FastAPI backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
```bash
# In a separate terminal, navigate to frontend
cd frontend

# Install dependencies (already prepared)
npm install

# Start Vite development server
npm run dev
```

*Open your browser at `http://localhost:5173` (or `http://localhost:8000` for the unified production bundle).*

---

## 👥 Seeded Personas & Role Switcher

The database automatically seeds 5 default departmental personnel with password `Password123!`:

| Username | Role | Department | Badge | Duties |
|---|---|---|---|---|
| `officer_chen` | **Submitter** | Patrol Operations | #4402 | Authors initiatives, views own drafts, runs live pre-submission checks. |
| `officer_rodriguez` | **Submitter** | Forensics & Cyber Crimes | #5120 | Authors technical and cyber infrastructure proposals. |
| `captain_miller` | **Reviewer** | Internal Affairs & Oversight | #1088 | Adjudicates submitted proposals; cannot review own submissions. |
| `commander_hayes` | **Reviewer** | Executive Review Bureau | #0421 | Evaluates high-value capital procurements and grants. |
| `admin_patel` | **Admin** | IT & Police Administration | #0012 | System maintenance, cryptographic audit verification, user administration. |

*Use the **ROLE SWITCHER** in the top navigation bar to toggle between roles with 1 click.*

---

## 🧪 Comprehensive Pytest Suite

Run the full automated test suite:
```bash
python -m pytest backend/tests -v
```

### Test Coverage Highlights:
- `test_proposals.py`: Auto-ID code formatting (`PROP-YYYY-XXXX`), field validation (negative cost, invalid categories), SQLite persistence, state transitions.
- `test_search.py`: Hybrid semantic search structure, legal disclaimer validation, non-hallucination test (never inventing missing decisions), paraphrased query test, irrelevant query low similarity test, live duplicate detection.
- `test_rbac.py`: Mandatory written rationale validation, Submitter rejection from workflow decisions, Reviewer conflict of interest prevention (reviewers cannot approve own proposals), separation of duties.
- `test_audit.py`: Cryptographic SHA-256 chain verification, tamper detection algorithm (detecting unauthorized SQLite row mutation), Admin-only verification access.
- `test_pdf.py`: Empty (0-byte) PDF upload rejection, corrupted header rejection, valid PDF in-memory extraction and vector indexing.

---

## 🏆 Innovation Features (Priority Order)

- **a. Pre-submission Check**: Live duplicate detection as the officer types, warning if near-duplicates exist and summarizing how historical proposals concluded.
- **b. Reviewer Brief**: Printable, one-page executive dossier synthesized strictly from stored database records, with precedent citations, cost benchmarks, and signature lines (`window.print()`).
- **c. Rejection-Risk Checklist**: Mines past rejection rationales across matching proposal categories to provide actionable mitigation guidance before submission.
- **d. Cost Benchmark**: Calculates category median, mean, and z-score, flagging fiscal outliers exceeding 1.75 standard deviations.
- **e. Conflict Detector**: Identifies historical precedents with conflicting decisions on overlapping subjects.
- **f. Resubmission Lineage Timeline**: DAG graph tracking proposals through iterative revisions, parent links, and final resolution.
- **g. Implementation Outcomes**: Surfaces post-deployment field results and operational lessons learned on precedent cards.
- **h. Bottleneck Analytics**: Empirically computes time spent in each lifecycle status and flags SLA breaches (>14 days in review).

---

## 📋 Final Feature Verification Table

| Module | Feature | Status | Notes |
|---|---|---|---|
| **Core 1** | Dashboard (live DB metrics & charts) | **Working** | Total, Approved, Rejected, Pending, Changes Requested, Category & Dept distributions. |
| **Core 2** | Proposals CRUD & State Machine | **Working** | Auto-ID `PROP-2026-XXXX`, validation for cost/category/status, SQLite persistence. |
| **Core 3** | Hybrid Precedent Retrieval | **Working** | Cosine similarity + token match + metadata filters; disclaimer; threshold warnings. |
| **Core 3** | Side-by-Side Comparison | **Working** | Two-column modal highlighting cost delta, ratio, and decision rationale. |
| **Core 4** | Workflow Adjudication | **Working** | Approve/Reject/Request Changes with mandatory rationale; append-only history. |
| **Core 5** | RBAC Enforcement (403 on violation) | **Working** | Reviewers barred from self-review; Submitters barred from deciding. |
| **Core 6** | Append-Only SHA-256 Audit Trail | **Working** | Chained hashes; Admin "Verify Integrity" & "Simulate Tamper" demo utilities. |
| **Core 7** | PDF Upload & Ingestion | **Working** | Parsed with `pypdf`, validated magic bytes, indexed into search engine. |
| **Core 8** | 25+ Fictional Police Proposals Dataset | **Working** | 28 rich fictional proposals with conflicts, near-duplicates, and resubmission chains. |
| **Inno A** | Pre-Submission Check | **Working** | Live duplicate check while drafting with historical outcome summaries. |
| **Inno B** | One-Page Reviewer Brief | **Working** | Stored citations, cost benchmark, risk factors, printable dossier (`window.print`). |
| **Inno C** | Rejection-Risk Checklist | **Working** | Category-mined historical rejection patterns and suggested mitigations. |
| **Inno D** | Cost Outlier Benchmark | **Working** | Z-score, median, mean, and outlier alerts vs category precedents. |
| **Inno E** | Precedent Conflict Detector | **Working** | Flags divergent determinations on overlapping scopes. |
| **Inno F** | Lineage Timeline / Graph | **Working** | Tracks resubmission chains from genesis proposal to final approval. |
| **Inno G** | Implementation Outcomes in Precedents | **Working** | Field results & lessons learned surfaced in search cards and comparisons. |
| **Inno H** | Bottleneck & SLA Analytics | **Working** | Stage turnaround times, SLA threshold breaches (>14 days), longest stalled dossier. |

---

## ⚠️ Troubleshooting & Limitations

- **Model Download on Offline Networks**: If the machine has no internet connection, the system automatically falls back to Scikit-Learn TF-IDF vectorization with 0 configuration needed. The active engine badge in the top bar will display `TF-IDF Vectorizer (Scikit-Learn Fallback)`.
- **Scanned Image PDFs without OCR**: `pypdf` extracts text layers from digital PDFs. If a user uploads a pure raster-scanned image PDF with no text layer, `pypdf` marks it with a note `[PDF uploaded: scanned/empty text layer detected]`.
- **SQLite Single-File Storage**: Default database uses SQLite (`ipmprs.db`). For multi-server enterprise clustering, set `DATABASE_URL=postgresql://...` in `.env`.
