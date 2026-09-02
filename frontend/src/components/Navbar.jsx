import React from 'react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header class="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg">
          R
        </div>
        <div>
          <h1 class="text-xl font-bold text-white tracking-wide">AI Payment Risk Investigator</h1>
          <p class="text-xs text-gray-400">Defensive Autonomous Risk Detection & Evidence Agent</p>
        </div>
      </div>

      <nav class="flex space-x-2">
        <button
          onClick={() => setActiveTab('dashboard')}
          class={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'dashboard'
              ? 'bg-indigo-600 text-white'
              : 'text-gray-300 hover:bg-gray-700 hover:text-white'
          }`}
        >
          Dashboard Analytics
        </button>
        <button
          onClick={() => setActiveTab('analyze')}
          class={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'analyze'
              ? 'bg-indigo-600 text-white'
              : 'text-gray-300 hover:bg-gray-700 hover:text-white'
          }`}
        >
          Analyze Transaction
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          class={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'audit'
              ? 'bg-indigo-600 text-white'
              : 'text-gray-300 hover:bg-gray-700 hover:text-white'
          }`}
        >
          Audit Log
        </button>
      </nav>
    </header>
  );
}
