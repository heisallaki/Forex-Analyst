import { BacktestRunRequest, RuleGroup } from "@/features/backtest/api/backtestApi";

export type StrategyImplementationStatus = "implemented" | "partial" | "not_implemented";

export interface StrategyPreset {
  key: string;
  strategyName: string;
  displayName: string;
  description: string;
  status: StrategyImplementationStatus;
  limitationNote?: string;
  suggestedInterval: string;
  buildRuleGroups: (params: { rsiOversold: number; rsiOverbought: number }) => {
    long: RuleGroup;
    short: RuleGroup;
  };
  buildParams: () => Pick<
    BacktestRunRequest,
    | "initial_balance"
    | "risk_per_trade_pct"
    | "spread_pips"
    | "slippage_pips"
    | "stop_loss_atr_multiple"
    | "take_profit_atr_multiple"
    | "max_holding_bars"
  >;
}

const DEFAULT_PARAMS = {
  initial_balance: 10000,
  risk_per_trade_pct: 1,
  spread_pips: 1.0,
  slippage_pips: 0.5,
  stop_loss_atr_multiple: 1.5,
  take_profit_atr_multiple: 3.0,
  max_holding_bars: 200
};

const EMPTY_RULES = { long: { match: "all", conditions: [] }, short: { match: "all", conditions: [] } };

export const STRATEGY_PRESETS: StrategyPreset[] = [
  {
    key: "trend_following",
    strategyName: "trend_following_ma_structure",
    displayName: "Trend Following — Moving Averages & Market Structure",
    description:
      "Enters in the direction of market structure when price is on the trending side of the 20-EMA and ADX confirms trend strength.",
    status: "implemented",
    suggestedInterval: "15min",
    buildRuleGroups: () => ({
      long: {
        match: "all",
        conditions: [
          { field: "close", operator: "gt", compare_field: "ema_20" },
          { field: "market_structure", operator: "eq", value: "uptrend" },
          { field: "adx_14", operator: "gt", value: 20 }
        ]
      },
      short: {
        match: "all",
        conditions: [
          { field: "close", operator: "lt", compare_field: "ema_20" },
          { field: "market_structure", operator: "eq", value: "downtrend" },
          { field: "adx_14", operator: "gt", value: 20 }
        ]
      }
    }),
    buildParams: () => DEFAULT_PARAMS
  },
  {
    key: "smc_liquidity",
    strategyName: "smart_money_liquidity",
    displayName: "Smart Money Concepts (SMC) & Liquidity",
    description:
      "Enters after a detected liquidity sweep or a bullish/bearish Fair Value Gap, using the price-action features computed in feature engineering.",
    status: "implemented",
    suggestedInterval: "15min",
    buildRuleGroups: () => ({
      long: {
        match: "any",
        conditions: [
          { field: "liquidity_sweep", operator: "eq", value: "bullish_sweep" },
          { field: "fair_value_gap", operator: "eq", value: "bullish_fvg" }
        ]
      },
      short: {
        match: "any",
        conditions: [
          { field: "liquidity_sweep", operator: "eq", value: "bearish_sweep" },
          { field: "fair_value_gap", operator: "eq", value: "bearish_fvg" }
        ]
      }
    }),
    buildParams: () => DEFAULT_PARAMS
  },
  {
    key: "range_mean_reversion",
    strategyName: "range_mean_reversion",
    displayName: "Range Trading / Mean Reversion",
    description: "Enters when RSI reaches an oversold or overbought extreme, betting on a reversion toward the mean.",
    status: "implemented",
    suggestedInterval: "1min",
    buildRuleGroups: ({ rsiOversold, rsiOverbought }) => ({
      long: { match: "all", conditions: [{ field: "rsi_14", operator: "lt", value: rsiOversold }] },
      short: { match: "all", conditions: [{ field: "rsi_14", operator: "gt", value: rsiOverbought }] }
    }),
    buildParams: () => DEFAULT_PARAMS
  },
  {
    key: "breakout",
    strategyName: "breakout_bollinger",
    displayName: "Breakout & Retest",
    description: "Enters when price closes beyond the Bollinger Band with ADX confirming momentum.",
    status: "partial",
    limitationNote:
      "Only the breakout trigger is implemented. Retest confirmation needs multi-bar state tracking the current single-bar rule engine doesn't support, so entries fire on the breakout alone.",
    suggestedInterval: "15min",
    buildRuleGroups: () => ({
      long: {
        match: "all",
        conditions: [
          { field: "close", operator: "gt", compare_field: "bollinger_upper" },
          { field: "adx_14", operator: "gt", value: 20 }
        ]
      },
      short: {
        match: "all",
        conditions: [
          { field: "close", operator: "lt", compare_field: "bollinger_lower" },
          { field: "adx_14", operator: "gt", value: 20 }
        ]
      }
    }),
    buildParams: () => DEFAULT_PARAMS
  },
  {
    key: "swing_trading",
    strategyName: "swing_trading",
    displayName: "Swing Trading",
    description:
      "The same trend/market-structure logic as Trend Following, run on a higher timeframe with wider stops and longer holds — matching how swing trading differs in practice.",
    status: "implemented",
    suggestedInterval: "1h",
    buildRuleGroups: () => ({
      long: {
        match: "all",
        conditions: [
          { field: "close", operator: "gt", compare_field: "ema_20" },
          { field: "market_structure", operator: "eq", value: "uptrend" }
        ]
      },
      short: {
        match: "all",
        conditions: [
          { field: "close", operator: "lt", compare_field: "ema_20" },
          { field: "market_structure", operator: "eq", value: "downtrend" }
        ]
      }
    }),
    buildParams: () => ({
      ...DEFAULT_PARAMS,
      stop_loss_atr_multiple: 2.5,
      take_profit_atr_multiple: 5.0,
      max_holding_bars: 500
    })
  },
  {
    key: "scalping",
    strategyName: "scalping_momentum",
    displayName: "Scalping",
    description:
      "Tight RSI + momentum entries on the 1-minute chart with very short holding periods and small stops, aiming for quick, small moves.",
    status: "implemented",
    suggestedInterval: "1min",
    buildRuleGroups: () => ({
      long: {
        match: "all",
        conditions: [
          { field: "rsi_14", operator: "lt", value: 35 },
          { field: "momentum", operator: "gt", value: 0 }
        ]
      },
      short: {
        match: "all",
        conditions: [
          { field: "rsi_14", operator: "gt", value: 65 },
          { field: "momentum", operator: "lt", value: 0 }
        ]
      }
    }),
    buildParams: () => ({
      ...DEFAULT_PARAMS,
      stop_loss_atr_multiple: 0.5,
      take_profit_atr_multiple: 1.0,
      max_holding_bars: 15
    })
  },
  {
    key: "price_action_sr",
    strategyName: "price_action_support_resistance",
    displayName: "Price Action & Support/Resistance",
    description: "Trading reactions off horizontal support/resistance zones.",
    status: "not_implemented",
    limitationNote:
      "Requires clustering historical swing points into persistent price zones and tracking price's relationship to them over time. That zone-detection feature does not exist yet — only single-bar swing-high/low flags are computed.",
    suggestedInterval: "15min",
    buildRuleGroups: () => EMPTY_RULES,
    buildParams: () => DEFAULT_PARAMS
  },
  {
    key: "news_catalyst",
    strategyName: "news_fundamental_catalyst",
    displayName: "News & Fundamental Catalyst Trading",
    description: "Trading around scheduled economic releases and news catalysts.",
    status: "not_implemented",
    limitationNote:
      "No economic calendar or news feed is integrated anywhere in this system — evaluated and explicitly deferred in the Market Data Engine module since no free provider met the reliability bar.",
    suggestedInterval: "15min",
    buildRuleGroups: () => EMPTY_RULES,
    buildParams: () => DEFAULT_PARAMS
  },
  {
    key: "fibonacci",
    strategyName: "fibonacci_retracement",
    displayName: "Fibonacci Retracement & Extension",
    description: "Trading reactions at Fibonacci retracement/extension levels.",
    status: "not_implemented",
    limitationNote:
      "No Fibonacci level calculation exists in feature engineering. Needs new logic to detect a qualifying swing pair and compute retracement levels as new per-bar features first.",
    suggestedInterval: "15min",
    buildRuleGroups: () => EMPTY_RULES,
    buildParams: () => DEFAULT_PARAMS
  },
  {
    key: "macro_correlation",
    strategyName: "macro_intermarket",
    displayName: "Macro Correlation & Intermarket Analysis",
    description: "Trading based on relationships between correlated instruments (e.g. Gold vs USD strength).",
    status: "not_implemented",
    limitationNote:
      "The backtesting engine evaluates one symbol at a time. Multi-instrument correlation analysis needs a new joint-analysis layer that doesn't exist yet.",
    suggestedInterval: "1day",
    buildRuleGroups: () => EMPTY_RULES,
    buildParams: () => DEFAULT_PARAMS
  }
];