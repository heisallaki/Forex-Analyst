import { httpGet } from "@/shared/api/httpClient";

export interface SignalListItem {
  id: string;
  strategy_id: string | null;
  symbol: string;
  direction: string;
  confidence: number;
  reasoning: Record<string, unknown>;
  created_at: string;
}

export async function listSignals(symbol: string | null, limit: number): Promise<SignalListItem[]> {
  const params = new URLSearchParams();
  if (symbol) {
    params.set("symbol", symbol);
  }
  params.set("limit", String(limit));
  return httpGet<SignalListItem[]>(`/decision/signals?${params.toString()}`);
}