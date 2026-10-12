# IPMPRS (Intelligent Proposal Management & Precedent Retrieval System)
## 3-Minute Hackathon Demonstration Script

### Act 1: Institutional Command Dashboard & Active Engine Telemetry (0:00 - 0:45)
1. **Show the Navbar & Active AI Engine**:
   - Point out the institutional dark green and navy design theme.
   - Point out the active engine badge in the top right: `Sentence Transformers (all-MiniLM-L6-v2)` (with automatic fallback to `TF-IDF Vectorizer`).
2. **Dashboard Real-Time Metrics**:
   - Show KPI cards computed live from the SQLite database:
     - 28 Total Proposals ($2,000,000+ requested)
     - 16 Approved ($980,000+ allocated, ~62% approval rate)
     - 7 Rejected
     - 3 Pending Review
     - 2 Changes Requested
   - Show Category breakdowns (Procurement, Operational, Infrastructure, Technical, Administrative) and Department expenditures.

---

### Act 2: Live Pre-Submission Precedent Synthesis & Innovations (0:45 - 1:45)
1. **Draft a New Proposal**:
   - Click **"Draft New Proposal"**.
   - Select Category: **Operational**, Department: **Tactical Response Unit**.
   - Type Title: `"Tactical Drone Unit with FLIR Thermal Cameras"`.
2. **Observe Live Innovation Features in Action**:
   - **Innovation A (Pre-submission Check)**: Live banner warns of historical near-duplicate `[PROP-2024-0010]` and summarizes how it ended: *Rejected: Lacks FAA night waiver authorization protocol*.
   - **Innovation D (Cost Benchmark & Outlier Detection)**: Enter cost `$145,000`. The engine flags: *"FLAGGED OUTLIER: Cost is 2.1x higher than category median ($68,000). Requires supervisory justification."*
   - **Innovation C (Rejection-Risk Checklist)**: Shows historical risks mined from actual rejected proposals in this category and provides concrete mitigations.
   - **Innovation E (Conflict Detector)**: Alerts to contradictory precedents in surveillance and tactical deployments.
3. **Compare Side-by-Side (Core 3)**:
   - Click **"Compare Side-by-Side"** on the retrieved precedent card to view a clean two-column comparison modal with cost variance and decision rationale.
4. **Submit Proposal**:
   - Click **"Submit for Command Review"**.

---

### Act 3: Reviewer Adjudication, RBAC, Printable Dossier & SHA-256 Audit (1:45 - 3:00)
1. **Demonstrate Conflict of Interest RBAC (Core 5)**:
   - Notice that Submitter *Officer Marcus Chen* cannot approve their own proposal.
   - Use the **Role Switcher** in the top bar to switch to **Captain David Miller (Reviewer)**.
2. **Innovation B (Printable Reviewer Brief)**:
   - Click **"Reviewer Brief (1-Page)"**.
   - Displays a structured, source-cited executive dossier synthesizing the proposal, cited precedents, cost benchmark, and signature block.
   - Click **"Print Brief"** to show the print preview.
3. **Innovation F (Resubmission Lineage Graph)**:
   - Open proposal `[PROP-2024-0003]` and click **"Resubmission Lineage"**.
   - Shows the 3-iteration tree: `PROP-2023-0002 (Rejected)` &rarr; `PROP-2023-0018 (Changes Requested)` &rarr; `PROP-2024-0003 (Approved)`.
4. **Adjudicate with Mandatory Rationale (Core 4)**:
   - Enter determination: **Approved** with rationale: *"Meets all tactical safety standards with grant co-sponsorship."*
   - Submit decision; watch it append immutably to the history log.
5. **Core 6 (Cryptographic SHA-256 Audit Trail & Tamper Detection)**:
   - Switch role to **Administrator Aarav Patel (Admin)** and navigate to **Audit Trail & Integrity**.
   - View the forensic ledger with chained hashes `hash = SHA-256(prev_hash + ...)`.
   - Click **"Verify Chain Integrity"** &rarr; Shows green confirmation: *Cryptographic Integrity Verified: All records intact*.
   - Click **"Simulate Tamper (Demo Test)"** to mutate an entry in SQLite without changing the hash.
   - Click **"Verify Chain Integrity"** again &rarr; Catches the corruption instantly, displaying: *TAMPERING DETECTED: Tampered content at record #X!*
