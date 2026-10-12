import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, CheckCircle2, XCircle, AlertTriangle, Clock, 
  FileText, Printer, GitCommit, Upload, User, DollarSign, 
  Layers, Building, Calendar, ShieldCheck, ShieldAlert 
} from 'lucide-react';
import { api } from '../api';
import { formatINR } from '../utils/currency';
import { useAuth } from '../context/AuthContext';
import ReviewerBriefModal from '../components/ReviewerBriefModal';
import LineageGraphModal from '../components/LineageGraphModal';

export default function ProposalDetail({ proposalId, setActivePage, onSelectProposal }) {
  const { currentUser } = useAuth();
  const [proposal, setProposal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Workflow Decision State
  const [decisionAction, setDecisionAction] = useState('Approved');
  const [decisionReason, setDecisionReason] = useState('');
  const [submittingDecision, setSubmittingDecision] = useState(false);
  const [decisionSuccess, setDecisionSuccess] = useState(null);
  const [decisionError, setDecisionError] = useState(null);

  // Modals
  const [showBriefModal, setShowBriefModal] = useState(false);
  const [showLineageModal, setShowLineageModal] = useState(false);

  // PDF Upload
  const [uploadingPdf, setUploadingPdf] = useState(false);
  const [pdfSuccess, setPdfSuccess] = useState(null);

  const fetchProposal = async () => {
    try {
      const data = await api.getProposal(proposalId);
      setProposal(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (proposalId) fetchProposal();
  }, [proposalId]);

  const handleDecisionSubmit = async () => {
    if (!decisionReason || decisionReason.trim().length < 5) {
      setDecisionError("Mandatory Decision Reason Required: Please provide a substantive justification (minimum 5 characters).");
      return;
    }

    setSubmittingDecision(true);
    setDecisionError(null);
    setDecisionSuccess(null);

    try {
      const res = await api.makeDecision(proposalId, {
        action: decisionAction,
        reason: decisionReason
      });
      setDecisionSuccess(`Successfully recorded decision: ${decisionAction}! Status updated.`);
      setDecisionReason('');
      fetchProposal();
    } catch (err) {
      setDecisionError(err.message);
    } finally {
      setSubmittingDecision(false);
    }
  };

  const handleMarkUnderReview = async () => {
    try {
      await api.markUnderReview(proposalId);
      fetchProposal();
    } catch (err) {
      setDecisionError(err.message);
    }
  };

  const handlePdfUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingPdf(true);
    setPdfSuccess(null);
    try {
      await api.uploadProposalPdf(proposalId, file);
      setPdfSuccess(`PDF '${file.name}' attached and parsed with pypdf!`);
      fetchProposal();
    } catch (err) {
      setDecisionError(`PDF upload rejected: ${err.message}`);
    } finally {
      setUploadingPdf(false);
    }
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '32px 24px', textAlign: 'center' }}>
        Retrieving official proposal dossier...
      </div>
    );
  }

  if (error || !proposal) {
    return (
      <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '32px 24px' }}>
        <div className="alert-banner alert-danger">{error || "Proposal record not found"}</div>
        <button className="btn btn-outline" onClick={() => setActivePage('proposals')}>
          <ArrowLeft size={16} />
          <span>Back to Proposals</span>
        </button>
      </div>
    );
  }

  // RBAC checks
  const isSubmitterOfThisProposal = currentUser?.id === proposal.submitter_id;
  const isReviewerRole = currentUser?.role === 'Reviewer' || currentUser?.role === 'Admin';
  const isReviewerSelfConflict = currentUser?.role === 'Reviewer' && isSubmitterOfThisProposal;
  const canMakeDecision = isReviewerRole && !isReviewerSelfConflict;

  let badgeClass = 'badge-draft';
  if (proposal.status === 'Approved') badgeClass = 'badge-approved';
  else if (proposal.status === 'Rejected') badgeClass = 'badge-rejected';
  else if (proposal.status === 'Changes Requested') badgeClass = 'badge-changes';
  else if (proposal.status === 'Under Review') badgeClass = 'badge-under-review';
  else if (proposal.status === 'Submitted') badgeClass = 'badge-submitted';

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      {/* Top Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button className="btn btn-outline" onClick={() => setActivePage('proposals')}>
            <ArrowLeft size={16} />
            <span>All Proposals</span>
          </button>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 800, color: 'var(--primary-green)', fontSize: '1rem' }}>
                {proposal.proposal_code}
              </span>
              <span className={`badge ${badgeClass}`}>{proposal.status}</span>
            </div>
            <h1 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--primary-navy)', margin: '2px 0 0 0' }}>
              {proposal.title}
            </h1>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button className="btn btn-navy" onClick={() => setShowBriefModal(true)}>
            <Printer size={15} />
            <span>Reviewer Brief (1-Page)</span>
          </button>

          <button className="btn btn-outline" onClick={() => setShowLineageModal(true)}>
            <GitCommit size={15} />
            <span>Resubmission Lineage</span>
          </button>
        </div>
      </div>

      {decisionSuccess && <div className="alert-banner alert-success">{decisionSuccess}</div>}
      {decisionError && <div className="alert-banner alert-danger">{decisionError}</div>}
      {pdfSuccess && <div className="alert-banner alert-success">{pdfSuccess}</div>}

      {/* Grid Layout: Main Dossier Details vs Workflow Decisions */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(450px, 1.4fr) minmax(350px, 1fr)',
        gap: '24px',
        alignItems: 'start'
      }}>
        {/* Left Column: Dossier Content */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Metadata Card */}
          <div className="card">
            <h3 style={{ fontSize: '1.05rem', color: 'var(--primary-navy)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              Institutional Metadata & Fiscal Allocation
            </h3>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '14px',
              marginBottom: '16px'
            }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>CATEGORY</div>
                <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--secondary-navy)' }}>
                  {proposal.category}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>DEPARTMENT</div>
                <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--secondary-navy)' }}>
                  {proposal.department}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>FISCAL EXPENDITURE</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--primary-green)' }}>
                  {formatINR(proposal.cost)}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>SUBMITTING OFFICER</div>
                <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--secondary-navy)' }}>
                  {proposal.submitter_name}
                </div>
              </div>
            </div>

            {/* Scope */}
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--secondary-navy)', textTransform: 'uppercase', marginBottom: '4px' }}>
                1. Operational Scope & Specifications
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#334155', lineHeight: 1.5, margin: 0 }}>
                {proposal.description}
              </p>
            </div>

            {/* Justification */}
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--secondary-navy)', textTransform: 'uppercase', marginBottom: '4px' }}>
                2. Operational Justification
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#334155', lineHeight: 1.5, margin: 0 }}>
                {proposal.justification}
              </p>
            </div>

            {/* Field Implementation Outcome if present (Innovation G) */}
            {(proposal.implementation_outcome || proposal.lessons_learned) && (
              <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', padding: '14px', borderRadius: '8px', marginBottom: '16px' }}>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#166534', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Post-Approval Field Outcome & Institutional Memory
                </h4>
                {proposal.implementation_outcome && (
                  <p style={{ fontSize: '0.85rem', color: '#14532d', margin: '0 0 6px 0' }}>
                    <strong>Deployment Result:</strong> {proposal.implementation_outcome}
                  </p>
                )}
                {proposal.lessons_learned && (
                  <p style={{ fontSize: '0.85rem', color: '#14532d', margin: 0 }}>
                    <strong>Lessons Learned:</strong> {proposal.lessons_learned}
                  </p>
                )}
              </div>
            )}

            {/* Document Reference / PDF Section */}
            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--secondary-navy)', margin: 0 }}>
                    Evidentiary Documentation (.pdf)
                  </h4>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {proposal.document_ref ? `Attached: ${proposal.document_ref}` : 'No PDF attached yet'}
                  </div>
                </div>

                <label className="btn btn-outline" style={{ fontSize: '0.75rem', cursor: 'pointer' }}>
                  <Upload size={13} />
                  <span>{uploadingPdf ? 'Processing with pypdf...' : 'Upload PDF'}</span>
                  <input type="file" accept=".pdf" onChange={handlePdfUpload} style={{ display: 'none' }} />
                </label>
              </div>
            </div>
          </div>

          {/* Append-Only Decision History */}
          <div className="card">
            <h3 style={{ fontSize: '1.05rem', color: 'var(--primary-navy)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              Append-Only Official Decision History
            </h3>

            {proposal.decisions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <Clock size={24} color="#94a3b8" style={{ marginBottom: '6px' }} />
                <div>No formal supervisory decisions have been recorded yet.</div>
                <div style={{ fontSize: '0.75rem', marginTop: '2px' }}>Awaiting command determination.</div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {proposal.decisions.map((dec, idx) => {
                  let decBadge = 'badge-draft';
                  if (dec.action === 'Approved') decBadge = 'badge-approved';
                  else if (dec.action === 'Rejected') decBadge = 'badge-rejected';
                  else if (dec.action === 'Changes Requested') decBadge = 'badge-changes';

                  return (
                    <div key={dec.id} style={{
                      padding: '12px',
                      backgroundColor: '#f8fafc',
                      borderRadius: '8px',
                      border: '1px solid #e2e8f0'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.8rem', color: 'var(--secondary-navy)' }}>
                            Decision #{idx + 1}
                          </span>
                          <span className={`badge ${decBadge}`}>{dec.action}</span>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {new Date(dec.created_at).toLocaleString()}
                        </div>
                      </div>

                      <div style={{ fontSize: '0.825rem', color: '#1e293b', marginTop: '6px', lineHeight: 1.4 }}>
                        <strong>Rationale:</strong> "{dec.reason}"
                      </div>

                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        Evaluating Commander: <strong>{dec.reviewer_name}</strong>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Workflow Adjudication Panel (CORE 4 & 5) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="card" style={{ borderTop: '4px solid var(--primary-navy)' }}>
            <h3 style={{ fontSize: '1.05rem', color: 'var(--primary-navy)', marginBottom: '8px' }}>
              Command Adjudication Panel
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '0 0 16px 0' }}>
              Enforces strict backend RBAC: AI never decides. Human supervisory officers must record mandatory rationale.
            </p>

            {/* Status Transition Shortcut */}
            {proposal.status === 'Submitted' && isReviewerRole && !isReviewerSelfConflict && (
              <div style={{ marginBottom: '16px' }}>
                <button
                  className="btn btn-navy"
                  style={{ width: '100%', fontSize: '0.825rem' }}
                  onClick={handleMarkUnderReview}
                >
                  <Clock size={15} />
                  <span>Mark as "Under Review"</span>
                </button>
              </div>
            )}

            {/* Conflict of Interest Warning for Reviewer Self-Proposals */}
            {isReviewerSelfConflict && (
              <div className="alert-banner alert-danger" style={{ display: 'block', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                  <ShieldAlert size={16} color="#991b1b" />
                  <strong style={{ fontSize: '0.85rem' }}>CONFLICT OF INTEREST ENFORCEMENT</strong>
                </div>
                <p style={{ fontSize: '0.78rem', margin: 0 }}>
                  You authored this proposal (Officer Marcus Chen). Departmental integrity regulations and backend RBAC strictly prohibit reviewing your own proposals.
                  Switch to another reviewer persona (e.g. Captain Miller or Admin Patel) to adjudicate.
                </p>
              </div>
            )}

            {/* Submitter Role Warning */}
            {currentUser?.role === 'Submitter' && (
              <div className="alert-banner alert-info" style={{ display: 'block', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                  <ShieldCheck size={16} color="#1e40af" />
                  <strong style={{ fontSize: '0.85rem' }}>SUBMITTER ACCESS MODE</strong>
                </div>
                <p style={{ fontSize: '0.78rem', margin: 0 }}>
                  You are logged in with the Submitter role. Workflow approvals, rejections, and changes requested require Reviewer or Admin credentials.
                </p>
              </div>
            )}

            {/* Decision Controls Form */}
            <div className="form-group">
              <label className="form-label">Adjudication Action *</label>
              <select
                className="form-select"
                value={decisionAction}
                onChange={e => setDecisionAction(e.target.value)}
                disabled={!canMakeDecision}
              >
                <option value="Approved">Approve Proposal</option>
                <option value="Rejected">Reject Proposal</option>
                <option value="Changes Requested">Request Changes / Revision</option>
                <option value="Under Review">Set Status: Under Review</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Mandatory Written Rationale *</label>
              <textarea
                className="form-textarea"
                placeholder="State the institutional, operational, and budgetary grounds for this determination (mandatory)..."
                value={decisionReason}
                onChange={e => setDecisionReason(e.target.value)}
                disabled={!canMakeDecision}
                style={{ minHeight: '110px' }}
              />
            </div>

            <button
              className={`btn ${decisionAction === 'Approved' ? 'btn-success' : (decisionAction === 'Rejected' ? 'btn-danger' : 'btn-warning')}`}
              disabled={!canMakeDecision || submittingDecision}
              onClick={handleDecisionSubmit}
              style={{ width: '100%', padding: '10px' }}
            >
              {submittingDecision ? 'Recording SHA-256 Decision...' : `Submit Official Decision: ${decisionAction}`}
            </button>
          </div>
        </div>
      </div>

      {/* Reviewer Brief Modal (Innovation B) */}
      {showBriefModal && (
        <ReviewerBriefModal
          proposalId={proposal.id}
          onClose={() => setShowBriefModal(false)}
        />
      )}

      {/* Lineage Graph Modal (Innovation F) */}
      {showLineageModal && (
        <LineageGraphModal
          proposalId={proposal.id}
          onClose={() => setShowLineageModal(false)}
          onSelectProposal={(id) => {
            setShowLineageModal(false);
            onSelectProposal(id);
          }}
        />
      )}
    </div>
  );
}
