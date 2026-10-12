import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, XCircle, Clock, AlertTriangle, FileText, 
  DollarSign, TrendingUp, PlusCircle, Search, ShieldCheck, 
  ArrowRight, Shield, Layers, Building
} from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { formatINR } from '../utils/currency';

export default function Dashboard({ setActivePage, onSelectProposal }) {
  const { currentUser } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await api.getDashboardStats();
        setStats(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '32px 24px', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>Computing operational metrics directly from institutional database...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '32px 24px' }}>
        <div className="alert-banner alert-danger">{error}</div>
      </div>
    );
  }

  const s = stats.summary;

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      {/* Top Welcome & Quick Actions */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        marginBottom: '24px',
        borderBottom: '1px solid var(--border-color)',
        paddingBottom: '16px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--primary-navy)', margin: 0 }}>
              Pondicherry Police Command Dashboard
            </h1>
            <span className="badge badge-submitted">POLICE OVERSIGHT</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
            Active Personnel: <strong>{currentUser?.full_name}</strong> ({currentUser?.role}) &bull; {currentUser?.department} &bull; Badge {currentUser?.badge_number}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          {currentUser?.role !== 'Reviewer' && (
            <button className="btn btn-primary" onClick={() => setActivePage('create')}>
              <PlusCircle size={16} />
              <span>Draft New Proposal</span>
            </button>
          )}
          <button className="btn btn-navy" onClick={() => setActivePage('precedents')}>
            <Search size={16} />
            <span>Search Precedents</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '28px'
      }}>
        {/* Total Proposals */}
        <div className="card" style={{ borderLeft: '4px solid var(--primary-navy)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>TOTAL PROPOSALS</span>
            <FileText size={18} color="var(--primary-navy)" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--primary-navy)', marginTop: '6px' }}>
            {s.total_proposals}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {formatINR(s.total_funding_requested)} total requested
          </div>
        </div>

        {/* Approved */}
        <div className="card" style={{ borderLeft: '4px solid #16a34a' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#16a34a' }}>APPROVED</span>
            <CheckCircle2 size={18} color="#16a34a" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#16a34a', marginTop: '6px' }}>
            {s.approved}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {formatINR(s.approved_funding)} allocated ({s.approval_rate_percent}% approval rate)
          </div>
        </div>

        {/* Rejected */}
        <div className="card" style={{ borderLeft: '4px solid #dc2626' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#dc2626' }}>REJECTED</span>
            <XCircle size={18} color="#dc2626" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#dc2626', marginTop: '6px' }}>
            {s.rejected}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Precedent rejection reasons mined
          </div>
        </div>

        {/* Pending Review */}
        <div className="card" style={{ borderLeft: '4px solid #0284c7' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0284c7' }}>PENDING REVIEW</span>
            <Clock size={18} color="#0284c7" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#0284c7', marginTop: '6px' }}>
            {s.pending}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {formatINR(s.pending_funding)} awaiting decision
          </div>
        </div>

        {/* Changes Requested */}
        <div className="card" style={{ borderLeft: '4px solid #d97706' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#d97706' }}>CHANGES REQ.</span>
            <AlertTriangle size={18} color="#d97706" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#d97706', marginTop: '6px' }}>
            {s.changes_requested}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Revision resubmissions pending
          </div>
        </div>
      </div>

      {/* Two Column Layout: Category Analytics & Recent Proposals */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: '24px'
      }}>
        {/* Left Column: Category and Department Distributions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Category Breakdown Card */}
          <div className="card">
            <h3 style={{ fontSize: '1.05rem', color: 'var(--primary-navy)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={18} color="var(--primary-green)" />
              <span>Proposals by Institutional Category</span>
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {stats.by_category.map(cat => {
                const pct = s.total_proposals > 0 ? Math.round((cat.count / s.total_proposals) * 100) : 0;
                return (
                  <div key={cat.category}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem', marginBottom: '3px' }}>
                      <span style={{ fontWeight: 600, color: 'var(--secondary-navy)' }}>{cat.category}</span>
                      <span style={{ color: 'var(--text-muted)' }}>
                        {cat.count} proposals &bull; {formatINR(cat.total_cost)} ({pct}%)
                      </span>
                    </div>
                    <div style={{ height: '7px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{
                        height: '100%',
                        width: `${pct}%`,
                        backgroundColor: 'var(--primary-green)',
                        borderRadius: '4px'
                      }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Department Breakdown Card */}
          <div className="card">
            <h3 style={{ fontSize: '1.05rem', color: 'var(--primary-navy)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Building size={18} color="var(--primary-navy)" />
              <span>Expenditure by Department</span>
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {stats.by_department.slice(0, 5).map(d => (
                <div key={d.department} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: '1px dashed #e2e8f0', fontSize: '0.825rem' }}>
                  <span style={{ color: 'var(--secondary-navy)', fontWeight: 500 }}>{d.department}</span>
                  <span style={{ fontWeight: 700, color: 'var(--primary-navy)' }}>{formatINR(d.total_cost)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Recent Proposals Table */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.05rem', color: 'var(--primary-navy)', margin: 0 }}>
              Recent Department Proposals
            </h3>
            <button className="btn btn-outline" style={{ fontSize: '0.75rem', padding: '4px 10px' }} onClick={() => setActivePage('proposals')}>
              View All Proposals
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {stats.recent_proposals.map(p => {
              let badgeClass = 'badge-draft';
              if (p.status === 'Approved') badgeClass = 'badge-approved';
              else if (p.status === 'Rejected') badgeClass = 'badge-rejected';
              else if (p.status === 'Changes Requested') badgeClass = 'badge-changes';
              else if (p.status === 'Under Review') badgeClass = 'badge-under-review';
              else if (p.status === 'Submitted') badgeClass = 'badge-submitted';

              return (
                <div 
                  key={p.id}
                  onClick={() => onSelectProposal(p.id)}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                    backgroundColor: '#ffffff',
                    cursor: 'pointer',
                    transition: 'border-color 0.15s ease, background-color 0.15s ease'
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--primary-green)'; e.currentTarget.style.backgroundColor = '#f8fafc'; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-color)'; e.currentTarget.style.backgroundColor = '#ffffff'; }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontWeight: 700, color: 'var(--primary-green)', fontSize: '0.8rem' }}>{p.proposal_code}</span>
                      <span className="badge-tag">{p.category}</span>
                    </div>
                    <span className={`badge ${badgeClass}`}>{p.status}</span>
                  </div>

                  <h4 style={{ margin: '0 0 4px 0', fontSize: '0.925rem', color: 'var(--primary-navy)', fontWeight: 600 }}>
                    {p.title}
                  </h4>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <span>{p.department} &bull; Submitter: {p.submitter_name}</span>
                    <strong style={{ color: 'var(--primary-navy)' }}>{formatINR(p.cost)}</strong>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
