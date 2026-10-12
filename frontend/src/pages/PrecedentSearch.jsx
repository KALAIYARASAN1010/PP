import React, { useState, useEffect } from 'react';
import { 
  Search, Sliders, Sparkles, AlertTriangle, Shield, 
  HelpCircle, CheckCircle2, TrendingUp, Layers, Columns3 
} from 'lucide-react';
import { api } from '../api';
import PrecedentCard from '../components/PrecedentCard';
import SideBySideModal from '../components/SideBySideModal';

const SUGGESTED_QUERIES = [
  "Body-worn cameras with in-car video syncing",
  "Unmanned tactical drones with thermal optics",
  "Automated license plate readers cloud retention",
  "Mental health crisis de-escalation training",
  "Baking chocolate raspberry cake pastry recipe (Irrelevant Query Test)"
];

export default function PrecedentSearch({ onSelectProposal }) {
  const [query, setQuery] = useState('Body-worn cameras with in-car video syncing');
  const [category, setCategory] = useState('');
  const [department, setDepartment] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [threshold, setThreshold] = useState(0.35);

  const [resultsData, setResultsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Side by Side comparison
  const [comparisonPrecedent, setComparisonPrecedent] = useState(null);

  const executeSearch = async (targetQuery = query) => {
    if (!targetQuery.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const data = await api.searchPrecedents({
        query: targetQuery,
        category: category || null,
        department: department || null,
        status: statusFilter || null,
        threshold: Number(threshold),
        top_k: 5
      });
      setResultsData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeSearch();
  }, [category, department, statusFilter, threshold]);

  const handleFormSubmit = (e) => {
    e.preventDefault();
    executeSearch();
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      {/* Title */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--primary-navy)', margin: 0 }}>
            Institutional Precedent Retrieval Engine
          </h1>
          <span className="badge badge-approved">HYBRID SEMANTIC + KEYWORD</span>
        </div>
        <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
          Query decades of past departmental proposals, supervisory rationales, and post-implementation outcomes
        </p>
      </div>

      {/* MANDATORY LEGAL & POLICY DISCLAIMER */}
      <div className="alert-banner alert-info" style={{ marginBottom: '20px' }}>
        <Shield size={22} color="#1d4ed8" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong style={{ fontSize: '0.85rem', display: 'block', marginBottom: '2px', color: '#1e40af' }}>
            STATUTORY OVERSIGHT & PRECEDENT INTERPRETATION DISCLAIMER
          </strong>
          <p style={{ margin: 0, fontSize: '0.8rem', color: '#1e3a8a', lineHeight: 1.4 }}>
            Similarity score measures textual, semantic, and institutional overlap against past records.
            <strong> High similarity does NOT indicate approval probability.</strong> Prior approved proposals do not guarantee future approval, and prior rejections do not preclude revised initiatives. Determining authority rests solely with designated human command reviewers.
          </p>
        </div>
      </div>

      {/* Search Input Bar & Suggested Chips */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <form onSubmit={handleFormSubmit} style={{ display: 'flex', gap: '10px', marginBottom: '14px' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <input
              type="text"
              className="form-input"
              style={{ fontSize: '1rem', padding: '12px 16px' }}
              placeholder="Search concepts, equipment, policies, or past determinations..."
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ padding: '0 24px' }} disabled={loading}>
            <Search size={18} />
            <span>Search Precedents</span>
          </button>
        </form>

        {/* Suggested Queries Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', fontSize: '0.75rem' }}>
          <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Quick Test Queries:</span>
          {SUGGESTED_QUERIES.map((sq, idx) => (
            <button
              key={idx}
              type="button"
              className="btn btn-outline"
              style={{ fontSize: '0.72rem', padding: '2px 8px', borderRadius: '4px' }}
              onClick={() => {
                setQuery(sq);
                executeSearch(sq);
              }}
            >
              {sq}
            </button>
          ))}
        </div>

        {/* Filters and Similarity Threshold Slider */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '12px',
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid var(--border-color)'
        }}>
          <div>
            <label className="form-label">Category Filter</label>
            <select className="form-select" value={category} onChange={e => setCategory(e.target.value)}>
              <option value="">All Categories</option>
              <option value="Administrative">Administrative</option>
              <option value="Technical">Technical</option>
              <option value="Procurement">Procurement</option>
              <option value="Infrastructure">Infrastructure</option>
              <option value="Operational">Operational</option>
            </select>
          </div>

          <div>
            <label className="form-label">Division Filter</label>
            <select className="form-select" value={department} onChange={e => setDepartment(e.target.value)}>
              <option value="">All Divisions</option>
              <option value="Patrol Operations">Patrol Operations</option>
              <option value="Forensics & Cyber Crimes">Forensics & Cyber Crimes</option>
              <option value="Tactical Response Unit">Tactical Response Unit</option>
              <option value="Traffic Division">Traffic Division</option>
              <option value="IT & Communications">IT & Communications</option>
            </select>
          </div>

          <div>
            <label className="form-label">Status Filter</label>
            <select className="form-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
              <option value="">All Statuses</option>
              <option value="Approved">Approved Only</option>
              <option value="Rejected">Rejected Only</option>
              <option value="Changes Requested">Changes Requested</option>
            </select>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <label className="form-label" style={{ margin: 0 }}>Similarity Threshold</label>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary-green)' }}>
                {Math.round(threshold * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.80"
              step="0.05"
              value={threshold}
              onChange={e => setThreshold(Number(e.target.value))}
              style={{ width: '100%' }}
            />
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              Below threshold triggers "no strong precedent" notice
            </div>
          </div>
        </div>
      </div>

      {error && <div className="alert-banner alert-danger">{error}</div>}

      {/* Results Header / Warning Banner */}
      {resultsData && (
        <div style={{ marginBottom: '16px' }}>
          {resultsData.warning_message && (
            <div className="alert-banner alert-warning">
              <AlertTriangle size={18} color="#b45309" style={{ flexShrink: 0 }} />
              <div>
                <strong>THRESHOLD NOTICE: </strong>
                <span>{resultsData.warning_message}</span>
              </div>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <div>
              Retrieved <strong>{resultsData.results.length}</strong> top precedents across {resultsData.total_candidates} records
              &bull; Active Engine: <strong style={{ color: 'var(--primary-navy)' }}>{resultsData.active_engine}</strong>
            </div>
            <div>
              Strong Precedents (&ge;{Math.round(threshold*100)}%): <strong>{resultsData.strong_precedent_count}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Results List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Computing hybrid cosine similarity and token overlaps...
        </div>
      ) : resultsData && resultsData.results.length > 0 ? (
        <div>
          {resultsData.results.map(prec => (
            <PrecedentCard
              key={prec.id}
              precedent={prec}
              onCompare={() => setComparisonPrecedent(prec)}
              onSelect={onSelectProposal}
            />
          ))}
        </div>
      ) : resultsData && resultsData.results.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <HelpCircle size={36} color="#94a3b8" style={{ marginBottom: '8px' }} />
          <h4>No Precedents Found</h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            No records matched your search query and metadata filters.
          </p>
        </div>
      ) : null}

      {/* Side by Side Modal */}
      {comparisonPrecedent && (
        <SideBySideModal
          currentProposal={{
            title: query,
            category: category || 'Active Search Query',
            department: department || 'Departmental Query',
            cost: 50000,
            description: `Draft inquiry for: ${query}`,
            justification: 'Synthesizing historical outcomes for comparison.',
            status: 'Query Mode'
          }}
          precedentProposal={comparisonPrecedent}
          onClose={() => setComparisonPrecedent(null)}
        />
      )}
    </div>
  );
}
