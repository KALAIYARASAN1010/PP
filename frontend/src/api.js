const BASE_URL = '/api';

export function getAuthToken() {
  return localStorage.getItem('ipmprs_token') || '';
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('ipmprs_token', token);
  } else {
    localStorage.removeItem('ipmprs_token');
  }
}

async function request(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    ...(options.headers || {})
  };

  // Add JSON Content-Type only if body is not FormData
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let errorDetail = `Request failed (${response.status})`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch (_) {
      errorDetail = await response.text();
    }
    const error = new Error(errorDetail);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) return null;
  return await response.json();
}

export const api = {
  // Auth
  login: async (username, password) => {
    return await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
  },
  getCurrentUser: async () => {
    return await request('/auth/me');
  },
  getUsers: async () => {
    return await request('/auth/users');
  },

  // Proposals
  getProposals: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.status) query.append('status', params.status);
    if (params.department) query.append('department', params.department);
    if (params.search) query.append('search', params.search);
    const qs = query.toString();
    return await request(`/proposals${qs ? `?${qs}` : ''}`);
  },
  getProposal: async (id) => {
    return await request(`/proposals/${id}`);
  },
  createProposal: async (data) => {
    return await request('/proposals', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  updateProposal: async (id, data) => {
    return await request(`/proposals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },
  submitProposal: async (id) => {
    return await request(`/proposals/${id}/submit`, {
      method: 'POST'
    });
  },
  uploadProposalPdf: async (id, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return await request(`/proposals/${id}/upload-pdf`, {
      method: 'POST',
      body: formData
    });
  },
  getProposalLineage: async (id) => {
    return await request(`/proposals/${id}/lineage`);
  },
  getProposalBrief: async (id) => {
    return await request(`/proposals/${id}/brief`);
  },

  // Precedents & Retrieval
  searchPrecedents: async (searchPayload) => {
    return await request('/precedents/search', {
      method: 'POST',
      body: JSON.stringify(searchPayload)
    });
  },
  checkDuplicates: async ({ title, description, category, current_proposal_id }) => {
    const params = new URLSearchParams({ title, description: description || '', category });
    if (current_proposal_id) params.append('current_proposal_id', current_proposal_id);
    return await request(`/precedents/check-duplicates?${params.toString()}`, {
      method: 'POST'
    });
  },
  getRiskChecklist: async ({ category, description }) => {
    const params = new URLSearchParams({ category, description: description || '' });
    return await request(`/precedents/risk-checklist?${params.toString()}`);
  },
  getCostBenchmark: async ({ cost, category }) => {
    const params = new URLSearchParams({ cost, category });
    return await request(`/precedents/cost-benchmark?${params.toString()}`);
  },
  getConflicts: async ({ category, description }) => {
    const params = new URLSearchParams({ category, description: description || '' });
    return await request(`/precedents/conflicts?${params.toString()}`);
  },
  getSideBySide: async (currentId, precedentId) => {
    return await request(`/precedents/side-by-side/${currentId}/${precedentId}`);
  },

  // Workflow & Decision
  makeDecision: async (proposalId, { action, reason }) => {
    return await request(`/workflow/${proposalId}/decide`, {
      method: 'POST',
      body: JSON.stringify({ action, reason })
    });
  },
  markUnderReview: async (proposalId) => {
    return await request(`/workflow/${proposalId}/under-review`, {
      method: 'POST'
    });
  },

  // Audit
  getAuditLogs: async () => {
    return await request('/audit/logs');
  },
  verifyAuditIntegrity: async () => {
    return await request('/audit/verify');
  },
  simulateAuditTamper: async (recordId) => {
    return await request(`/audit/simulate-tamper?record_id=${recordId}`, {
      method: 'POST'
    });
  },

  // Analytics & Dashboard
  getDashboardStats: async () => {
    return await request('/analytics/dashboard');
  },
  getBottlenecks: async () => {
    return await request('/analytics/bottlenecks');
  },
  getEngineStatus: async () => {
    return await request('/analytics/engine-status');
  }
};
