import { httpGet } from "@/shared/api/httpClient";
import { MarketStatus } from "@/features/market/types";

export async function getMarketStatus(): Promise<MarketStatus> {
  return httpGet<MarketStatus>("/market/status");
}

export interface CandleData {
  symbol: string;
  interval: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
  timestamp: string;
}

export async function getCandles(symbol: string, interval: string, limit: number): Promise<CandleData[]> {
  const encodedSymbol = encodeURIComponent(symbol);
  return httpGet<CandleData[]>(`/market/candles/${encodedSymbol}?interval=${interval}&limit=${limit}`);
}