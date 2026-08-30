import { httpGet, httpPost } from "@/shared/api/httpClient";

export interface ModelPrediction {
  model_name: string;
  prediction_type: string;
  output: Record<string, unknown>;
  created_at: string | null;
}

export interface PredictMarketResponse {
  symbol: string;
  interval: string;
  timestamp: string;
  predictions: ModelPrediction[];
  note: string;
}

export interface RecommendationResponse {
  symbol: string;
  interval: string;
  generated_at: string;
  action: string;
  trend: string;
  confidence: number;
  risk_level: string;
  expected_reward_atr: number;
  expected_risk_atr: number;
  reward_risk_ratio: number | null;
  market_regime: string;
  supporting_indicators: string[];
  reasoning: string;
  alternative_scenarios: string[];
  invalidation_conditions: string[];
  disclaimer: string;
}

export interface ModelStatusEntry {
  model_name: string;
  trained: boolean;
  trained_at: string | null;
  metrics: Record<string, unknown> | null;
}

export interface ModelStatusResponse {
  symbol: string;
  interval: string;
  models: ModelStatusEntry[];
  all_trained: boolean;
}

export interface TrainModelsResponse {
  symbol: string;
  interval: string;
  dataset_size: number;
  models: { model_name: string; version: string; metrics: Record<string, unknown> }[];
}

export async function getPredictions(symbol: string, interval: string): Promise<PredictMarketResponse> {
  return httpGet<PredictMarketResponse>(`/ai/predict/${encodeURIComponent(symbol)}?interval=${interval}`);
}

export async function getRecommendation(symbol: string, interval: string): Promise<RecommendationResponse> {
  return httpGet<RecommendationResponse>(`/decision/recommend/${encodeURIComponent(symbol)}?interval=${interval}`);
}

export async function getModelStatus(symbol: string, interval: string): Promise<ModelStatusResponse> {
  return httpGet<ModelStatusResponse>(`/ai/models/status/${encodeURIComponent(symbol)}?interval=${interval}`);
}

export async function trainModels(symbol: string, interval: string): Promise<TrainModelsResponse> {
  return httpPost<TrainModelsResponse>("/ai/train", {
    symbol,
    interval,
    limit: 3000,
    horizon: 20,
    minimum_samples: 200
  });
}