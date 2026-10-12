import React, { useState, useEffect } from 'react';
import { X, GitCommit, ArrowRight, CornerDownRight, Calendar, DollarSign } from 'lucide-react';
import { api } from '../api';
import { formatINR } from '../utils/currency';

export default function LineageGraphModal({ proposalId, onClose, onSelectProposal }) {
  const [lineage, setLineage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchLineage() {
      try {
        const data = await api.getProposalLineage(proposalId);
        setLineage(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    if (proposalId) fetchLineage();
  }, [proposalId]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '800px' }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--primary-navy)' }}>
              Proposal Lineage & Resubmission History
            </h3>
            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Institutional lineage graph from initial iteration to final resolution
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {loading && <div style={{ textAlign: 'center', padding: '30px' }}>Loading proposal lineage chain...</div>}

          {lineage && lineage.nodes && lineage.nodes.length <= 1 && (
            <div style={{ textAlign: 'center', padding: '30px 10px', color: 'var(--text-muted)' }}>
              <GitCommit size={36} color="#94a3b8" style={{ marginBottom: '8px' }} />
              <h4>Single Standalone Proposal</h4>
              <p style={{ fontSize: '0.85rem' }}>This proposal has no recorded parent revisions or resubmitted iterations.</p>
            </div>
          )}

          {lineage && lineage.nodes && lineage.nodes.length > 1 && (
            <div>
              <div style={{ marginBottom: '16px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Lineage Chain Length: <strong>{lineage.chain_length} iterations</strong>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {lineage.nodes.map((node, idx) => {
                  const isCurrent = node.is_current;
                  let badgeClass = 'badge-draft';
                  if (node.status === 'Approved') badgeClass = 'badge-approved';
                  else if (node.status === 'Rejected') badgeClass = 'badge-rejected';
                  else if (node.status === 'Changes Requested') badgeClass = 'badge-changes';
                  else if (node.status === 'Under Review') badgeClass = 'badge-under-review';

                  return (
                    <div 
                      key={node.id}
                      style={{
                        position: 'relative',
                        padding: '16px',
                        borderRadius: '8px',
                        border: isCurrent ? '2px solid var(--primary-green)' : '1px solid #cbd5e1',
                        backgroundColor: isCurrent ? '#f0fdf4' : '#ffffff',
                        boxShadow: isCurrent ? 'var(--shadow-md)' : 'none'
                      }}
                    >
                      {/* Connection arrow between nodes */}
                      {idx > 0 && (
                        <div style={{
                          position: 'absolute',
                          top: '-16px',
                          left: '28px',
                          color: '#64748b',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '0.7rem',
                          fontWeight: 600
                        }}>
                          <CornerDownRight size={14} />
                          <span>Resubmission / Supersedes Revision #{idx}</span>
                        </div>
                      )}

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <span style={{ fontWeight: 700, color: 'var(--primary-green)', fontSize: '0.85rem' }}>
                              Iteration #{idx + 1}: {node.proposal_code}
                            </span>
                            <span className={`badge ${badgeClass}`}>{node.status}</span>
                            {isCurrent && (
                              <span style={{ backgroundColor: 'var(--primary-green)', color: '#ffffff', fontSize: '0.65rem', padding: '1px 6px', borderRadius: '4px', fontWeight: 700 }}>
                                CURRENT PROPOSAL
                              </span>
                            )}
                          </div>
                          <h4 style={{ margin: 0, fontSize: '1rem', color: 'var(--primary-navy)' }}>
                            {node.title}
                          </h4>
                        </div>

                        <div style={{ textAlign: 'right', fontSize: '0.85rem' }}>
                          <div style={{ fontWeight: 700, color: 'var(--primary-navy)' }}>
                            {formatINR(node.cost)}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            {new Date(node.date).toLocaleDateString()}
                          </div>
                        </div>
                      </div>

                      {!isCurrent && onSelectProposal && (
                        <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'flex-end' }}>
                          <button 
                            className="btn btn-outline" 
                            style={{ fontSize: '0.75rem', padding: '3px 8px' }}
                            onClick={() => {
                              onClose();
                              onSelectProposal(node.id);
                            }}
                          >
                            Inspect Iteration #{idx + 1}
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-outline" onClick={onClose}>
            Close Lineage
          </button>
        </div>
      </div>
    </div>
  );
}
