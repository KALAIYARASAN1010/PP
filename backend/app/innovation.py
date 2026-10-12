import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session

from .models import Proposal, DecisionHistory
from .engine import precedent_engine, extract_keywords

def check_pre_submission_duplicates(
    title: str,
    description: str,
    category: str,
    db: Session,
    threshold: float = 0.50,
    current_proposal_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    INNOVATION A: Pre-submission check.
    Warns the officer of live duplicates and how similar historical proposals ended.
    """
    query_text = f"{title}. {category}. {description}"
    query = db.query(Proposal)
    if current_proposal_id:
        query = query.filter(Proposal.id != current_proposal_id)
    candidates = query.all()

    if not candidates:
        return {
            "has_potential_duplicate": False,
            "highest_similarity": 0.0,
            "duplicates": [],
            "recommendation": "No prior records exist for comparison."
        }

    # Format candidate corpus
    cand_dicts = []
    for c in candidates:
        last_dec = c.decisions[-1] if c.decisions else None
        cand_dicts.append({
            "id": c.id,
            "proposal_code": c.proposal_code,
            "title": c.title,
            "category": c.category,
            "department": c.department,
            "cost": c.cost,
            "date": c.date,
            "decision": last_dec.action if last_dec else None,
            "reason": last_dec.reason if last_dec else None,
            "corpus_text": f"{c.title}. {c.category} {c.department}. {c.description} {c.justification}",
            "embedding": json.loads(c.embedding_json) if c.embedding_json else None,
            "implementation_outcome": c.implementation_outcome,
            "lessons_learned": c.lessons_learned,
        })

    results = precedent_engine.compute_similarity(query_text, cand_dicts, threshold=threshold, top_k=3)
    duplicates = []
    highest_sim = 0.0

    for r in results:
        if r["similarity_score"] >= threshold:
            sim = r["similarity_score"]
            highest_sim = max(highest_sim, sim)
            outcome_text = f"Status: {r.get('decision') or 'In Progress'}"
            if r.get("reason"):
                outcome_text += f" — Note: {r['reason'][:90]}..."
            duplicates.append({
                "proposal_code": r["proposal_code"],
                "title": r["title"],
                "status": r.get("decision") or "Under Review",
                "similarity_score": sim,
                "decision": r.get("decision"),
                "outcome_summary": outcome_text
            })

    has_dup = len(duplicates) > 0
    rec = "Proceed with submission. No closely matching past proposal detected."
    if has_dup:
        if highest_sim >= 0.75:
            rec = "CRITICAL WARNING: High duplicate similarity detected! Check precedent outcomes and differentiate your justification before submitting to avoid rejection."
        else:
            rec = "ADVISORY: Related historical proposals found. Review cited past decisions to strengthen this proposal."

    return {
        "has_potential_duplicate": has_dup,
        "highest_similarity": round(highest_sim, 3),
        "duplicates": duplicates,
        "recommendation": rec
    }

def mine_rejection_risks(category: str, description: str, db: Session) -> Dict[str, Any]:
    """
    INNOVATION C: Rejection-risk checklist mined from past rejection reasons.
    Extracts patterns from actual rejected proposals in the database.
    """
    rejections = (
        db.query(DecisionHistory)
        .join(Proposal)
        .filter(DecisionHistory.action == "Rejected")
        .all()
    )

    risk_items = []
    category_rejections = [d for d in rejections if d.proposal.category == category]
    pool = category_rejections if category_rejections else rejections

    query_tokens = set(extract_keywords(description.lower()))

    for rej in pool:
        reason_text = rej.reason
        reason_lower = reason_text.lower()
        matched = False
        relevance = "Category-wide precedent rejection factor"
        mitigation = "Address this concern explicitly in your operational justification."

        if "budget" in reason_lower or "cost" in reason_lower or "quote" in reason_lower:
            mitigation = "Provide granular line-item quotes and identify federal/state grant co-sponsorship."
            matched = True
        elif "privacy" in reason_lower or "policy" in reason_lower or "civil liberties" in reason_lower:
            mitigation = "Attach legal compliance review and public privacy impact policy document."
            matched = True
        elif "staff" in reason_lower or "training" in reason_lower or "capacity" in reason_lower:
            mitigation = "Include dedicated certified instructor hours and shift staffing coverage plan."
            matched = True
        elif "maintenance" in reason_lower or "lifecycle" in reason_lower:
            mitigation = "Detail 3-year recurring maintenance warranty and vendor SLA terms."
            matched = True
        else:
            matched = True

        if matched:
            risk_items.append({
                "risk_title": f"Prior Decision: {rej.proposal.proposal_code}",
                "risk_category": rej.proposal.category,
                "past_rejection_reason": reason_text,
                "frequency_in_past_rejections": 1,
                "relevance_explanation": f"Proposal '{rej.proposal.title}' was rejected on this basis.",
                "mitigation_suggestion": mitigation
            })

    # Deduplicate / limit to top 4 most pertinent
    unique_risks = risk_items[:4]
    risk_level = "Elevated" if len(unique_risks) >= 3 else ("Moderate" if len(unique_risks) >= 1 else "Low")

    return {
        "category": category,
        "identified_risks": unique_risks,
        "overall_risk_level": risk_level
    }

def benchmark_cost_against_precedents(cost: float, category: str, db: Session) -> Dict[str, Any]:
    """
    INNOVATION D: Cost benchmark vs similar precedents with outlier detection.
    """
    proposals = db.query(Proposal).filter(Proposal.category == category).all()
    costs = [p.cost for p in proposals if p.cost > 0]

    if not costs:
        return {
            "requested_cost": cost,
            "category": category,
            "similar_proposals_count": 0,
            "benchmark_average": cost,
            "benchmark_median": cost,
            "benchmark_min": cost,
            "benchmark_max": cost,
            "z_score": 0.0,
            "is_outlier": False,
            "cost_assessment": "First proposal in category; baseline will be established."
        }

    arr = np.array(costs)
    avg = float(np.mean(arr))
    med = float(np.median(arr))
    min_c = float(np.min(arr))
    max_c = float(np.max(arr))
    std = float(np.std(arr)) if len(arr) > 1 else 1.0

    z_score = float((cost - avg) / (std if std > 0 else 1.0))
    is_outlier = z_score > 1.75 or (med > 0 and cost > 2.2 * med)

    if is_outlier:
            assessment = f"FLAGGED OUTLIER: Cost is {round(cost/med, 1) if med else 1}x higher than category median (₹{med:,.2f}). Requires senior supervisory fiscal justification."
    elif z_score > 0.8:
        assessment = f"ABOVE AVERAGE: Higher than {round(avg, 2):,.2f} departmental mean; review line-item procurement breakdown."
    elif z_score < -0.8:
            assessment = f"ECONOMICAL: Well below average category cost (₹{avg:,.2f}). Low budgetary resistance expected."
    else:
        assessment = f"STANDARD RANGE: Aligns closely with historical expenditure patterns for {category}."

    return {
        "requested_cost": cost,
        "category": category,
        "similar_proposals_count": len(costs),
        "benchmark_average": round(avg, 2),
        "benchmark_median": round(med, 2),
        "benchmark_min": round(min_c, 2),
        "benchmark_max": round(max_c, 2),
        "z_score": round(z_score, 2),
        "is_outlier": is_outlier,
        "cost_assessment": assessment
    }

def detect_precedent_conflicts(category: str, description: str, db: Session) -> Dict[str, Any]:
    """
    INNOVATION E: Conflict detector for precedents with opposite outcomes.
    Flags instances where similar topics resulted in contradictory decisions.
    """
    # Look for proposals in the same category where one was Approved and one was Rejected
    approved = (
        db.query(Proposal)
        .join(DecisionHistory)
        .filter(Proposal.category == category, DecisionHistory.action == "Approved")
        .all()
    )
    rejected = (
        db.query(Proposal)
        .join(DecisionHistory)
        .filter(Proposal.category == category, DecisionHistory.action == "Rejected")
        .all()
    )

    conflicts = []
    for app in approved:
        app_dec = [d for d in app.decisions if d.action == "Approved"][-1]
        for rej in rejected:
            rej_dec = [d for d in rej.decisions if d.action == "Rejected"][-1]
            
            # Check overlap between approved and rejected
            kw_app = set(extract_keywords(f"{app.title} {app.description}"))
            kw_rej = set(extract_keywords(f"{rej.title} {rej.description}"))
            overlap = kw_app.intersection(kw_rej)

            if len(overlap) >= 2:
                conflicts.append({
                    "approved_proposal_code": app.proposal_code,
                    "approved_title": app.title,
                    "approved_reason": app_dec.reason,
                    "rejected_proposal_code": rej.proposal_code,
                    "rejected_title": rej.title,
                    "rejected_reason": rej_dec.reason,
                    "topic_summary": f"Shared scope around: {', '.join(list(overlap)[:4])}",
                    "conflict_analysis": (
                        f"Precedent divergence detected: {app.proposal_code} was approved with rationale ('{app_dec.reason[:60]}...'), "
                        f"whereas {rej.proposal_code} was rejected ('{rej_dec.reason[:60]}...'). Reconcile requirements before final determination."
                    )
                })

    return {
        "has_conflicts": len(conflicts) > 0,
        "conflict_count": len(conflicts),
        "conflicts": conflicts[:3]
    }

def build_lineage_graph(proposal_id: int, db: Session) -> Dict[str, Any]:
    """
    INNOVATION F: Lineage timeline / graph (resubmissions, parent proposal).
    Walks parent and child relationships.
    """
    target = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not target:
        return {"nodes": [], "edges": [], "chain_length": 0}

    # Find root ancestor
    root = target
    while root.parent_proposal_id is not None:
        parent = db.query(Proposal).filter(Proposal.id == root.parent_proposal_id).first()
        if not parent or parent.id == root.id:
            break
        root = parent

    # Traverse all descendants from root
    visited_ids = set()
    nodes = []
    edges = []

    def traverse(p: Proposal):
        if p.id in visited_ids:
            return
        visited_ids.add(p.id)
        nodes.append({
            "id": p.id,
            "proposal_code": p.proposal_code,
            "title": p.title,
            "status": p.status,
            "date": p.date,
            "cost": p.cost,
            "is_current": (p.id == target.id)
        })
        children = db.query(Proposal).filter(Proposal.parent_proposal_id == p.id).all()
        for c in children:
            edges.append({
                "source_code": p.proposal_code,
                "target_code": c.proposal_code,
                "relationship": "Resubmission / Revision"
            })
            traverse(c)

    traverse(root)

    return {
        "nodes": nodes,
        "edges": edges,
        "chain_length": len(nodes)
    }

def generate_reviewer_brief(proposal_id: int, db: Session) -> Dict[str, Any]:
    """
    INNOVATION B: Reviewer brief (one-page, source-cited, built ONLY from stored data, printable).
    """
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise ValueError("Proposal not found")

    # Mined precedents
    corpus_text = f"{proposal.title}. {proposal.category} {proposal.department}. {proposal.description} {proposal.justification}"
    all_proposals = db.query(Proposal).filter(Proposal.id != proposal.id).all()
    cand_dicts = [{
        "id": c.id,
        "proposal_code": c.proposal_code,
        "title": c.title,
        "category": c.category,
        "department": c.department,
        "cost": c.cost,
        "date": c.date,
        "decision": c.decisions[-1].action if c.decisions else None,
        "reason": c.decisions[-1].reason if c.decisions else None,
        "corpus_text": f"{c.title}. {c.category} {c.department}. {c.description} {c.justification}",
        "embedding": json.loads(c.embedding_json) if c.embedding_json else None,
        "implementation_outcome": c.implementation_outcome,
        "lessons_learned": c.lessons_learned
    } for c in all_proposals]

    citations = precedent_engine.compute_similarity(corpus_text, cand_dicts, threshold=0.30, top_k=4)
    cost_bench = benchmark_cost_against_precedents(proposal.cost, proposal.category, db)
    risk_info = mine_rejection_risks(proposal.category, proposal.description, db)
    conflict_info = detect_precedent_conflicts(proposal.category, proposal.description, db)

    conflict_summary = None
    if conflict_info["has_conflicts"]:
        c = conflict_info["conflicts"][0]
        conflict_summary = f"Precedent conflict: {c['approved_proposal_code']} (Approved) vs {c['rejected_proposal_code']} (Rejected)."

    now = datetime.now(timezone.utc)

    # Printable HTML template
    printable_html = f"""
    <div class="brief-container" style="font-family: Arial, sans-serif; padding: 24px; color: #0f172a; max-width: 800px; margin: 0 auto;">
        <div style="border-bottom: 3px solid #1b4332; padding-bottom: 12px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <h1 style="color: #1b4332; margin: 0; font-size: 20pt; text-transform: uppercase; letter-spacing: 1px;">POLICE DEPARTMENT EXECUTIVE BRIEFING</h1>
                <p style="margin: 4px 0 0 0; color: #475569; font-size: 10pt;">OFFICIAL INSTITUTIONAL PROPOSAL EVALUATION DOSSIER</p>
            </div>
            <div style="text-align: right; font-size: 9pt; color: #64748b;">
                <strong>CLASSIFICATION:</strong> INTERNAL LAW ENFORCEMENT USE<br/>
                <strong>DOSSIER ID:</strong> {proposal.proposal_code}<br/>
                <strong>DATE:</strong> {now.strftime("%Y-%m-%d %H:%M UTC")}
            </div>
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; margin-bottom: 16px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 10pt;">
                <tr>
                    <td style="padding: 4px; font-weight: bold; width: 18%;">Title:</td>
                    <td style="padding: 4px;">{proposal.title}</td>
                    <td style="padding: 4px; font-weight: bold; width: 18%;">Category:</td>
                    <td style="padding: 4px;">{proposal.category}</td>
                </tr>
                <tr>
                    <td style="padding: 4px; font-weight: bold;">Department:</td>
                    <td style="padding: 4px;">{proposal.department}</td>
                    <td style="padding: 4px; font-weight: bold;">Requested Cost:</td>
                    <td style="padding: 4px; font-weight: bold; color: #1b4332;">₹{proposal.cost:,.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 4px; font-weight: bold;">Submitter:</td>
                    <td style="padding: 4px;">{proposal.submitter.full_name} (Badge #{proposal.submitter.badge_number})</td>
                    <td style="padding: 4px; font-weight: bold;">Current Status:</td>
                    <td style="padding: 4px;"><span style="background: #e2e8f0; padding: 2px 8px; border-radius: 4px;">{proposal.status}</span></td>
                </tr>
            </table>
        </div>

        <div style="margin-bottom: 14px;">
            <h3 style="color: #0f172a; margin: 0 0 6px 0; font-size: 11pt; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">1. OPERATIONAL SCOPE & JUSTIFICATION</h3>
            <p style="font-size: 9.5pt; line-height: 1.4; margin: 4px 0 8px 0;"><strong>Scope:</strong> {proposal.description}</p>
            <p style="font-size: 9.5pt; line-height: 1.4; margin: 4px 0 0 0;"><strong>Justification:</strong> {proposal.justification}</p>
        </div>

        <div style="margin-bottom: 14px;">
            <h3 style="color: #0f172a; margin: 0 0 6px 0; font-size: 11pt; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">2. COST BENCHMARK & ANOMALY ASSESSMENT</h3>
            <p style="font-size: 9.5pt; margin: 4px 0;">
                Category Median: <strong>₹{cost_bench['benchmark_median']:,.2f}</strong> | Mean: <strong>₹{cost_bench['benchmark_average']:,.2f}</strong> | Z-Score: <strong>{cost_bench['z_score']}</strong><br/>
                <em>{cost_bench['cost_assessment']}</em>
            </p>
        </div>

        <div style="margin-bottom: 14px;">
            <h3 style="color: #0f172a; margin: 0 0 6px 0; font-size: 11pt; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">3. PRECEDENT CITATIONS (DATA RETRIEVED FROM INSTITUTIONAL REPOSITORY)</h3>
            <div style="font-size: 9pt;">
                {''.join([f'''
                <div style="padding: 6px 0; border-bottom: 1px dashed #e2e8f0;">
                    <strong>[{c['proposal_code']}] {c['title']}</strong> (Match: {int(c['similarity_score']*100)}%)<br/>
                    Outcome: <strong>{c.get('decision') or 'Pending'}</strong> | Reason: <em>"{c.get('reason') or 'No decision recorded'}"</em><br/>
                    <span style="color: #475569;">Rationale overlap: {c['why_matched']}</span>
                </div>
                ''' for c in citations])}
            </div>
        </div>

        <div style="margin-bottom: 14px; background: #fffbeb; border: 1px solid #fef3c7; padding: 10px; border-radius: 4px;">
            <h3 style="color: #92400e; margin: 0 0 4px 0; font-size: 10pt;">4. HISTORICAL REJECTION RISK FACTORS IDENTIFIED</h3>
            <ul style="margin: 4px 0 0 16px; padding: 0; font-size: 8.5pt;">
                {''.join([f"<li><strong>{r['risk_title']}:</strong> {r['past_rejection_reason']} &rarr; <em>Mitigation: {r['mitigation_suggestion']}</em></li>" for r in risk_info['identified_risks']])}
            </ul>
        </div>

        <div style="margin-top: 24px; padding-top: 12px; border-top: 2px solid #0f172a; display: flex; justify-content: space-between; font-size: 9pt;">
            <div>
                <p style="margin: 0;"><strong>EVALUATING COMMANDER / REVIEWER:</strong> _______________________</p>
                <p style="margin: 4px 0 0 0;">SIGNATURE & BADGE: __________________________________</p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0;">DECISION: [ &nbsp; ] APPROVE &nbsp; [ &nbsp; ] REJECT &nbsp; [ &nbsp; ] CHANGES REQ.</p>
                <p style="margin: 4px 0 0 0;">DATE OF ACTION: ____________________</p>
            </div>
        </div>
    </div>
    """

    return {
        "brief_generated_at": now,
        "proposal_code": proposal.proposal_code,
        "title": proposal.title,
        "category": proposal.category,
        "department": proposal.department,
        "submitter_name": proposal.submitter.full_name,
        "cost": proposal.cost,
        "justification_summary": proposal.justification[:250] + ("..." if len(proposal.justification) > 250 else ""),
        "stored_citations": citations,
        "cost_benchmark_summary": cost_bench,
        "historical_risk_factors": [r["past_rejection_reason"] for r in risk_info["identified_risks"]],
        "conflict_summary": conflict_summary,
        "printable_formatted_html": printable_html
    }

def compute_bottleneck_analytics(db: Session) -> Dict[str, Any]:
    """
    INNOVATION H: Bottleneck analytics (time per status, SLA breaches).
    Calculates operational turnaround times and identifies stalled proposals.
    """
    all_proposals = db.query(Proposal).all()
    now = datetime.now(timezone.utc)

    # Status counts and ages
    status_counts = {}
    status_ages = {}
    sla_breaches = {}

    SLA_LIMITS = {
        "Draft": 30,
        "Submitted": 7,
        "Under Review": 14,  # SLA: reviews should conclude within 14 days
        "Changes Requested": 14,
        "Approved": 999,
        "Rejected": 999,
        "Closed": 999
    }

    stalled_candidate = None
    max_days_stalled = -1.0

    for p in all_proposals:
        st = p.status
        status_counts[st] = status_counts.get(st, 0) + 1
        
        # Calculate days in current status
        # If decisions exist, time since last decision, else time since created_at
        p_date = p.created_at
        if p.decisions:
            p_date = p.decisions[-1].created_at

        # Ensure tz-awareness
        if p_date.tzinfo is None:
            p_date = p_date.replace(tzinfo=timezone.utc)

        days = (now - p_date).total_seconds() / 86400.0
        days = max(0.0, days)

        if st not in status_ages:
            status_ages[st] = []
        status_ages[st].append(days)

        limit = SLA_LIMITS.get(st, 30)
        if days > limit and st in {"Submitted", "Under Review", "Changes Requested"}:
            sla_breaches[st] = sla_breaches.get(st, 0) + 1
            if days > max_days_stalled:
                max_days_stalled = days
                stalled_candidate = {
                    "proposal_code": p.proposal_code,
                    "title": p.title,
                    "status": p.status,
                    "days_in_status": round(days, 1),
                    "department": p.department,
                    "cost": p.cost
                }

    stages = []
    total_active = 0
    all_ages = []

    for status_name in ["Draft", "Submitted", "Under Review", "Changes Requested", "Approved", "Rejected", "Closed"]:
        cnt = status_counts.get(status_name, 0)
        ages = status_ages.get(status_name, [])
        avg_days = float(np.mean(ages)) if ages else 0.0
        breaches = sla_breaches.get(status_name, 0)
        limit = SLA_LIMITS.get(status_name, 14)

        if status_name in {"Draft", "Submitted", "Under Review", "Changes Requested"}:
            total_active += cnt
            all_ages.extend(ages)

        stages.append({
            "status": status_name,
            "count": cnt,
            "average_days_in_status": round(avg_days, 1),
            "sla_threshold_days": limit,
            "sla_breaches_count": breaches
        })

    overall_avg = float(np.mean(all_ages)) if all_ages else 0.0

    return {
        "total_active_proposals": total_active,
        "stages": stages,
        "overall_avg_turnaround_days": round(overall_avg, 1),
        "longest_stalled_proposal": stalled_candidate
    }
