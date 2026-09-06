import { httpGet, httpPost } from "@/shared/api/httpClient";

export interface StrategyListItem {
  id: string;
  name: string;
  description: string | null;
  version: number;
  is_active: boolean;
}

export async function listStrategies(): Promise<StrategyListItem[]> {
  return httpGet<StrategyListItem[]>("/backtest/strategies");
}

export async function deactivateStrategy(strategyId: string): Promise<void> {
  await httpPost<void>(`/backtest/strategies/${strategyId}/deactivate`, {}, "PATCH");
}

export async function deleteStrategy(strategyId: string): Promise<void> {
  await httpPost<void>(`/backtest/strategies/${strategyId}`, {}, "DELETE");
}