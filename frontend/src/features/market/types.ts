export interface MarketStatus {
  instruments: string[];
  active_sessions: string[];
}

export interface PriceTick {
  event: string;
  symbol: string;
  price: string;
  timestamp: number;
}