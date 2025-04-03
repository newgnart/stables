import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { WalletConnectButton } from '../WalletConnectButton';
import { WalletProviderWrapper } from '../../contexts/WalletContext';

// Mock the useWallet hook
jest.mock('../../contexts/WalletContext', () => ({
  ...jest.requireActual('../../contexts/WalletContext'),
  useWallet: () => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    isConnected: false,
    address: null,
    error: null,
  }),
}));

describe('WalletConnectButton', () => {
  it('renders connect button when wallet is not connected', () => {
    render(
      <WalletProviderWrapper>
        <WalletConnectButton />
      </WalletProviderWrapper>
    );
    
    expect(screen.getByText('Connect Wallet')).toBeInTheDocument();
  });

  it('renders connected state with truncated address when wallet is connected', () => {
    const mockAddress = '0x1234567890abcdef1234567890abcdef12345678';
    jest.spyOn(require('../../contexts/WalletContext'), 'useWallet').mockImplementation(() => ({
      connect: jest.fn(),
      disconnect: jest.fn(),
      isConnected: true,
      address: mockAddress,
      error: null,
    }));

    render(
      <WalletProviderWrapper>
        <WalletConnectButton />
      </WalletProviderWrapper>
    );
    
    expect(screen.getByText(`Connected: ${mockAddress.slice(0, 6)}...${mockAddress.slice(-4)}`)).toBeInTheDocument();
  });

  it('calls connect function when clicked in disconnected state', () => {
    const mockConnect = jest.fn();
    jest.spyOn(require('../../contexts/WalletContext'), 'useWallet').mockImplementation(() => ({
      connect: mockConnect,
      disconnect: jest.fn(),
      isConnected: false,
      address: null,
      error: null,
    }));

    render(
      <WalletProviderWrapper>
        <WalletConnectButton />
      </WalletProviderWrapper>
    );
    
    fireEvent.click(screen.getByText('Connect Wallet'));
    expect(mockConnect).toHaveBeenCalled();
  });

  it('calls disconnect function when clicked in connected state', () => {
    const mockDisconnect = jest.fn();
    const mockAddress = '0x1234567890abcdef1234567890abcdef12345678';
    jest.spyOn(require('../../contexts/WalletContext'), 'useWallet').mockImplementation(() => ({
      connect: jest.fn(),
      disconnect: mockDisconnect,
      isConnected: true,
      address: mockAddress,
      error: null,
    }));

    render(
      <WalletProviderWrapper>
        <WalletConnectButton />
      </WalletProviderWrapper>
    );
    
    fireEvent.click(screen.getByText(`Connected: ${mockAddress.slice(0, 6)}...${mockAddress.slice(-4)}`));
    expect(mockDisconnect).toHaveBeenCalled();
  });
}); 