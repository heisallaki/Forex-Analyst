export type PasswordStrengthLabel = "weak" | "fair" | "good" | "strong";

export interface PasswordStrengthResult {
  score: number;
  label: PasswordStrengthLabel;
  color: "error" | "warning" | "info" | "success";
}

export function evaluatePasswordStrength(password: string): PasswordStrengthResult {
  let score = 0;
  if (password.length >= 8) score += 1;
  if (password.length >= 12) score += 1;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  if (score <= 1) return { score, label: "weak", color: "error" };
  if (score <= 2) return { score, label: "fair", color: "warning" };
  if (score <= 3) return { score, label: "good", color: "info" };
  return { score, label: "strong", color: "success" };
}