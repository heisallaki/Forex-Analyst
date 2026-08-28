import { httpPost } from "@/shared/api/httpClient";

export interface RuleCondition {
  field: string;
  operator: string;
  value?: number | string;
  compare_field?: string;
}

export interface RuleGroup {
  match: string;
  conditions: RuleCondition[];
}

export interface BacktestRunRequest {
  symbol: string;
  intervals: string[];
  limit: number;
  strategy_name: string;
  strategy_description?: string;
  entry_long_rules?: RuleGroup;
  entry_short_rules?: RuleGroup;
  initial_balance: number;
  risk_per_trade_pct: number;
  spread_pips: number;
  slippage_pips: number;
  stop_loss_atr_multiple: number;
  take_profit_atr_multiple: number;
  max_holding_bars: number;
}

export interface TradeResult {
  side: string;
  entry_price: number;
  exit_price: number;
  pnl: number;
  r_multiple: number | null;
  opened_at: string;
  closed_at: string;
  exit_reason: string;
}

export interface BacktestStatistics {
  total_trades: number;
  win_rate: number | null;
  profit_factor: number | null;
  sharpe_ratio: number | null;
  sortino_ratio: number | null;
  max_drawdown_pct: number;
  final_equity: number;
  monthly_performance: Record<string, number>;
}

export interface BacktestIntervalResult {
  interval: string;
  trades: TradeResult[];
  statistics: BacktestStatistics;
}

export interface BacktestRunResponse {
  strategy_id: string;
  strategy_name: string;
  symbol: string;
  results: BacktestIntervalResult[];
}

export async function runBacktest(payload: BacktestRunRequest): Promise<BacktestRunResponse> {
  return httpPost<BacktestRunResponse>("/backtest/run", payload);
}