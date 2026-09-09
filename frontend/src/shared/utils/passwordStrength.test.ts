import { describe, it, expect } from "vitest";
import { evaluatePasswordStrength } from "./passwordStrength";

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