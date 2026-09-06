import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PriceTicker } from "./PriceTicker";

describe("PriceTicker", () => {
  it("shows live for a symbol with a tick", () => {
    render(
      <PriceTicker
        instruments={["EUR/USD"]}
        ticks={{ "EUR/USD": { event: "price", symbol: "EUR/USD", price: "1.1000", timestamp: 0 } }}
        status="open"
      />
    );
    expect(screen.getByText("live")).toBeInTheDocument();
    expect(screen.getByText("1.1000")).toBeInTheDocument();
  });

  it("shows reconnecting for a symbol with no tick while the socket is closed", () => {
    render(<PriceTicker instruments={["GBP/USD"]} ticks={{}} status="closed" />);
    expect(screen.getByText("reconnecting")).toBeInTheDocument();
  });

  it("never renders the literal word error as a status label", () => {
    render(<PriceTicker instruments={["USD/JPY"]} ticks={{}} status="connecting" />);
    expect(screen.queryByText("error")).not.toBeInTheDocument();
  });
});