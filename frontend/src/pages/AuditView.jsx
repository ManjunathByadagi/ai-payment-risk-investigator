import React from 'react';

const eventTypeLabels = {
  TRANSACTION_ANALYSIS: 'Transaction Analysis',
  AI_INVESTIGATION_COMPLETED: 'AI Investigation Completed'
};

export default function AuditView({ logs }) {
  return (
    <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden shadow-md">
      <div class="px-6 py-4 border-b border-gray-700">
        <h2 class="text-lg font-bold text-white">System Audit Logs</h2>
        <p class="text-xs text-gray-400">Immutable trail of scoring evaluations and investigation decisions.</p>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm text-gray-300">
          <thead class="bg-gray-900/60 text-xs uppercase text-gray-400 border-b border-gray-700">
            <tr>
              <th class="px-6 py-3">ID</th>
              <th class="px-6 py-3">Event Type</th>
              <th class="px-6 py-3">Txn ID</th>
              <th class="px-6 py-3">Timestamp</th>
              <th class="px-6 py-3">Decision</th>
              <th class="px-6 py-3">Reason / Details</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700">
            {logs && logs.length > 0 ? (
              logs.map((log) => (
                <tr key={log.id} class="hover:bg-gray-750 transition">
                  <td class="px-6 py-4 text-xs font-mono text-gray-500">#{log.id}</td>
                  <td class="px-6 py-4 font-semibold text-indigo-400 text-xs">{eventTypeLabels[log.event_type] || log.event_type}</td>
                  <td class="px-6 py-4 font-mono text-xs text-white">{log.transaction_id}</td>
                  <td class="px-6 py-4 text-xs text-gray-400">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td class="px-6 py-4">
                    <span class={`inline-block px-2 py-0.5 text-xs font-bold rounded ${
                      log.decision === 'MANUAL_REVIEW' ? 'bg-red-900/60 text-red-300 border border-red-700' :
                      log.decision === 'MONITOR' ? 'bg-yellow-900/60 text-yellow-300 border border-yellow-700' :
                      'bg-green-900/60 text-green-300 border border-green-700'
                    }`}>
                      {log.decision}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-xs text-gray-300 max-w-md truncate">{log.reason}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" class="px-6 py-8 text-center text-gray-500">No audit log records recorded yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
