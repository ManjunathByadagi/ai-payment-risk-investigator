import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar.jsx';
import DashboardView from './pages/DashboardView.jsx';
import AnalyzeView from './pages/AnalyzeView.jsx';
import AuditView from './pages/AuditView.jsx';
import { fetchSummary, fetchRiskDistribution, analyzeTransaction, triggerInvestigation, fetchAuditLogs } from './api.js';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [summary, setSummary] = useState(null);
  const [recentTxns, setRecentTxns] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [presetData, setPresetData] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [investigationResult, setInvestigationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadDashboardData = async () => {
    try {
      const sum = await fetchSummary();
      const dist = await fetchRiskDistribution();
      const logs = await fetchAuditLogs();
      setSummary(sum);
      setRecentTxns(dist.recent_transactions || []);
      setAuditLogs(logs || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleAnalyze = async (formData) => {
    setLoading(true);
    setError(null);
    setInvestigationResult(null);
    try {
      const res = await analyzeTransaction(formData);
      setAnalysisResult(res);
      if (res.risk_level === 'HIGH') {
        const investigation = await triggerInvestigation(res.transaction_id);
        setInvestigationResult(investigation);
      }
      await loadDashboardData();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerInvestigation = async (transactionId) => {
    setLoading(true);
    setError(null);
    try {
      const res = await triggerInvestigation(transactionId);
      setInvestigationResult(res);
      await loadDashboardData();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePopulatePreset = (type) => {
    let preset = {};
    if (type === 'low') {
      preset = {
        customer_id: 'CUST_00001',
        merchant_id: 'MERCH_0012',
        amount: 350.00,
        currency: 'INR',
        customer_country: 'IN',
        transaction_country: 'IN',
        device_id: 'DEV_00001',
        device_new: 0,
        customer_account_age_days: 450,
        transactions_last_10_minutes: 0,
        transactions_last_1_hour: 1,
        transactions_last_24_hours: 2,
        average_customer_amount: 400.00,
        merchant_risk_score: 0.02,
        customer_previous_risk_count: 0,
        failed_transactions_last_24_hours: 0,
        ip_risk_score: 0.05,
        unusual_time: 0
      };
    } else if (type === 'medium') {
      preset = {
        customer_id: 'CUST_00250',
        merchant_id: 'MERCH_0088',
        amount: 2200.00,
        currency: 'INR',
        customer_country: 'IN',
        transaction_country: 'IN',
        device_id: 'DEV_00250',
        device_new: 0,
        customer_account_age_days: 120,
        transactions_last_10_minutes: 1,
        transactions_last_1_hour: 3,
        transactions_last_24_hours: 5,
        average_customer_amount: 350.00,
        merchant_risk_score: 0.25,
        customer_previous_risk_count: 1,
        failed_transactions_last_24_hours: 1,
        ip_risk_score: 0.35,
        unusual_time: 1
      };
    } else if (type === 'high_device') {
      preset = {
        customer_id: 'CUST_00800',
        merchant_id: 'MERCH_0300',
        amount: 18500.00,
        currency: 'INR',
        customer_country: 'IN',
        transaction_country: 'US',
        device_id: 'DEV_99999',
        device_new: 1,
        customer_account_age_days: 30,
        transactions_last_10_minutes: 2,
        transactions_last_1_hour: 4,
        transactions_last_24_hours: 8,
        average_customer_amount: 900.00,
        merchant_risk_score: 0.65,
        customer_previous_risk_count: 2,
        failed_transactions_last_24_hours: 2,
        ip_risk_score: 0.88,
        unusual_time: 1
      };
    } else if (type === 'high_velocity') {
      preset = {
        customer_id: 'CUST_01500',
        merchant_id: 'MERCH_0500',
        amount: 9500.00,
        currency: 'INR',
        customer_country: 'IN',
        transaction_country: 'IN',
        device_id: 'DEV_01500',
        device_new: 0,
        customer_account_age_days: 15,
        transactions_last_10_minutes: 6,
        transactions_last_1_hour: 12,
        transactions_last_24_hours: 25,
        average_customer_amount: 500.00,
        merchant_risk_score: 0.50,
        customer_previous_risk_count: 3,
        failed_transactions_last_24_hours: 4,
        ip_risk_score: 0.70,
        unusual_time: 1
      };
    } else if (type === 'high_multi') {
      preset = {
        customer_id: 'CUST_02800',
        merchant_id: 'MERCH_0750',
        amount: 45000.00,
        currency: 'INR',
        customer_country: 'IN',
        transaction_country: 'AE',
        device_id: 'DEV_88888',
        device_new: 1,
        customer_account_age_days: 5,
        transactions_last_10_minutes: 5,
        transactions_last_1_hour: 10,
        transactions_last_24_hours: 18,
        average_customer_amount: 1000.00,
        merchant_risk_score: 0.85,
        customer_previous_risk_count: 4,
        failed_transactions_last_24_hours: 5,
        ip_risk_score: 0.95,
        unusual_time: 1
      };
    }
    setPresetData(preset);
    setActiveTab('analyze');
    handleAnalyze(preset);
  };

  return (
    <div class="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main class="flex-1 max-w-7xl w-full mx-auto p-6">
        {activeTab === 'dashboard' && (
          <DashboardView
            summary={summary}
            recentTxns={recentTxns}
            onSelectTxn={(t) => {
              setActiveTab('analyze');
            }}
            onPopulatePreset={handlePopulatePreset}
          />
        )}

        {activeTab === 'analyze' && (
          <AnalyzeView
            initialData={presetData}
            onAnalyze={handleAnalyze}
            onTriggerInvestigation={handleTriggerInvestigation}
            analysisResult={analysisResult}
            investigationResult={investigationResult}
            loading={loading}
            error={error}
          />
        )}

        {activeTab === 'audit' && (
          <AuditView logs={auditLogs} />
        )}
      </main>
    </div>
  );
}
