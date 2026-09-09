import { describe, it, expect } from "vitest";
import { humanizeSnakeCase } from "./formatLabel";

describe("humanizeSnakeCase", () => {
  it("replaces underscores with spaces", () => {
    expect(humanizeSnakeCase("decision_engine")).toBe("Decision Engine");
  });

  it("capitalizes only the first letter", () => {
    expect(humanizeSnakeCase("backtest")).toBe("Backtest");
  });

  it("handles an empty string", () => {
    expect(humanizeSnakeCase("")).toBe("");
  });

  it("handles multiple underscores", () => {
    expect(humanizeSnakeCase("market_regime_classifier")).toBe("Market Regime Classifier");
  });
});