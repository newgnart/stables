import React from 'react';
import { WalletConnectButton } from '../components/WalletConnectButton';
import { Metrics } from '../components/Metrics';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <WalletConnectButton />
          </div>
          <Metrics />
        </div>
      </div>
    </div>
  );
} 