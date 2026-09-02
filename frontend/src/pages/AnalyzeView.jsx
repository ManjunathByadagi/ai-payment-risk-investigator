import React, { useState, useEffect } from 'react';

export default function AnalyzeView({ initialData, onAnalyze, onTriggerInvestigation, analysisResult, investigationResult, loading, error }) {
  const [formData, setFormData] = useState({
    customer_id: 'CUST_00123',
    merchant_id: 'MERCH_0045',
    amount: 12500.00,
    currency: 'INR',
    customer_country: 'IN',
    transaction_country: 'US',
    device_id: 'DEV_99812',
    device_new: 1,
    customer_account_age_days: 45,
    transactions_last_10_minutes: 4,
    transactions_last_1_hour: 7,
    transactions_last_24_hours: 12,
    average_customer_amount: 149.77,
    merchant_risk_score: 0.45,
    customer_previous_risk_count: 1,
    failed_transactions_last_24_hours: 2,
    ip_risk_score: 0.85,
    unusual_time: 1
  });

  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({ ...prev, ...initialData }));
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onAnalyze(formData);
  };

  // Dynamic evidence mapper
  const ev = investigationResult?.evidence || {};

  const geoTool = ev.check_geographic_consistency;
  const velTool = ev.get_transaction_velocity;
  const devTool = ev.get_device_activity;
  const custTool = ev.get_customer_history;
  const merchTool = ev.get_merchant_statistics;
  const relatedTool = ev.get_recent_related_transactions;
  const customerHistoryAvailable = custTool?.found === true;
  const merchantStatisticsAvailable = merchTool?.found === true;

  const hasGeoSignal = analysisResult?.risk_signals?.some(s => s.signal === 'geographic_mismatch');

  return (
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Left Column: Input Form */}
      <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
        <h2 class="text-lg font-bold text-white mb-4">Transaction Risk Parameters</h2>
        <p class="text-xs text-gray-400 mb-4">High-risk transactions trigger bounded evidence investigation (maximum 4 tool calls).</p>
        <form onSubmit={handleSubmit} class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Customer ID</label>
              <input
                type="text"
                name="customer_id"
                value={formData.customer_id}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                required
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Merchant ID</label>
              <input
                type="text"
                name="merchant_id"
                value={formData.merchant_id}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                required
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Amount (INR)</label>
              <input
                type="number"
                step="0.01"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                required
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Declared Customer Avg (INR)</label>
              <input
                type="number"
                step="0.01"
                name="average_customer_amount"
                value={formData.average_customer_amount}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                required
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Customer Country</label>
              <input
                type="text"
                name="customer_country"
                value={formData.customer_country}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Transaction Country</label>
              <input
                type="text"
                name="transaction_country"
                value={formData.transaction_country}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Device ID</label>
              <input
                type="text"
                name="device_id"
                value={formData.device_id}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">New Device?</label>
              <select
                name="device_new"
                value={formData.device_new}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              >
                <option value={0}>No (0)</option>
                <option value={1}>Yes (1)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">IP Risk (0-1)</label>
              <input
                type="number"
                step="0.05"
                name="ip_risk_score"
                value={formData.ip_risk_score}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Txns (10m)</label>
              <input
                type="number"
                name="transactions_last_10_minutes"
                value={formData.transactions_last_10_minutes}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Txns (1h)</label>
              <input
                type="number"
                name="transactions_last_1_hour"
                value={formData.transactions_last_1_hour}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-400 mb-1">Failed (24h)</label>
              <input
                type="number"
                name="failed_transactions_last_24_hours"
                value={formData.failed_transactions_last_24_hours}
                onChange={handleChange}
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg shadow-md transition duration-150 disabled:opacity-50 mt-4"
          >
            {loading ? 'Evaluating Model...' : 'Run Risk Scoring & Analysis'}
          </button>
        </form>
      </div>

      {/* Right Column: Analysis & Agent Output */}
      <div class="space-y-6">
        {error && (
          <div class="p-4 bg-red-900/50 border border-red-700 text-red-200 text-sm rounded-xl">
            {error}
          </div>
        )}

        {analysisResult && (
          <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md space-y-4">
            <div class="flex justify-between items-center pb-4 border-b border-gray-700">
              <div>
                <span class="text-xs text-gray-400 font-mono">TXN ID: {analysisResult.transaction_id}</span>
                <h3 class="text-xl font-bold text-white">Scoring Result</h3>
              </div>
              <div class="text-right">
                <span class={`inline-block px-3 py-1 text-sm font-bold rounded-lg ${
                  analysisResult.risk_level === 'HIGH' ? 'bg-red-900/80 text-red-200 border border-red-600' :
                  analysisResult.risk_level === 'MEDIUM' ? 'bg-yellow-900/80 text-yellow-200 border border-yellow-600' :
                  'bg-green-900/80 text-green-200 border border-green-600'
                }`}>
                  {analysisResult.risk_level} RISK
                </span>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4 bg-gray-900/60 p-4 rounded-lg">
              <div>
                <p class="text-xs text-gray-400">Risk Probability Score</p>
                <p class="text-2xl font-black text-indigo-400">{(analysisResult.risk_probability * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">Recommended Action</p>
                <p class="text-2xl font-black text-white">{analysisResult.decision}</p>
              </div>
            </div>

            {/* Risk Signals List */}
            <div>
              <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">ML Risk Signals Detected</h4>
              {analysisResult.risk_signals && analysisResult.risk_signals.length > 0 ? (
                <ul class="space-y-2">
                  {analysisResult.risk_signals.map((sig, idx) => (
                    <li key={idx} class="p-3 bg-gray-900/80 rounded-lg border-l-4 border-amber-500 text-xs text-gray-200">
                      <span class="font-semibold text-amber-400 uppercase mr-2">[{sig.severity}]</span>
                      {sig.description}
                    </li>
                  ))}
                </ul>
              ) : (
                <p class="text-xs text-gray-500 italic">No significant risk anomaly signals detected.</p>
              )}
            </div>

            {/* HIGH is automatic; MEDIUM remains a manual/optional action. */}
            {analysisResult.investigation_available && !investigationResult && (
              <div class="pt-2">
                <button
                  onClick={() => onTriggerInvestigation(analysisResult.transaction_id)}
                  disabled={loading}
                  class="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white font-semibold rounded-lg shadow-md transition"
                >
                  {loading ? 'Agent Investigating Tools...' : analysisResult.risk_level === 'MEDIUM' ? 'Optionally Investigate with AI Agent' : 'Investigate with AI Agent'}
                </button>
              </div>
            )}
          </div>
        )}

        {/* AI Agent Report Output */}
        {investigationResult && (
          <div class="bg-gray-800 p-6 rounded-xl border border-amber-500/40 shadow-lg space-y-4">
            <div class="flex justify-between items-center border-b border-gray-700 pb-3">
              <h3 class="text-lg font-bold text-amber-400 flex items-center">
                AI Risk Agent Investigation Report
              </h3>
              <span class="text-xs bg-amber-900/60 text-amber-200 px-2.5 py-1 rounded-full font-medium">
                {investigationResult.is_llm_generated ? 'LLM Enhanced' : 'Deterministic Evidence Tools'}
              </span>
            </div>

            <div class="bg-gray-900/90 p-4 rounded-lg font-mono text-xs text-gray-300 leading-relaxed whitespace-pre-wrap border border-gray-700">
              {investigationResult.investigation_summary}
            </div>

            <div class="grid grid-cols-3 gap-3 text-xs">
              <div class="bg-gray-900 p-3 rounded-lg border border-gray-700">
                <span class="text-gray-400 block">Evidence Strength</span>
                <span class="text-sm font-bold text-indigo-300">{investigationResult.evidence_strength || ev._evidence_strength || 'HIGH'}</span>
              </div>
              <div class="bg-gray-900 p-3 rounded-lg border border-gray-700">
                <span class="text-gray-400 block">Investigation Coverage</span>
                <span class="text-sm font-bold text-indigo-300">
                  {investigationResult.tools_executed_count || ev._tools_executed_count || 2} / {investigationResult.max_tools || ev._max_tools || 4} Tools
                </span>
              </div>
              <div class="bg-gray-900 p-3 rounded-lg border border-gray-700">
                <span class="text-gray-400 block">Recommended Action</span>
                <span class="text-sm font-bold text-amber-400">{investigationResult.recommended_action}</span>
              </div>
              <div class="bg-gray-900 p-3 rounded-lg border border-gray-700">
                <span class="text-gray-400 block">Investigation Confidence</span>
                <span class="text-sm font-bold text-indigo-300">
                  {typeof investigationResult.confidence_score === 'number' ? `${(investigationResult.confidence_score * 100).toFixed(1)}%` : 'Unavailable'}
                </span>
              </div>
            </div>

            {/* Investigation Steps Audit Display */}
            {(investigationResult.investigation_steps || ev._investigation_steps) && (
              <div>
                <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Dynamic Agent Execution Steps</h4>
                <div class="space-y-2">
                  {(investigationResult.investigation_steps || ev._investigation_steps).map((s, idx) => (
                    <div key={idx} class="p-2.5 bg-gray-900/90 rounded-lg border border-gray-700 text-xs">
                      <div class="flex justify-between items-center font-mono text-indigo-400 mb-1">
                        <span>Step {s.step}: {s.tool_name}</span>
                        <span class="text-xs text-green-400 font-sans">Completed</span>
                      </div>
                      <p class="text-gray-300 text-xs">{s.reason}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Structured Deterministic Tool Evidence Grid */}
            <div>
              <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Deterministic Tool Evidence</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                
                {/* 1. Device Activity Tool */}
                <div class="p-3 bg-gray-900 rounded-lg border border-gray-700 space-y-1">
                  <div class="flex justify-between items-center">
                    <span class="font-bold text-gray-200">Device Activity</span>
                    <span class={`px-2 py-0.5 rounded text-[10px] font-bold ${devTool ? 'bg-green-900/70 text-green-300 border border-green-700' : 'bg-gray-800 text-gray-400 border border-gray-700'}`}>
                      {devTool ? 'VERIFIED' : 'NOT CHECKED'}
                    </span>
                  </div>
                  {devTool ? (
                    <p class="text-gray-300">
                      <span class="font-bold text-amber-400">{devTool.device_risk_level} RISK</span> — {devTool.is_new_device ? 'New Device' : 'Known Device'} ({devTool.device_id}), IP Risk: {devTool.ip_risk_score}
                    </p>
                  ) : (
                    <p class="text-gray-500 italic">Tool unexecuted by agent planner.</p>
                  )}
                </div>

                {/* 2. Transaction Velocity Tool */}
                <div class="p-3 bg-gray-900 rounded-lg border border-gray-700 space-y-1">
                  <div class="flex justify-between items-center">
                    <span class="font-bold text-gray-200">Transaction Velocity</span>
                    <span class={`px-2 py-0.5 rounded text-[10px] font-bold ${velTool ? 'bg-green-900/70 text-green-300 border border-green-700' : 'bg-gray-800 text-gray-400 border border-gray-700'}`}>
                      {velTool ? 'VERIFIED' : 'NOT CHECKED'}
                    </span>
                  </div>
                  {velTool ? (
                    <p class="text-gray-300">
                      <span class="font-bold text-amber-400">{velTool.velocity_status} VELOCITY</span> — {velTool.transactions_last_10_minutes} txns in 10m ({velTool.transactions_last_1_hour} in 1h, {velTool.failed_transactions_last_24_hours} failed in 24h)
                    </p>
                  ) : (
                    <p class="text-gray-500 italic">Tool unexecuted by agent planner.</p>
                  )}
                </div>

                {/* 3. Geographic Consistency Tool */}
                <div class="p-3 bg-gray-900 rounded-lg border border-gray-700 space-y-1">
                  <div class="flex justify-between items-center">
                    <span class="font-bold text-gray-200">Geographic Consistency</span>
                    <span class={`px-2 py-0.5 rounded text-[10px] font-bold ${geoTool ? 'bg-green-900/70 text-green-300 border border-green-700' : 'bg-gray-800 text-gray-400 border border-gray-700'}`}>
                      {geoTool ? 'VERIFIED' : 'NOT CHECKED'}
                    </span>
                  </div>
                  {geoTool ? (
                    <p class="text-gray-300">
                      <span class="font-bold text-amber-400">{geoTool.geo_risk_level} RISK</span> — {geoTool.geographic_mismatch ? `MISMATCH (${geoTool.transaction_country} vs ${geoTool.home_country})` : `CONSISTENT (${geoTool.transaction_country})`}
                    </p>
                  ) : (
                    <p class="text-gray-500 italic">
                      {hasGeoSignal ? 'ML Signal: Mismatch detected | Tool Verification: NOT CHECKED' : 'Tool unexecuted by agent planner.'}
                    </p>
                  )}
                </div>

                {/* 4. Customer History Tool */}
                <div class="p-3 bg-gray-900 rounded-lg border border-gray-700 space-y-1">
                  <div class="flex justify-between items-center">
                    <span class="font-bold text-gray-200">Customer Spend History</span>
                    <span class={`px-2 py-0.5 rounded text-[10px] font-bold ${customerHistoryAvailable ? 'bg-green-900/70 text-green-300 border border-green-700' : custTool ? 'bg-yellow-900/70 text-yellow-300 border border-yellow-700' : 'bg-gray-800 text-gray-400 border border-gray-700'}`}>
                      {customerHistoryAvailable ? 'VERIFIED' : custTool ? 'NOT AVAILABLE' : 'NOT CHECKED'}
                    </span>
                  </div>
                  {customerHistoryAvailable ? (
                    <p class="text-gray-300">
                      Ledger Historical Avg: ₹{custTool.average_amount} ({custTool.total_historical_transactions} txns){custTool.declared_benchmark_amount ? ` | Declared Benchmark: ₹${custTool.declared_benchmark_amount}` : ''}, {custTool.previous_risk_flags} prior flags
                    </p>
                  ) : custTool ? (
                    <p class="text-gray-500 italic">No historical ledger data available for this customer.</p>
                  ) : (
                    <p class="text-gray-500 italic">Tool unexecuted by agent planner.</p>
                  )}
                </div>

                {/* 5. Merchant Statistics Tool */}
                <div class="p-3 bg-gray-900 rounded-lg border border-gray-700 space-y-1">
                  <div class="flex justify-between items-center">
                    <span class="font-bold text-gray-200">Merchant Risk Profile</span>
                    <span class={`px-2 py-0.5 rounded text-[10px] font-bold ${merchantStatisticsAvailable ? 'bg-green-900/70 text-green-300 border border-green-700' : merchTool ? 'bg-yellow-900/70 text-yellow-300 border border-yellow-700' : 'bg-gray-800 text-gray-400 border border-gray-700'}`}>
                      {merchantStatisticsAvailable ? 'VERIFIED' : merchTool ? 'NOT AVAILABLE' : 'NOT CHECKED'}
                    </span>
                  </div>
                  {merchantStatisticsAvailable ? (
                    <p class="text-gray-300">
                      Risk Score: {merchTool.merchant_risk_score}, Dispute Rate: {(merchTool.dispute_rate * 100).toFixed(1)}%
                    </p>
                  ) : merchTool ? (
                    <p class="text-gray-500 italic">No merchant ledger data available for this merchant.</p>
                  ) : (
                    <p class="text-gray-500 italic">Tool unexecuted by agent planner.</p>
                  )}
                </div>

                {/* 6. Recent Related Transactions Tool */}
                <div class="p-3 bg-gray-900 rounded-lg border border-gray-700 space-y-1">
                  <div class="flex justify-between items-center">
                    <span class="font-bold text-gray-200">Related Customer/Merchant Txns</span>
                    <span class={`px-2 py-0.5 rounded text-[10px] font-bold ${relatedTool ? 'bg-green-900/70 text-green-300 border border-green-700' : 'bg-gray-800 text-gray-400 border border-gray-700'}`}>
                      {relatedTool ? 'VERIFIED' : 'NOT CHECKED'}
                    </span>
                  </div>
                  {relatedTool ? (
                    <p class="text-gray-300">
                      {relatedTool.related_count} related txns ({relatedTool.recent_flagged_count} flagged)
                    </p>
                  ) : (
                    <p class="text-gray-500 italic">Tool unexecuted by agent planner.</p>
                  )}
                </div>

              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
