import { httpGet, httpPost } from "@/shared/api/httpClient";

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  permissions: Record<string, boolean>;
  is_active: boolean;
  is_verified: boolean;
}

export interface ExecutionStatus {
  execution_enabled: boolean;
  max_position_size: number;
  max_open_positions: number;
  max_daily_loss_pct: number;
  broker_configured: boolean;
}

export interface SystemSettings {
  min_confidence_threshold: number;
  min_reward_risk_ratio: number;
  updated_at: string;
  updated_by: string | null;
}

export interface MessageResponse {
  message: string;
}

export async function getProfile(): Promise<UserProfile> {
  return httpGet<UserProfile>("/auth/me");
}

export async function getExecutionStatus(): Promise<ExecutionStatus> {
  return httpGet<ExecutionStatus>("/execution/status");
}

export async function getSystemSettings(): Promise<SystemSettings> {
  return httpGet<SystemSettings>("/admin/settings");
}

export async function updateSystemSettings(
  minConfidenceThreshold: number,
  minRewardRiskRatio: number
): Promise<SystemSettings> {
  return httpPost<SystemSettings>(
    "/admin/settings",
    { min_confidence_threshold: minConfidenceThreshold, min_reward_risk_ratio: minRewardRiskRatio },
    "PATCH"
  );
}

export async function verifyEmail(code: string): Promise<MessageResponse> {
  return httpPost<MessageResponse>("/auth/verify-email", { code });
}

export async function resendVerification(): Promise<MessageResponse> {
  return httpPost<MessageResponse>("/auth/resend-verification", {});
}

export async function requestAccountDeletion(): Promise<MessageResponse> {
  return httpPost<MessageResponse>("/auth/request-account-deletion", {});
}

export async function confirmAccountDeletion(code: string): Promise<MessageResponse> {
  return httpPost<MessageResponse>("/auth/confirm-account-deletion", { code });
}