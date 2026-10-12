import React from 'react';
import { Shield, LayoutDashboard, FileText, Search, Clock, Lock, UserCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import EngineBadge from './EngineBadge';

export default function Navbar({ activePage, setActivePage }) {
  const { currentUser, switchPersona, presetUsers } = useAuth();

  return (
    <header style={{
      backgroundColor: 'var(--primary-navy)',
      color: '#ffffff',
      borderBottom: '3px solid var(--primary-green)',
      boxShadow: 'var(--shadow-md)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      {/* Top Bar */}
      <div style={{
        maxWidth: '1440px',
        margin: '0 auto',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', cursor: 'pointer' }} onClick={() => setActivePage('dashboard')}>
          <div style={{
            width: '42px',
            height: '42px',
            backgroundColor: 'var(--primary-green)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
          }}>
            <Shield size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '0.8px', color: '#ffffff' }}>IPMPRS</span>
              <span style={{
                fontSize: '0.65rem',
                backgroundColor: 'rgba(255,255,255,0.12)',
                padding: '2px 6px',
                borderRadius: '4px',
                fontWeight: 600,
                color: '#cbd5e1'
              }}>LAW ENFORCEMENT</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', margin: 0 }}>
              Pondicherry Police Department
            </p>
            <p style={{ fontSize: '0.68rem', color: '#64748b', margin: '2px 0 0 0' }}>
              Secure proposal intelligence &amp; precedent repository
            </p>
          </div>
        </div>

        {/* AI Engine Status & Quick Persona Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <EngineBadge />

          {/* Persona Switcher */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: 'rgba(255,255,255,0.06)',
            padding: '4px 8px',
            borderRadius: '8px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', fontWeight: 600 }}>ROLE SWITCHER:</span>
            {presetUsers.map(u => {
              const isActive = currentUser?.username === u.username;
              return (
                <button
                  key={u.username}
                  onClick={() => switchPersona(u.username)}
                  style={{
                    backgroundColor: isActive ? u.color : 'transparent',
                    color: isActive ? '#ffffff' : '#cbd5e1',
                    border: isActive ? `1px solid rgba(255,255,255,0.3)` : '1px solid transparent',
                    borderRadius: '6px',
                    padding: '3px 8px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    transition: 'all 0.15s ease'
                  }}
                  title={`Switch to ${u.name} (${u.role})`}
                >
                  <UserCheck size={12} />
                  <span>{u.role}</span>
                </button>
              );
            })}
          </div>

          {/* Current Active User Profile */}
          {currentUser && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              paddingLeft: '12px',
              borderLeft: '1px solid rgba(255,255,255,0.15)'
            }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.825rem', fontWeight: 700, color: '#f8fafc' }}>
                  {currentUser.full_name}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                  {currentUser.badge_number} &bull; {currentUser.department}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav style={{
        backgroundColor: 'var(--secondary-navy)',
        borderTop: '1px solid rgba(255,255,255,0.08)',
        padding: '0 24px'
      }}>
        <div style={{
          maxWidth: '1440px',
          margin: '0 auto',
          display: 'flex',
          gap: '4px',
          overflowX: 'auto'
        }}>
          <button
            onClick={() => setActivePage('dashboard')}
            style={{
              padding: '10px 16px',
              fontSize: '0.875rem',
              fontWeight: 600,
              background: 'none',
              border: 'none',
              color: activePage === 'dashboard' ? '#ffffff' : '#94a3b8',
              borderBottom: activePage === 'dashboard' ? '3px solid #52b788' : '3px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <LayoutDashboard size={16} />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => setActivePage('proposals')}
            style={{
              padding: '10px 16px',
              fontSize: '0.875rem',
              fontWeight: 600,
              background: 'none',
              border: 'none',
              color: activePage === 'proposals' ? '#ffffff' : '#94a3b8',
              borderBottom: activePage === 'proposals' ? '3px solid #52b788' : '3px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <FileText size={16} />
            <span>Proposals</span>
          </button>

          <button
            onClick={() => setActivePage('precedents')}
            style={{
              padding: '10px 16px',
              fontSize: '0.875rem',
              fontWeight: 600,
              background: 'none',
              border: 'none',
              color: activePage === 'precedents' ? '#ffffff' : '#94a3b8',
              borderBottom: activePage === 'precedents' ? '3px solid #52b788' : '3px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Search size={16} />
            <span>Precedent Search</span>
          </button>

          <button
            onClick={() => setActivePage('bottlenecks')}
            style={{
              padding: '10px 16px',
              fontSize: '0.875rem',
              fontWeight: 600,
              background: 'none',
              border: 'none',
              color: activePage === 'bottlenecks' ? '#ffffff' : '#94a3b8',
              borderBottom: activePage === 'bottlenecks' ? '3px solid #52b788' : '3px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Clock size={16} />
            <span>Bottlenecks & SLA</span>
          </button>

          <button
            onClick={() => setActivePage('audit')}
            style={{
              padding: '10px 16px',
              fontSize: '0.875rem',
              fontWeight: 600,
              background: 'none',
              border: 'none',
              color: activePage === 'audit' ? '#ffffff' : '#94a3b8',
              borderBottom: activePage === 'audit' ? '3px solid #52b788' : '3px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Lock size={16} />
            <span>Audit Trail & Integrity</span>
          </button>
        </div>
      </nav>
    </header>
  );
}
