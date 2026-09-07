declare const describe: (name: string, fn: () => void) => void;
declare const it: (name: string, fn: () => void) => void;
declare const expect: (actual: unknown) => {
  toBe(expected: unknown): void;
};

export function humanizeSnakeCase(value: string): string {
  if (!value) return "";

  return value
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

// tests

describe("humanizeSnakeCase", () => {
  it("replaces underscores with spaces", () => {
    expect(humanizeSnakeCase("decision_engine")).toBe("Decision engine");
  });

  it("capitalizes only the first letter", () => {
    expect(humanizeSnakeCase("backtest")).toBe("Backtest");
  });

  it("handles an empty string", () => {
    expect(humanizeSnakeCase("")).toBe("");
  });

  it("handles multiple underscores", () => {
    expect(humanizeSnakeCase("market_regime_classifier")).toBe("Market regime classifier");
  });
});