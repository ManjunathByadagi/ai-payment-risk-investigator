import React from 'react';

export default function DashboardView({ summary, recentTxns, onSelectTxn, onPopulatePreset }) {
  return (
    <div class="space-y-6">
      {/* Metric Cards Grid */}
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div class="bg-gray-800 p-5 rounded-xl border border-gray-700 shadow-sm">
          <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Total Evaluated</p>
          <p class="text-2xl font-bold text-white mt-2">{summary?.total_transactions || 0}</p>
        </div>

        <div class="bg-gray-800 p-5 rounded-xl border border-red-900/40 shadow-sm">
          <p class="text-xs font-semibold text-red-400 uppercase tracking-wider">High Risk</p>
          <p class="text-2xl font-bold text-red-500 mt-2">{summary?.high_risk_count || 0}</p>
        </div>

        <div class="bg-gray-800 p-5 rounded-xl border border-yellow-900/40 shadow-sm">
          <p class="text-xs font-semibold text-yellow-400 uppercase tracking-wider">Medium Risk</p>
          <p class="text-2xl font-bold text-yellow-500 mt-2">{summary?.medium_risk_count || 0}</p>
        </div>

        <div class="bg-gray-800 p-5 rounded-xl border border-green-900/40 shadow-sm">
          <p class="text-xs font-semibold text-green-400 uppercase tracking-wider">Low Risk</p>
          <p class="text-2xl font-bold text-green-500 mt-2">{summary?.low_risk_count || 0}</p>
        </div>

        <div class="bg-gray-800 p-5 rounded-xl border border-indigo-900/40 shadow-sm">
          <p class="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Average Risk Probability</p>
          <p class="text-2xl font-bold text-indigo-400 mt-2">{summary?.avg_risk_score ? (summary.avg_risk_score * 100).toFixed(1) + '%' : '0.0%'}</p>
        </div>
      </div>

      {/* Preset Demo Buttons */}
      <div class="bg-gray-800 p-5 rounded-xl border border-gray-700">
        <h3 class="text-sm font-semibold text-gray-300 mb-3">Quick Preset Demos (Click to Load & Analyze):</h3>
        <div class="flex flex-wrap gap-3">
          <button
            onClick={() => onPopulatePreset('low')}
            class="px-3 py-2 text-xs font-medium bg-green-900/50 hover:bg-green-900 text-green-200 border border-green-700 rounded-lg transition"
          >
            1. Normal Low-Risk (Domestic INR)
          </button>
          <button
            onClick={() => onPopulatePreset('medium')}
            class="px-3 py-2 text-xs font-medium bg-yellow-900/50 hover:bg-yellow-900 text-yellow-200 border border-yellow-700 rounded-lg transition"
          >
            2. Medium Risk (Elevated Amount)
          </button>
          <button
            onClick={() => onPopulatePreset('high_device')}
            class="px-3 py-2 text-xs font-medium bg-red-900/50 hover:bg-red-900 text-red-200 border border-red-700 rounded-lg transition"
          >
            3. High Risk (New Device & Geo Mismatch)
          </button>
          <button
            onClick={() => onPopulatePreset('high_velocity')}
            class="px-3 py-2 text-xs font-medium bg-red-900/50 hover:bg-red-900 text-red-200 border border-red-700 rounded-lg transition"
          >
            4. High Risk (High Velocity & Failures)
          </button>
          <button
            onClick={() => onPopulatePreset('high_multi')}
            class="px-3 py-2 text-xs font-medium bg-purple-900/50 hover:bg-purple-900 text-purple-200 border border-purple-700 rounded-lg transition"
          >
            5. High Risk (Multi-Signal Anomaly)
          </button>
        </div>
      </div>

      {/* Recent Analyzed Transactions Table */}
      <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-700 flex justify-between items-center">
          <h3 class="text-base font-semibold text-white">Recent Evaluated Transactions</h3>
          <span class="text-xs text-gray-400">Recent Analysis Results</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm text-gray-300">
            <thead class="bg-gray-900/50 text-xs uppercase text-gray-400 border-b border-gray-700">
              <tr>
                <th class="px-6 py-3">Txn ID</th>
                <th class="px-6 py-3">Amount</th>
                <th class="px-6 py-3">Risk Probability</th>
                <th class="px-6 py-3">Risk Level</th>
                <th class="px-6 py-3">Recommended Decision</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-700">
              {recentTxns && recentTxns.length > 0 ? (
                recentTxns.map((t) => (
                  <tr key={t.transaction_id} class="hover:bg-gray-750 transition cursor-pointer" onClick={() => onSelectTxn(t)}>
                    <td class="px-6 py-4 font-mono text-indigo-400 font-medium">{t.transaction_id}</td>
                    <td class="px-6 py-4 font-semibold text-white">₹{t.amount?.toLocaleString()}</td>
                    <td class="px-6 py-4 font-medium">{(t.risk_probability * 100).toFixed(1)}%</td>
                    <td class="px-6 py-4">
                      <span class={`inline-flex px-2 py-1 text-xs font-bold rounded-md ${
                        t.risk_level === 'HIGH' ? 'bg-red-900/60 text-red-300 border border-red-700' :
                        t.risk_level === 'MEDIUM' ? 'bg-yellow-900/60 text-yellow-300 border border-yellow-700' :
                        'bg-green-900/60 text-green-300 border border-green-700'
                      }`}>
                        {t.risk_level}
                      </span>
                    </td>
                    <td class="px-6 py-4 font-semibold text-gray-200">{t.decision}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" class="px-6 py-8 text-center text-gray-500">No transactions analyzed yet. Use presets above to run instant analyses.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
