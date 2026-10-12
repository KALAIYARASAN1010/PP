import React, { useState, useEffect } from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle2, AlertOctagon, Lock, RefreshCw, KeyRound, Bug } from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';

export default function AuditTrail() {
  const { currentUser } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Verification State
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);

  // Tamper Simulation State
  const [simulating, setSimulating] = useState(false);
  const [tamperMessage, setTamperMessage] = useState(null);

  const loadAuditLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAuditLogs();
      setLogs(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const handleVerifyIntegrity = async () => {
    setVerifying(true);
    setVerificationResult(null);
    try {
      const res = await api.verifyAuditIntegrity();
      setVerificationResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setVerifying(false);
    }
  };

  const handleSimulateTamper = async () => {
    if (logs.length === 0) return;
    setSimulating(true);
    setTamperMessage(null);
    try {
      // Tamper with record 2 or first record
      const targetId = logs.length > 2 ? logs[logs.length - 2].id : logs[0].id;
      const res = await api.simulateAuditTamper(targetId);
      setTamperMessage(`Simulated unauthorized edit on Record #${targetId}. Click "Verify Chain Integrity" to test cryptographic detection.`);
      loadAuditLogs();
    } catch (err) {
      setError(err.message);
    } finally {
      setSimulating(false);
    }
  };

  const isAdmin = currentUser?.role === 'Admin';

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      {/* Title & Actions */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        marginBottom: '20px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--primary-navy)', margin: 0 }}>
              Immutable Cryptographic Audit Trail
            </h1>
            <span className="badge badge-submitted">SHA-256 HASH CHAIN</span>
          </div>
          <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
            Strict append-only forensic ledger recording every proposal creation, PDF attachment, and command adjudication
          </p>
        </div>

        {/* Admin Controls */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary"
            onClick={handleVerifyIntegrity}
            disabled={verifying || !isAdmin}
            title={!isAdmin ? "Integrity verification requires Administrator privileges" : ""}
          >
            <ShieldCheck size={16} />
            <span>{verifying ? 'Recalculating SHA-256 Chain...' : 'Verify Chain Integrity'}</span>
          </button>

          {isAdmin && (
            <button
              className="btn btn-outline"
              onClick={handleSimulateTamper}
              disabled={simulating}
              title="Demonstrates detection of unauthorized database mutation"
              style={{ color: '#b91c1c', borderColor: '#fca5a5' }}
            >
              <Bug size={15} />
              <span>{simulating ? 'Mutating Row...' : 'Simulate Tamper (Demo Test)'}</span>
            </button>
          )}

          <button className="btn btn-outline" onClick={loadAuditLogs}>
            <RefreshCw size={15} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {tamperMessage && (
        <div className="alert-banner alert-warning">
          <AlertOctagon size={18} color="#b45309" style={{ flexShrink: 0 }} />
          <span>{tamperMessage}</span>
        </div>
      )}

      {/* Verification Result Banner */}
      {verificationResult && (
        <div className={`alert-banner ${verificationResult.is_valid ? 'alert-success' : 'alert-danger'}`} style={{ marginBottom: '20px' }}>
          {verificationResult.is_valid ? (
            <CheckCircle2 size={22} color="#16a34a" style={{ flexShrink: 0 }} />
          ) : (
            <ShieldAlert size={22} color="#dc2626" style={{ flexShrink: 0 }} />
          )}
          <div>
            <strong style={{ fontSize: '0.95rem' }}>
              {verificationResult.is_valid ? "CRYPTOGRAPHIC INTEGRITY VERIFIED (VALID)" : "TAMPERING / CORRUPTION DETECTED (INVALID)"}
            </strong>
            <p style={{ margin: '2px 0 0 0', fontSize: '0.825rem' }}>
              {verificationResult.is_valid
                ? `All ${verificationResult.total_records} append-only records recomputed and validated against the genesis block. Zero forged hashes or manipulated timestamps detected.`
                : verificationResult.error_message}
            </p>
          </div>
        </div>
      )}

      {error && <div className="alert-banner alert-danger">{error}</div>}

      {/* Audit Log Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: 'var(--primary-navy)' }}>
            Cryptographic Event Ledger ({logs.length} entries)
          </h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Genesis Hash: 000000000000...
          </span>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            Loading audit records from SQLite database...
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.825rem' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8fafc', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>ID</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>TIMESTAMP</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>ACTOR</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>ACTION</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>ENTITY</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>PAYLOAD DETAILS</th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--secondary-navy)' }}>SHA-256 HASH CHAIN</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--primary-green)' }}>
                      #{log.id}
                    </td>
                    <td style={{ padding: '10px 14px', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      {log.timestamp ? log.timestamp.substring(0, 19).replace('T', ' ') : 'N/A'}
                    </td>
                    <td style={{ padding: '10px 14px', fontWeight: 600 }}>
                      {log.user_name}
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      <span className="badge badge-tag" style={{ fontWeight: 700 }}>
                        {log.action}
                      </span>
                    </td>
                    <td style={{ padding: '10px 14px', fontWeight: 600 }}>
                      {log.entity_type}: {log.entity_id}
                    </td>
                    <td style={{ padding: '10px 14px', maxWidth: '320px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: '#475569' }} title={log.details_json}>
                      {log.details_json}
                    </td>
                    <td style={{ padding: '10px 14px', fontFamily: 'monospace', fontSize: '0.72rem', whiteSpace: 'nowrap' }}>
                      <div style={{ color: 'var(--text-muted)' }}>
                        Prev: {log.previous_hash.substring(0, 10)}...
                      </div>
                      <div style={{ color: 'var(--primary-navy)', fontWeight: 700 }}>
                        Curr: {log.current_hash.substring(0, 10)}...
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
