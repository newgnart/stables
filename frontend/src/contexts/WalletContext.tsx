import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { Web3Provider } from '@ethersproject/providers';
import { Web3ReactProvider, useWeb3React } from '@web3-react/core';
import { InjectedConnector } from '@web3-react/injected-connector';

// Initialize injected connector
export const injected = new InjectedConnector({
  supportedChainIds: [1, 137, 42161], // Ethereum, Polygon, Arbitrum
});

interface WalletContextType {
  connect: () => Promise<void>;
  disconnect: () => void;
  isConnected: boolean;
  address: string | null;
  error: Error | null;
}

const WalletContext = createContext<WalletContextType>({
  connect: async () => {},
  disconnect: () => {},
  isConnected: false,
  address: null,
  error: null,
});

export function useWallet() {
  return useContext(WalletContext);
}

function getLibrary(provider: any): Web3Provider {
  const library = new Web3Provider(provider);
  library.pollingInterval = 12000;
  return library;
}

export function WalletProvider({ children }: { children: ReactNode }) {
  const context = useWeb3React();
  const [isConnecting, setIsConnecting] = useState(false);

  const connect = useCallback(async () => {
    if (isConnecting) return;
    setIsConnecting(true);
    try {
      await context.activate(injected);
    } catch (err) {
      console.error('Failed to connect wallet:', err);
    } finally {
      setIsConnecting(false);
    }
  }, [context, isConnecting]);

  const disconnect = useCallback(() => {
    try {
      context.deactivate();
    } catch (err) {
      console.error('Failed to disconnect wallet:', err);
    }
  }, [context]);

  const value = {
    connect,
    disconnect,
    isConnected: context.active || false,
    address: context.account || null,
    error: context.error || null,
  };

  return (
    <WalletContext.Provider value={value}>
      {children}
    </WalletContext.Provider>
  );
}

export function WalletProviderWrapper({ children }: { children: ReactNode }) {
  return (
    <Web3ReactProvider getLibrary={getLibrary}>
      <WalletProvider>{children}</WalletProvider>
    </Web3ReactProvider>
  );
} 