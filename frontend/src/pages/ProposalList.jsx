import React, { useState, useEffect } from 'react';
import { Search, Filter, PlusCircle, FileText, ArrowRight, Layers, Tag } from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { formatINR } from '../utils/currency';

export default function ProposalList({ setActivePage, onSelectProposal }) {
  const { currentUser } = useAuth();
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [deptFilter, setDeptFilter] = useState('');

  const loadProposals = async () => {
    setLoading(true);
    try {
      const data = await api.getProposals({
        search: searchTerm,
        category: categoryFilter,
        status: statusFilter,
        department: deptFilter
      });
      setProposals(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProposals();
  }, [categoryFilter, statusFilter, deptFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadProposals();
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      {/* Title & Action Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        marginBottom: '20px'
      }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary-navy)', margin: 0 }}>
            Department Proposals Repository
          </h1>
          <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
            Comprehensive institutional archive of departmental initiatives, authorizations, and drafts
          </p>
        </div>

        {currentUser?.role !== 'Reviewer' && (
          <button className="btn btn-primary" onClick={() => setActivePage('create')}>
            <PlusCircle size={16} />
            <span>Draft New Proposal</span>
          </button>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="card" style={{ marginBottom: '24px', padding: '16px' }}>
        <form onSubmit={handleSearchSubmit} style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '12px',
          alignItems: 'flex-end'
        }}>
          {/* Search Term */}
          <div>
            <label className="form-label">Search Query / Code</label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Title, keywords, PROP-..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          {/* Category Filter */}
          <div>
            <label className="form-label">Category</label>
            <select 
              className="form-select"
              value={categoryFilter}
              onChange={e => setCategoryFilter(e.target.value)}
            >
              <option value="">All Categories</option>
              <option value="Administrative">Administrative</option>
              <option value="Technical">Technical</option>
              <option value="Procurement">Procurement</option>
              <option value="Infrastructure">Infrastructure</option>
              <option value="Operational">Operational</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="form-label">Lifecycle Status</label>
            <select 
              className="form-select"
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="Draft">Draft</option>
              <option value="Submitted">Submitted</option>
              <option value="Under Review">Under Review</option>
              <option value="Changes Requested">Changes Requested</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
              <option value="Closed">Closed</option>
            </select>
          </div>

          {/* Department Filter */}
          <div>
            <label className="form-label">Department</label>
            <select 
              className="form-select"
              value={deptFilter}
              onChange={e => setDeptFilter(e.target.value)}
            >
              <option value="">All Divisions</option>
              <option value="Patrol Operations">Patrol Operations</option>
              <option value="Forensics & Cyber Crimes">Forensics & Cyber Crimes</option>
              <option value="Tactical Response Unit">Tactical Response Unit</option>
              <option value="Traffic Division">Traffic Division</option>
              <option value="IT & Communications">IT & Communications</option>
              <option value="Internal Affairs & Oversight">Internal Affairs & Oversight</option>
            </select>
          </div>

          {/* Search Button */}
          <div>
            <button type="submit" className="btn btn-navy" style={{ width: '100%' }}>
              <Search size={15} />
              <span>Filter Repository</span>
            </button>
          </div>
        </form>
      </div>

      {/* Proposals List Table / Cards */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Retrieving departmental proposals...
        </div>
      ) : proposals.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px 24px' }}>
          <FileText size={40} color="#94a3b8" style={{ marginBottom: '12px' }} />
          <h3 style={{ color: 'var(--primary-navy)' }}>No Proposals Found</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            No proposals match the current filter criteria.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
            Showing <strong>{proposals.length}</strong> proposals from repository
          </div>

          {proposals.map(p => {
            let badgeClass = 'badge-draft';
            if (p.status === 'Approved') badgeClass = 'badge-approved';
            else if (p.status === 'Rejected') badgeClass = 'badge-rejected';
            else if (p.status === 'Changes Requested') badgeClass = 'badge-changes';
            else if (p.status === 'Under Review') badgeClass = 'badge-under-review';
            else if (p.status === 'Submitted') badgeClass = 'badge-submitted';
            else if (p.status === 'Closed') badgeClass = 'badge-closed';

            return (
              <div
                key={p.id}
                className="card"
                onClick={() => onSelectProposal(p.id)}
                style={{
                  cursor: 'pointer',
                  padding: '16px 20px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '16px',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ flex: 1, minWidth: '280px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 700, color: 'var(--primary-green)', fontSize: '0.85rem' }}>
                      {p.proposal_code}
                    </span>
                    <span className={`badge ${badgeClass}`}>{p.status}</span>
                    <span className="badge-tag">{p.category}</span>
                    <span className="badge-tag">{p.department}</span>
                    {p.document_ref && (
                      <span style={{ fontSize: '0.7rem', color: '#0369a1', fontWeight: 600 }}>
                        &bull; [PDF Attached]
                      </span>
                    )}
                  </div>

                  <h3 style={{ margin: '0 0 6px 0', fontSize: '1.05rem', color: 'var(--primary-navy)' }}>
                    {p.title}
                  </h3>

                  <p style={{
                    margin: 0,
                    fontSize: '0.825rem',
                    color: 'var(--text-muted)',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>
                    {p.description}
                  </p>
                </div>

                <div style={{ textAlign: 'right', minWidth: '140px' }}>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--primary-navy)' }}>
                    {formatINR(p.cost)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    By: {p.submitter_name}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                    {new Date(p.date).toLocaleDateString()}
                  </div>
                  <button
                    className="btn btn-outline"
                    style={{ fontSize: '0.75rem', padding: '3px 10px', marginTop: '8px' }}
                  >
                    <span>View Dossier</span>
                    <ArrowRight size={12} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
