import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

interface Metric {
  stablecoin: {
    symbol: string;
    chain: {
      name: string;
    };
  };
  transfer_volume: number;
  mint_volume: number;
  burn_volume: number;
  timestamp: string;
}

interface Filters {
  stablecoin?: string;
  chain?: string;
  startDate?: string;
  endDate?: string;
}

export function Metrics() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [filters, setFilters] = useState<Filters>({});

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getMetrics(filters);
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch metrics'));
      // Set some mock data for development
      setMetrics([
        {
          stablecoin: {
            symbol: 'USDC',
            chain: { name: 'Ethereum' }
          },
          transfer_volume: 1000000,
          mint_volume: 500000,
          burn_volume: 300000,
          timestamp: new Date().toISOString()
        },
        {
          stablecoin: {
            symbol: 'USDT',
            chain: { name: 'Polygon' }
          },
          transfer_volume: 800000,
          mint_volume: 400000,
          burn_volume: 200000,
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-4">Loading metrics...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-4">
        <div className="text-red-500 mb-2">Error loading metrics</div>
        <div className="text-sm text-gray-500">Showing mock data for development</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex gap-4 mb-4">
        <select
          className="px-3 py-2 border rounded-lg"
          value={filters.stablecoin || ''}
          onChange={(e) => setFilters({ ...filters, stablecoin: e.target.value })}
        >
          <option value="">All Stablecoins</option>
          <option value="USDC">USDC</option>
          <option value="USDT">USDT</option>
          <option value="DAI">DAI</option>
        </select>

        <select
          className="px-3 py-2 border rounded-lg"
          value={filters.chain || ''}
          onChange={(e) => setFilters({ ...filters, chain: e.target.value })}
        >
          <option value="">All Chains</option>
          <option value="ethereum">Ethereum</option>
          <option value="polygon">Polygon</option>
          <option value="arbitrum">Arbitrum</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Stablecoin
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Chain
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Transfer Volume
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Mint Volume
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Burn Volume
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {metrics.map((metric, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {metric.stablecoin.symbol}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {metric.stablecoin.chain.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {metric.transfer_volume.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {metric.mint_volume.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {metric.burn_volume.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(metric.timestamp).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 