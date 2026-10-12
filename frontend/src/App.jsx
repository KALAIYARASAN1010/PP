import React, { useState } from 'react';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ProposalList from './pages/ProposalList';
import ProposalCreate from './pages/ProposalCreate';
import ProposalDetail from './pages/ProposalDetail';
import PrecedentSearch from './pages/PrecedentSearch';
import BottleneckAnalytics from './pages/BottleneckAnalytics';
import AuditTrail from './pages/AuditTrail';

function MainApp() {
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedProposalId, setSelectedProposalId] = useState(null);

  const handleSelectProposal = (id) => {
    setSelectedProposalId(id);
    setActivePage('detail');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar 
        activePage={activePage} 
        setActivePage={(page) => {
          setActivePage(page);
          if (page !== 'detail') setSelectedProposalId(null);
        }} 
      />

      <main style={{ flex: 1, paddingBottom: '48px' }}>
        {activePage === 'dashboard' && (
          <Dashboard 
            setActivePage={setActivePage} 
            onSelectProposal={handleSelectProposal} 
          />
        )}

        {activePage === 'proposals' && (
          <ProposalList 
            setActivePage={setActivePage} 
            onSelectProposal={handleSelectProposal} 
          />
        )}

        {activePage === 'create' && (
          <ProposalCreate 
            setActivePage={setActivePage} 
            onSelectProposal={handleSelectProposal} 
          />
        )}

        {activePage === 'detail' && selectedProposalId && (
          <ProposalDetail 
            proposalId={selectedProposalId} 
            setActivePage={setActivePage}
            onSelectProposal={handleSelectProposal}
          />
        )}

        {activePage === 'precedents' && (
          <PrecedentSearch 
            onSelectProposal={handleSelectProposal} 
          />
        )}

        {activePage === 'bottlenecks' && (
          <BottleneckAnalytics 
            onSelectProposal={handleSelectProposal} 
          />
        )}

        {activePage === 'audit' && (
          <AuditTrail />
        )}
      </main>

      <footer style={{
        backgroundColor: 'var(--primary-navy)',
        color: '#94a3b8',
        borderTop: '1px solid rgba(255,255,255,0.08)',
        padding: '16px 24px',
        textAlign: 'center',
        fontSize: '0.78rem'
      }}>
        <div style={{ maxWidth: '1440px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <div>
            <strong>IPMPRS</strong> &bull; Pondicherry Police Proposal Intelligence System
          </div>
          <div>
            Pondicherry Police Department &bull; Secure institutional workspace
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
