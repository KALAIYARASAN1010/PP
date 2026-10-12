import React, { useState, useEffect } from 'react';
import { 
  PlusCircle, AlertTriangle, CheckCircle2, ShieldAlert, 
  TrendingUp, FileUp, Columns3, Info, Sparkles, ArrowLeft 
} from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import PrecedentCard from '../components/PrecedentCard';
import SideBySideModal from '../components/SideBySideModal';
import { formatINR } from '../utils/currency';

export default function ProposalCreate({ setActivePage, onSelectProposal }) {
  const { currentUser } = useAuth();

  // Form Fields
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Procurement');
  const [department, setDepartment] = useState(currentUser?.department || 'Patrol Operations');
  const [cost, setCost] = useState(45000);
  const [justification, setJustification] = useState('');
  const [description, setDescription] = useState('');
  const [pdfFile, setPdfFile] = useState(null);

  // Live Innovation State (computed dynamically as officer types!)
  const [dupCheck, setDupCheck] = useState(null);
  const [costBench, setCostBench] = useState(null);
  const [riskChecklist, setRiskChecklist] = useState(null);
  const [conflicts, setConflicts] = useState(null);
  const [livePrecedents, setLivePrecedents] = useState([]);
  
  // Side by Side comparison modal
  const [comparePrecedent, setComparePrecedent] = useState(null);

  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // Debounced live intelligence check
  useEffect(() => {
    const handler = setTimeout(async () => {
      if (title.trim().length >= 4) {
        try {
          // 1. Live Duplicate Check (Innovation A)
          const dupRes = await api.checkDuplicates({
            title,
            description,
            category
          });
          setDupCheck(dupRes);

          // 2. Cost Benchmark vs Similar Precedents (Innovation D)
          if (cost > 0) {
            const benchRes = await api.getCostBenchmark({
              cost: Number(cost),
              category
            });
            setCostBench(benchRes);
          }

          // 3. Rejection-Risk Checklist Mined from Past Rejections (Innovation C)
          const riskRes = await api.getRiskChecklist({
            category,
            description
          });
          setRiskChecklist(riskRes);

          // 4. Precedent Conflict Detector (Innovation E)
          const confRes = await api.getConflicts({
            category,
            description
          });
          setConflicts(confRes);

          // 5. Live Precedent Search (Core 3: Runs live while drafting)
          const searchRes = await api.searchPrecedents({
            query: `${title} ${description}`,
            category,
            top_k: 3,
            threshold: 0.35
          });
          setLivePrecedents(searchRes.results || []);

        } catch (err) {
          console.error("Live precedent lookup error:", err);
        }
      }
    }, 450);

    return () => clearTimeout(handler);
  }, [title, description, category, cost]);

  const handleSubmit = async (targetStatus = 'Draft') => {
    if (!title || !description || !justification) {
      setErrorMessage("Please complete the Title, Operational Scope, and Justification fields.");
      return;
    }

    setSubmitting(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      // 1. Create Proposal
      const created = await api.createProposal({
        title,
        category,
        department,
        cost: Number(cost),
        description,
        justification,
        status: targetStatus
      });

      // 2. Upload PDF if attached
      if (pdfFile) {
        try {
          await api.uploadProposalPdf(created.id, pdfFile);
        } catch (pdfErr) {
          setErrorMessage(`Proposal created (${created.proposal_code}), but PDF attachment failed: ${pdfErr.message}`);
          setSubmitting(false);
          return;
        }
      }

      setStatusMessage(`Successfully generated proposal ${created.proposal_code} (${targetStatus})!`);
      setTimeout(() => {
        onSelectProposal(created.id);
      }, 1000);

    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <button className="btn btn-outline" onClick={() => setActivePage('proposals')}>
          <ArrowLeft size={16} />
          <span>Back</span>
        </button>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary-navy)', margin: 0 }}>
            Author New Departmental Proposal
          </h1>
          <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
            AI-Assisted Institutional Precedent Synthesis & Pre-Submission Validation
          </p>
        </div>
      </div>

      {statusMessage && <div className="alert-banner alert-success">{statusMessage}</div>}
      {errorMessage && <div className="alert-banner alert-danger">{errorMessage}</div>}

      {/* Two Column Drafting Studio */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(400px, 1.2fr) minmax(350px, 1fr)',
        gap: '24px',
        alignItems: 'start'
      }}>
        {/* Left Column: Input Form */}
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', color: 'var(--primary-navy)', marginBottom: '16px' }}>
            Proposal Specifications
          </h3>

          <div className="form-group">
            <label className="form-label">Proposal Title *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Next-Generation Body-Worn Camera Fleet Replacement"
              value={title}
              onChange={e => setTitle(e.target.value)}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">Category *</label>
              <select className="form-select" value={category} onChange={e => setCategory(e.target.value)}>
                <option value="Administrative">Administrative</option>
                <option value="Technical">Technical</option>
                <option value="Procurement">Procurement</option>
                <option value="Infrastructure">Infrastructure</option>
                <option value="Operational">Operational</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Department / Unit *</label>
              <select className="form-select" value={department} onChange={e => setDepartment(e.target.value)}>
                <option value="Patrol Operations">Patrol Operations</option>
                <option value="Forensics & Cyber Crimes">Forensics & Cyber Crimes</option>
                <option value="Tactical Response Unit">Tactical Response Unit</option>
                <option value="Traffic Division">Traffic Division</option>
                <option value="IT & Communications">IT & Communications</option>
                <option value="Training Division">Training Division</option>
                <option value="Executive Review Bureau">Executive Review Bureau</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Estimated fiscal expenditure (INR ₹) *</label>
            <input
              type="number"
              className="form-input"
              value={cost}
              onChange={e => setCost(Math.max(0, Number(e.target.value)))}
              min="0"
              step="500"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Operational Scope & Technical Description *</label>
            <textarea
              className="form-textarea"
              style={{ minHeight: '120px' }}
              placeholder="Detail hardware specifications, vendor details, deployment timeline, and technical requirements..."
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Institutional Need & Operational Justification *</label>
            <textarea
              className="form-textarea"
              style={{ minHeight: '100px' }}
              placeholder="Why is this required? How does it resolve deficiencies or support public safety milestones?..."
              value={justification}
              onChange={e => setJustification(e.target.value)}
            />
          </div>

          {/* PDF Upload */}
          <div className="form-group" style={{ backgroundColor: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px dashed #cbd5e1' }}>
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FileUp size={16} color="var(--primary-green)" />
              <span>Attach Supporting Document (.pdf)</span>
            </label>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0 0 8px 0' }}>
              Uploaded PDF text will be extracted with pypdf and indexed into the semantic vector store. Corrupt files are automatically validated and rejected.
            </p>
            <input
              type="file"
              accept=".pdf"
              onChange={e => setPdfFile(e.target.files[0] || null)}
              style={{ fontSize: '0.85rem' }}
            />
            {pdfFile && (
              <div style={{ marginTop: '6px', fontSize: '0.78rem', color: '#166534', fontWeight: 600 }}>
                Selected: {pdfFile.name} ({Math.round(pdfFile.size / 1024)} KB)
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
            <button
              className="btn btn-outline"
              disabled={submitting}
              onClick={() => handleSubmit('Draft')}
              style={{ flex: 1 }}
            >
              Save as Draft
            </button>
            <button
              className="btn btn-primary"
              disabled={submitting}
              onClick={() => handleSubmit('Submitted')}
              style={{ flex: 1.5 }}
            >
              {submitting ? 'Submitting...' : 'Submit for Command Review'}
            </button>
          </div>
        </div>

        {/* Right Column: Live Institutional Intelligence Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* A. Live Pre-Submission Duplicate Warning (Innovation A) */}
          {dupCheck && dupCheck.has_potential_duplicate && (
            <div className="alert-banner alert-warning" style={{ display: 'block' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <ShieldAlert size={20} color="#b45309" />
                <strong style={{ fontSize: '0.95rem' }}>PRE-SUBMISSION DUPLICATE WARNING</strong>
              </div>
              <p style={{ margin: '0 0 8px 0', fontSize: '0.825rem' }}>
                {dupCheck.recommendation}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {dupCheck.duplicates.map(d => (
                  <div key={d.proposal_code} style={{ backgroundColor: 'rgba(255,255,255,0.7)', padding: '6px 10px', borderRadius: '4px', fontSize: '0.78rem' }}>
                    <strong>[{d.proposal_code}] {d.title}</strong> &bull; {Math.round(d.similarity_score * 100)}% match
                    <div style={{ color: '#78350f', marginTop: '2px' }}>{d.outcome_summary}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* D. Live Cost Benchmark vs Precedents (Innovation D) */}
          {costBench && (
            <div className="card" style={{ padding: '16px', borderLeft: `4px solid ${costBench.is_outlier ? '#dc2626' : '#16a34a'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)' }}>
                  COST BENCHMARK & OUTLIER DETECTION
                </span>
                <span style={{
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  padding: '2px 6px',
                  borderRadius: '4px',
                  backgroundColor: costBench.is_outlier ? '#fee2e2' : '#dcfce7',
                  color: costBench.is_outlier ? '#991b1b' : '#166534'
                }}>
                  {costBench.is_outlier ? 'OUTLIER FLAGGED' : 'STANDARD RANGE'}
                </span>
              </div>
              <p style={{ fontSize: '0.825rem', color: '#334155', margin: '0 0 8px 0' }}>
                {costBench.cost_assessment}
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '8px', borderRadius: '6px' }}>
                <div>
                  <div style={{ color: 'var(--text-muted)' }}>Category Median</div>
                  <div style={{ fontWeight: 700 }}>{formatINR(costBench.benchmark_median)}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-muted)' }}>Mean Avg</div>
                  <div style={{ fontWeight: 700 }}>{formatINR(costBench.benchmark_average)}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-muted)' }}>Z-Score</div>
                  <div style={{ fontWeight: 700 }}>{costBench.z_score}</div>
                </div>
              </div>
            </div>
          )}

          {/* C. Rejection-Risk Checklist Mined from Past Rejections (Innovation C) */}
          {riskChecklist && riskChecklist.identified_risks.length > 0 && (
            <div className="card" style={{ padding: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <AlertTriangle size={17} color="#d97706" />
                <h4 style={{ margin: 0, fontSize: '0.9rem', color: 'var(--primary-navy)' }}>
                  Rejection-Risk Checklist (Mined from Prior Decisions)
                </h4>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0 0 10px 0' }}>
                Key historical rejection grounds in <strong>{category}</strong> to address in your justification:
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {riskChecklist.identified_risks.map((r, idx) => (
                  <div key={idx} style={{ backgroundColor: '#fffbeb', border: '1px solid #fef3c7', padding: '8px', borderRadius: '6px', fontSize: '0.78rem' }}>
                    <div style={{ fontWeight: 700, color: '#92400e' }}>{r.risk_title}</div>
                    <div style={{ color: '#78350f', margin: '2px 0' }}>"{r.past_rejection_reason}"</div>
                    <div style={{ color: '#166534', fontWeight: 600 }}>&rarr; Recommended Mitigation: {r.mitigation_suggestion}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* E. Precedent Conflict Detector (Innovation E) */}
          {conflicts && conflicts.has_conflicts && (
            <div className="card" style={{ padding: '16px', backgroundColor: '#fef2f2', borderColor: '#fca5a5' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <ShieldAlert size={17} color="#dc2626" />
                <h4 style={{ margin: 0, fontSize: '0.9rem', color: '#991b1b' }}>
                  Precedent Divergence Alert
                </h4>
              </div>
              <p style={{ fontSize: '0.75rem', color: '#7f1d1d', margin: 0 }}>
                {conflicts.conflicts[0].conflict_analysis}
              </p>
            </div>
          )}

          {/* Live Top Precedent Matches (Core 3) */}
          <div className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={16} color="var(--primary-green)" />
                <h4 style={{ margin: 0, fontSize: '0.9rem', color: 'var(--primary-navy)' }}>
                  Live Precedent Retrieval
                </h4>
              </div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Top Matches</span>
            </div>

            {livePrecedents.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '20px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Type proposal title and description to activate live hybrid semantic precedent retrieval.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {livePrecedents.map(prec => (
                  <PrecedentCard
                    key={prec.id}
                    precedent={prec}
                    onCompare={() => setComparePrecedent(prec)}
                    onSelect={() => onSelectProposal(prec.id)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Side by Side Modal */}
      {comparePrecedent && (
        <SideBySideModal
          currentProposal={{
            title: title || 'Draft Proposal',
            category,
            department,
            cost: Number(cost),
            description: description || 'Scope under development',
            justification: justification || 'Justification under development',
            status: 'Draft'
          }}
          precedentProposal={comparePrecedent}
          onClose={() => setComparePrecedent(null)}
        />
      )}
    </div>
  );
}
