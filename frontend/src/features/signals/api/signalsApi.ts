import { httpGet, httpPost } from "@/shared/api/httpClient";

export interface SignalListItem {
  id: string;
  strategy_id: string | null;
  symbol: string;
  direction: string;
  confidence: number;
  reasoning: Record<string, unknown>;
  created_at: string;
  hidden_at: string | null;
  outcome: string | null;
  evaluated_at: string | null;
  is_owner: boolean;
}

export interface SignalBulkActionResponse {
  succeeded: string[];
  skipped: string[];
}

export interface AccuracyStats {
  total_evaluated: number;
  wins: number;
  losses: number;
  flats: number;
  win_rate: number | null;
  long_win_rate: number | null;
  short_win_rate: number | null;
}

export interface EvaluateSignalsResult {
  evaluated: number;
  skipped: number;
}

export async function listSignals(symbol: string | null, limit: number, includeHidden = false): Promise<SignalListItem[]> {
  const params = new URLSearchParams();
  if (symbol) {
    params.set("symbol", symbol);
  }
  params.set("limit", String(limit));
  params.set("include_hidden", String(includeHidden));
  return httpGet<SignalListItem[]>(`/decision/signals?${params.toString()}`);
}

export async function hideSignals(signalIds: string[]): Promise<SignalBulkActionResponse> {
  return httpPost<SignalBulkActionResponse>("/decision/signals/hide", { signal_ids: signalIds });
}

export async function unhideSignals(signalIds: string[]): Promise<SignalBulkActionResponse> {
  return httpPost<SignalBulkActionResponse>("/decision/signals/unhide", { signal_ids: signalIds });
}

export async function deleteSignals(signalIds: string[]): Promise<SignalBulkActionResponse> {
  return httpPost<SignalBulkActionResponse>("/decision/signals/delete", { signal_ids: signalIds });
}

export async function getAccuracyStats(): Promise<AccuracyStats> {
  return httpGet<AccuracyStats>("/decision/accuracy");
}

export async function evaluatePendingSignals(): Promise<EvaluateSignalsResult> {
  return httpPost<EvaluateSignalsResult>("/decision/signals/evaluate", {});
}