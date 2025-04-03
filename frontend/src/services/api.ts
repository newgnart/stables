interface Filters {
  stablecoin?: string;
  chain?: string;
  startDate?: string;
  endDate?: string;
}

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = {
  async getMetrics(filters: Filters = {}) {
    const params = new URLSearchParams();
    if (filters.stablecoin) params.append("stablecoin", filters.stablecoin);
    if (filters.chain) params.append("chain", filters.chain);
    if (filters.startDate) params.append("start_date", filters.startDate);
    if (filters.endDate) params.append("end_date", filters.endDate);

    const response = await fetch(`${API_URL}/api/metrics?${params.toString()}`);
    if (!response.ok) {
      throw new Error("Failed to fetch metrics");
    }
    return response.json();
  },
};
