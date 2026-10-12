import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, AlertTriangle } from 'lucide-react';
import { api } from '../api';

export default function EngineBadge() {
  const [engineInfo, setEngineInfo] = useState({
    active_engine: 'Checking AI Engine...',
    is_semantic: true
  });

  useEffect(() => {
    async function fetchEngine() {
      try {
        const res = await api.getEngineStatus();
        setEngineInfo(res);
      } catch (_) {
        setEngineInfo({
          active_engine: 'TF-IDF Fallback (Offline)',
          is_semantic: false
        });
      }
    }
    fetchEngine();
  }, []);

  const isSemantic = engineInfo.is_semantic;

  return (
    <div 
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 10px',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: 600,
        backgroundColor: isSemantic ? 'rgba(45, 106, 79, 0.25)' : 'rgba(217, 119, 6, 0.2)',
        color: isSemantic ? '#86efac' : '#fde68a',
        border: `1px solid ${isSemantic ? 'rgba(74, 222, 128, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
        cursor: 'default'
      }}
      title={isSemantic ? "Deep semantic dense vector embeddings loaded (sentence-transformers/all-MiniLM-L6-v2)" : "Lexical TF-IDF Vectorizer fallback mode active"}
    >
      <Cpu size={13} />
      <span>{engineInfo.active_engine}</span>
      {isSemantic ? <CheckCircle2 size={12} color="#86efac" /> : <AlertTriangle size={12} color="#fde68a" />}
    </div>
  );
}
