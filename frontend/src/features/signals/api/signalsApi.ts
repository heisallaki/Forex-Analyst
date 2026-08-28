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
  is_owner: boolean;
}

export interface SignalBulkActionResponse {
  succeeded: string[];
  skipped: string[];
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