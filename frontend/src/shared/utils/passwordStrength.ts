export type PasswordStrengthLabel = "weak" | "medium" | "strong";

export interface PasswordStrengthResult {
  score: number;
  label: PasswordStrengthLabel;
}

export function evaluatePasswordStrength(password: string): PasswordStrengthResult {
  const normalizedPassword = password ?? "";

  let score = 0;
  if (normalizedPassword.length >= 8) score += 30;
  if (normalizedPassword.length >= 12) score += 10;

  const checks = [
    /[a-z]/,
    /[A-Z]/,
    /\d/,
    /[^A-Za-z0-9]/,
  ];

  score += checks.filter((pattern) => pattern.test(normalizedPassword)).length * 15;

  let label: PasswordStrengthLabel = "weak";
  if (score >= 70) {
    label = "strong";
  } else if (score >= 40) {
    label = "medium";
  }

  return { score: Math.min(score, 100), label };
}

import { describe, it, expect } from "vitest";

describe("evaluatePasswordStrength", () => {
  it("rates a short simple password as weak", () => {
    expect(evaluatePasswordStrength("abc").label).toBe("weak");
  });

  it("rates a long mixed-case password with numbers and symbols as strong", () => {
    expect(evaluatePasswordStrength("Str0ng!Passw0rd").label).toBe("strong");
  });

  it("score increases as complexity increases", () => {
    const weak = evaluatePasswordStrength("abc").score;
    const strong = evaluatePasswordStrength("Str0ng!Passw0rd123").score;
    expect(strong).toBeGreaterThan(weak);
  });
});