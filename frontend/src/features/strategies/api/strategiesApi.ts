import { httpGet } from "@/shared/api/httpClient";

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