import React, { useState, useEffect } from 'react';
import { X, Printer, FileText, CheckCircle, AlertTriangle } from 'lucide-react';
import { api } from '../api';

export default function ReviewerBriefModal({ proposalId, onClose }) {
  const [brief, setBrief] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchBrief() {
      try {
        const data = await api.getProposalBrief(proposalId);
        setBrief(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    if (proposalId) fetchBrief();
  }, [proposalId]);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '900px' }} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header no-print">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileText size={20} color="var(--primary-green)" />
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--primary-navy)' }}>
                Official Reviewer Executive Briefing
              </h3>
              <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                One-Page Source-Cited Dossier Built Exclusively from Stored Records
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-primary" onClick={handlePrint} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
              <Printer size={15} />
              <span>Print Brief (1-Page)</span>
            </button>
            <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Modal Body / Printable Dossier */}
        <div className="modal-body printable-area">
          {loading && <div style={{ textAlign: 'center', padding: '40px' }}>Synthesizing stored institutional citations...</div>}
          {error && <div className="alert-banner alert-danger">{error}</div>}

          {brief && brief.printable_formatted_html && (
            <div 
              dangerouslySetInnerHTML={{ __html: brief.printable_formatted_html }}
            />
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer no-print">
          <button className="btn btn-outline" onClick={onClose}>
            Close Dossier
          </button>
          <button className="btn btn-primary" onClick={handlePrint}>
            <Printer size={15} />
            <span>Print Dossier</span>
          </button>
        </div>
      </div>
    </div>
  );
}
