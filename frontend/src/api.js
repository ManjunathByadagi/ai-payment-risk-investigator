const API_BASE = 'http://localhost:8000/api/v1';

export async function fetchHealth() {
  const res = await fetch('http://localhost:8000/health');
  return res.json();
}

export async function fetchSummary() {
  const res = await fetch(`${API_BASE}/analytics/summary`);
  return res.json();
}

export async function fetchRiskDistribution() {
  const res = await fetch(`${API_BASE}/analytics/risk-distribution`);
  return res.json();
}

export async function analyzeTransaction(txnData) {
  const res = await fetch(`${API_BASE}/transactions/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(txnData)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to analyze transaction');
  }
  return res.json();
}

export async function triggerInvestigation(transactionId) {
  const res = await fetch(`${API_BASE}/investigations/${transactionId}`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to trigger investigation');
  }
  return res.json();
}

export async function fetchAuditLogs() {
  const res = await fetch(`${API_BASE}/audit`);
  return res.json();
}
