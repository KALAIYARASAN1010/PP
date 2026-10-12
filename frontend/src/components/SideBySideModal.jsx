import React from 'react';
import { X, ArrowRight, DollarSign, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';
import { formatINR } from '../utils/currency';

export default function SideBySideModal({ comparisonData, currentProposal, precedentProposal, onClose }) {
  if (!currentProposal || !precedentProposal) return null;

  const costDelta = currentProposal.cost - precedentProposal.cost;
  const costRatio = precedentProposal.cost > 0 ? (currentProposal.cost / precedentProposal.cost).toFixed(2) : 1;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '1000px' }} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--primary-navy)' }}>
              Institutional Precedent Side-by-Side Comparison
            </h3>
            <p style={{ margin: '2px 0 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Evaluate structural differences, budgetary variance, and precedent outcomes
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* Summary Metric Ribbon */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
            marginBottom: '20px',
            backgroundColor: '#f8fafc',
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid #e2e8f0'
          }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Cost Variance</div>
              <div style={{
                fontSize: '1.1rem',
                fontWeight: 700,
                color: costDelta > 0 ? '#b91c1c' : '#15803d'
              }}>
                {costDelta >= 0 ? `+${formatINR(costDelta)}` : `-${formatINR(Math.abs(costDelta))}`}
                <span style={{ fontSize: '0.75rem', fontWeight: 500, marginLeft: '6px' }}>({costRatio}x precedent)</span>
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Precedent Outcome</div>
              <div style={{ fontSize: '1rem', fontWeight: 700 }}>
                <span className={`badge ${precedentProposal.decision === 'Approved' ? 'badge-approved' : 'badge-rejected'}`}>
                  {precedentProposal.decision || 'No Decision Recorded'}
                </span>
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Category / Dept Match</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--secondary-navy)' }}>
                {currentProposal.category === precedentProposal.category ? 'Identical Category' : 'Different Category'} &bull; {currentProposal.department === precedentProposal.department ? 'Same Dept' : 'Cross-Dept'}
              </div>
            </div>
          </div>

          {/* Two Columns Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px'
          }}>
            {/* Column 1: Current Proposal */}
            <div style={{ border: '1px solid #cbd5e1', borderRadius: '8px', padding: '16px', backgroundColor: '#ffffff' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0369a1', textTransform: 'uppercase' }}>
                  CURRENT PROPOSAL (UNDER EVALUATION)
                </span>
                <span className="badge badge-under-review">{currentProposal.status || 'Draft'}</span>
              </div>
              <h4 style={{ margin: '0 0 6px 0', fontSize: '1.05rem', color: 'var(--primary-navy)' }}>
                {currentProposal.title}
              </h4>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                {currentProposal.proposal_code || 'NEW DRAFT'} &bull; {currentProposal.category} &bull; {currentProposal.department}
              </div>

              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>REQUESTED COST:</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--primary-green)' }}>
                  {formatINR(currentProposal.cost)}
                </div>
              </div>

              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>OPERATIONAL SCOPE:</div>
                <p style={{ fontSize: '0.85rem', color: '#334155', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                  {currentProposal.description}
                </p>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>JUSTIFICATION:</div>
                <p style={{ fontSize: '0.85rem', color: '#334155', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                  {currentProposal.justification}
                </p>
              </div>
            </div>

            {/* Column 2: Historical Precedent */}
            <div style={{ border: '1px solid #cbd5e1', borderRadius: '8px', padding: '16px', backgroundColor: '#f8fafc' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary-green)', textTransform: 'uppercase' }}>
                  HISTORICAL PRECEDENT (ARCHIVED)
                </span>
                <span className={`badge ${precedentProposal.decision === 'Approved' ? 'badge-approved' : 'badge-rejected'}`}>
                  {precedentProposal.decision || 'No Decision'}
                </span>
              </div>
              <h4 style={{ margin: '0 0 6px 0', fontSize: '1.05rem', color: 'var(--primary-navy)' }}>
                {precedentProposal.title}
              </h4>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                {precedentProposal.proposal_code} &bull; {precedentProposal.category} &bull; {precedentProposal.department}
              </div>

              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>HISTORICAL COST:</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--secondary-navy)' }}>
                  {formatINR(precedentProposal.cost)}
                </div>
              </div>

              {/* Prior Decision Reason */}
              {precedentProposal.reason && (
                <div style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  padding: '8px 10px',
                  marginBottom: '12px',
                  fontSize: '0.825rem'
                }}>
                  <strong style={{ color: 'var(--secondary-navy)' }}>Recorded Commander Decision Rationale: </strong>
                  <span style={{ color: '#475569' }}>"{precedentProposal.reason}"</span>
                </div>
              )}

              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>HISTORICAL SCOPE:</div>
                <p style={{ fontSize: '0.85rem', color: '#334155', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                  {precedentProposal.description || precedentProposal.why_matched}
                </p>
              </div>

              {/* Field Deployment Lessons if present */}
              {(precedentProposal.implementation_outcome || precedentProposal.lessons_learned) && (
                <div style={{
                  backgroundColor: '#f0fdf4',
                  border: '1px solid #bbf7d0',
                  borderRadius: '6px',
                  padding: '8px 10px',
                  fontSize: '0.8rem'
                }}>
                  {precedentProposal.implementation_outcome && (
                    <div style={{ marginBottom: '4px' }}>
                      <strong style={{ color: '#166534' }}>Field Outcome: </strong>
                      <span style={{ color: '#14532d' }}>{precedentProposal.implementation_outcome}</span>
                    </div>
                  )}
                  {precedentProposal.lessons_learned && (
                    <div>
                      <strong style={{ color: '#166534' }}>Lesson: </strong>
                      <span style={{ color: '#14532d' }}>{precedentProposal.lessons_learned}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="btn btn-outline" onClick={onClose}>
            Close Comparison
          </button>
        </div>
      </div>
    </div>
  );
}
