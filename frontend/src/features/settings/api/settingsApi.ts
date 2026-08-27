import { httpGet } from "@/shared/api/httpClient";

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  permissions: Record<string, boolean>;
  is_active: boolean;
}

export interface ExecutionStatus {
  execution_enabled: boolean;
  max_position_size: number;
  max_open_positions: number;
  max_daily_loss_pct: number;
  broker_configured: boolean;
}

export async function getProfile(): Promise<UserProfile> {
  return httpGet<UserProfile>("/auth/me");
}

export async function getExecutionStatus(): Promise<ExecutionStatus> {
  return httpGet<ExecutionStatus>("/execution/status");
}