export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  permissions: Record<string, boolean>;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AuthUser;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  role: string;
}