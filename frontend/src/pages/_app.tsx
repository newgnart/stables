import type { AppProps } from 'next/app';
import { WalletProviderWrapper } from '../contexts/WalletContext';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <WalletProviderWrapper>
      <Component {...pageProps} />
    </WalletProviderWrapper>
  );
} 