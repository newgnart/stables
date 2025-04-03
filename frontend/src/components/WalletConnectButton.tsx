import React from 'react';
import { useWallet } from '../contexts/WalletContext';

export function WalletConnectButton() {
  const { connect, disconnect, isConnected, address } = useWallet();

  return (
    <button
      onClick={isConnected ? disconnect : connect}
      className="px-4 py-2 font-semibold text-sm bg-blue-500 text-white rounded-lg shadow-sm hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
    >
      {isConnected ? `Connected: ${address?.slice(0, 6)}...${address?.slice(-4)}` : 'Connect Wallet'}
    </button>
  );
} 