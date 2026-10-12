import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, CheckCircle2, TrendingDown, Hourglass, ShieldAlert } from 'lucide-react';
import { api } from '../api';
import { formatINR } from '../utils/currency';

export default function BottleneckAnalytics({ onSelectProposal }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchBottlenecks() {
      try {
        const res = await api.getBottlenecks();
        setData(res);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchBottlenecks();
  }, []);

  if (loading) {
    return (
      <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '32px 24px', textAlign: 'center' }}>
        Calculating operational turnaround times and SLA breach status...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '32px 24px' }}>
        <div className="alert-banner alert-danger">{error || "Failed to load bottleneck analytics"}</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      {/* Title */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--primary-navy)', margin: 0 }}>
            Workflow Bottleneck & SLA Analytics
          </h1>
          <span className="badge badge-submitted">INNOVATION MODULE H</span>
        </div>
        <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
          Empirical measurements of proposal aging, supervisory queue latency, and SLA thresholds
        </p>
      </div>

      {/* Top Summary Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div className="card" style={{ borderLeft: '4px solid var(--primary-navy)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>ACTIVE PIPELINE VOLUME</div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--primary-navy)', marginTop: '4px' }}>
            {data.total_active_proposals} proposals
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Draft, Submitted, & In-Review</div>
        </div>

        <div className="card" style={{ borderLeft: '4px solid #0284c7' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#0284c7' }}>AVERAGE ACTIVE AGE</div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#0284c7', marginTop: '4px' }}>
            {data.overall_avg_turnaround_days} days
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Across active queue stages</div>
        </div>

        <div className="card" style={{ borderLeft: '4px solid #d97706' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#d97706' }}>ACTIVE SLA BREACHES</div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#d97706', marginTop: '4px' }}>
            {data.stages.reduce((acc, s) => acc + s.sla_breaches_count, 0)} items
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Exceeding 14-day command review target</div>
        </div>
      </div>

      {/* Longest Stalled Proposal Banner */}
      {data.longest_stalled_proposal && (
        <div className="alert-banner alert-warning" style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Hourglass size={24} color="#b45309" />
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.95rem' }}>
                PRIORITY STALLED DOSSIER: [{data.longest_stalled_proposal.proposal_code}] {data.longest_stalled_proposal.title}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#78350f', marginTop: '2px' }}>
                Currently in <strong>{data.longest_stalled_proposal.status}</strong> for <strong>{data.longest_stalled_proposal.days_in_status} days</strong> &bull; {data.longest_stalled_proposal.department} &bull; {formatINR(data.longest_stalled_proposal.cost)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Lifecycle Stage SLA Breakdown Table */}
      <div className="card">
        <h3 style={{ fontSize: '1.1rem', color: 'var(--primary-navy)', marginBottom: '16px' }}>
          Stage Duration & SLA Performance Breakdown
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8fafc', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>LIFECYCLE STAGE</th>
                <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>COUNT</th>
                <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>AVG DURATION</th>
                <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>SLA TARGET</th>
                <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>SLA BREACHES</th>
                <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>STATUS HEALTH</th>
              </tr>
            </thead>
            <tbody>
              {data.stages.map((st, idx) => {
                const hasBreach = st.sla_breaches_count > 0;
                return (
                  <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '12px 14px', fontWeight: 600 }}>{st.status}</td>
                    <td style={{ padding: '12px 14px' }}>{st.count}</td>
                    <td style={{ padding: '12px 14px', fontWeight: 700 }}>
                      {st.average_days_in_status} days
                    </td>
                    <td style={{ padding: '12px 14px', color: 'var(--text-muted)' }}>
                      {st.sla_threshold_days < 100 ? `${st.sla_threshold_days} days max` : 'N/A (Final)'}
                    </td>
                    <td style={{ padding: '12px 14px' }}>
                      {hasBreach ? (
                        <span style={{ color: '#b91c1c', fontWeight: 700 }}>
                          {st.sla_breaches_count} breaches
                        </span>
                      ) : (
                        <span style={{ color: '#16a34a', fontWeight: 500 }}>None</span>
                      )}
                    </td>
                    <td style={{ padding: '12px 14px' }}>
                      {hasBreach ? (
                        <span className="badge badge-changes">SLA Warning</span>
                      ) : (
                        <span className="badge badge-approved">Optimal</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
