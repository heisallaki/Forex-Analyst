import { httpGet, httpPost } from "@/shared/api/httpClient";

export interface Portfolio {
  id: string;
  name: string;
  base_currency: string;
  initial_balance: number;
  current_balance: number;
  created_at: string;
}

export interface Trade {
  id: string;
  portfolio_id: string;
  signal_id: string | null;
  symbol: string;
  side: string;
  entry_price: number;
  exit_price: number | null;
  quantity: number;
  stop_loss: number | null;
  take_profit: number | null;
  status: string;
  pnl: number | null;
  opened_at: string;
  closed_at: string | null;
}

export interface PortfolioPerformance {
  current_balance: number;
  initial_balance: number;
  return_pct: number;
  total_trades: number;
  open_trades: number;
  win_rate: number | null;
  profit_factor: number | null;
  gross_profit: number;
  gross_loss: number;
  total_pnl: number;
}

export async function listPortfolios(): Promise<Portfolio[]> {
  return httpGet<Portfolio[]>("/paper/portfolios");
}

export async function createPortfolio(name: string, initialBalance: number): Promise<Portfolio> {
  return httpPost<Portfolio>("/paper/portfolios", { name, initial_balance: initialBalance });
}

export async function getPortfolioPerformance(portfolioId: string): Promise<PortfolioPerformance> {
  return httpGet<PortfolioPerformance>(`/paper/portfolios/${portfolioId}/performance`);
}

export async function listTrades(portfolioId: string, status?: string): Promise<Trade[]> {
  const params = new URLSearchParams({ portfolio_id: portfolioId });
  if (status) {
    params.set("status", status);
  }
  return httpGet<Trade[]>(`/paper/trades?${params.toString()}`);
}

export interface OpenTradePayload {
  portfolio_id: string;
  symbol: string;
  side: "long" | "short";
  quantity?: number;
  risk_amount?: number;
  stop_loss?: number;
  take_profit?: number;
}

export async function openTrade(payload: OpenTradePayload): Promise<Trade> {
  return httpPost<Trade>("/paper/trades", payload);
}

export async function closeTrade(tradeId: string): Promise<Trade> {
  return httpPost<Trade>(`/paper/trades/${tradeId}/close`, {});
}