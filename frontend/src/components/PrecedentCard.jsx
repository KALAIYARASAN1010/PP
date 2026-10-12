import React from 'react';
import { Columns3, AlertCircle, Award, CheckCircle2, XCircle, Clock, Lightbulb, TrendingUp } from 'lucide-react';
import { formatINR } from '../utils/currency';

export default function PrecedentCard({ precedent, onCompare, onSelect }) {
  const scorePercent = Math.round(precedent.similarity_score * 100);

  // Score badge coloring
  let scoreColor = '#16a34a'; // High green
  let scoreBg = '#dcfce7';
  if (scorePercent < 45) {
    scoreColor = '#d97706'; // Amber moderate
    scoreBg = '#fef3c7';
  } else if (scorePercent < 65) {
    scoreColor = '#0284c7'; // Blue solid
    scoreBg = '#e0f2fe';
  }

  const decision = precedent.decision;
  let decisionBadgeClass = 'badge-draft';
  if (decision === 'Approved') decisionBadgeClass = 'badge-approved';
  else if (decision === 'Rejected') decisionBadgeClass = 'badge-rejected';
  else if (decision === 'Changes Requested') decisionBadgeClass = 'badge-changes';
  else if (decision === 'Under Review') decisionBadgeClass = 'badge-under-review';

  return (
    <div className="card" style={{ marginBottom: '16px', borderLeft: `4px solid ${scoreColor}` }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontWeight: 700, color: 'var(--primary-green)', fontSize: '0.85rem' }}>
              {precedent.proposal_code}
            </span>
            <span className={`badge ${decisionBadgeClass}`}>
              {decision || 'No Decision Recorded'}
            </span>
            <span className="badge-tag">{precedent.category}</span>
            <span className="badge-tag">{precedent.department}</span>
          </div>
          <h4 
            style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary-navy)', cursor: onSelect ? 'pointer' : 'default' }}
            onClick={() => onSelect && onSelect(precedent.id)}
          >
            {precedent.title}
          </h4>
        </div>

        {/* Similarity Score Pill */}
        <div style={{ textAlign: 'right' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            backgroundColor: scoreBg,
            color: scoreColor,
            fontWeight: 800,
            fontSize: '0.9rem',
            padding: '4px 10px',
            borderRadius: '9999px',
            border: `1px solid ${scoreColor}`
          }}>
            <TrendingUp size={14} />
            <span>{scorePercent}% Similarity</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            {precedent.is_strong_precedent ? 'Strong Precedent' : 'Moderate Overlap'}
          </div>
        </div>
      </div>

      {/* Decision Rationale or Note */}
      {precedent.reason && (
        <div style={{
          backgroundColor: '#f8fafc',
          border: '1px solid #e2e8f0',
          borderRadius: '6px',
          padding: '8px 12px',
          marginBottom: '10px',
          fontSize: '0.85rem'
        }}>
          <strong style={{ color: 'var(--secondary-navy)' }}>Prior Decision Rationale: </strong>
          <span style={{ color: '#334155' }}>"{precedent.reason}"</span>
        </div>
      )}

      {/* Why Matched explanation */}
      <div style={{ fontSize: '0.825rem', color: '#475569', marginBottom: '10px', display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
        <Lightbulb size={15} color="#d97706" style={{ flexShrink: 0, marginTop: '2px' }} />
        <span><strong>Why Matched:</strong> {precedent.why_matched}</span>
      </div>

      {/* Highlighted keyword matches */}
      {precedent.highlighted_matches && precedent.highlighted_matches.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginRight: '6px' }}>
            MATCHED KEYWORDS:
          </span>
          {precedent.highlighted_matches.map((token, idx) => (
            <span key={idx} className="highlight-pill">{token}</span>
          ))}
        </div>
      )}

      {/* Implementation Outcome & Lessons Learned (INNOVATION G) */}
      {(precedent.implementation_outcome || precedent.lessons_learned) && (
        <div style={{
          backgroundColor: '#f0fdf4',
          border: '1px solid #bbf7d0',
          borderRadius: '6px',
          padding: '10px 12px',
          marginBottom: '12px',
          fontSize: '0.825rem'
        }}>
          {precedent.implementation_outcome && (
            <div style={{ marginBottom: precedent.lessons_learned ? '6px' : '0' }}>
              <strong style={{ color: '#166534' }}>Field Deployment Outcome: </strong>
              <span style={{ color: '#14532d' }}>{precedent.implementation_outcome}</span>
            </div>
          )}
          {precedent.lessons_learned && (
            <div>
              <strong style={{ color: '#166534' }}>Institutional Lesson: </strong>
              <span style={{ color: '#14532d' }}>{precedent.lessons_learned}</span>
            </div>
          )}
        </div>
      )}

      {/* Footer Info & Actions */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderTop: '1px solid #f1f5f9',
        paddingTop: '10px',
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        flexWrap: 'wrap',
        gap: '8px'
      }}>
        <div>
          Requested Cost: <strong style={{ color: 'var(--primary-navy)' }}>{formatINR(precedent.cost)}</strong> &bull; Date: {new Date(precedent.date).toLocaleDateString()}
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {onCompare && (
            <button
              onClick={() => onCompare(precedent)}
              className="btn btn-outline"
              style={{ fontSize: '0.78rem', padding: '4px 10px' }}
            >
              <Columns3 size={13} />
              <span>Compare Side-by-Side</span>
            </button>
          )}
          {onSelect && (
            <button
              onClick={() => onSelect(precedent.id)}
              className="btn btn-primary"
              style={{ fontSize: '0.78rem', padding: '4px 10px' }}
            >
              View Full Precedent
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
