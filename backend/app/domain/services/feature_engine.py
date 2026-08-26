import pandas as pd

from app.core.market_sessions import get_active_sessions
from app.domain.entities.market import Candle
from app.domain.services import indicators, market_metrics, price_action


def _candles_to_dataframe(candles: list[Candle]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": [candle.timestamp for candle in candles],
            "open": [candle.open for candle in candles],
            "high": [candle.high for candle in candles],
            "low": [candle.low for candle in candles],
            "close": [candle.close for candle in candles],
            "volume": [candle.volume or 0.0 for candle in candles],
        }
    )


def _nan_to_none(value) -> float | None:
    if value is None:
        return None
    if pd.isna(value):
        return None
    return float(value)


def compute_feature_rows(candles: list[Candle]) -> list[dict]:
    if not candles:
        return []

    df = _candles_to_dataframe(candles)

    df["sma_20"] = indicators.sma(df["close"], 20)
    df["ema_20"] = indicators.ema(df["close"], 20)
    df["vwap"] = indicators.vwap(df)
    df["atr_14"] = indicators.atr(df, 14)
    df["rsi_14"] = indicators.rsi(df["close"], 14)

    macd_line, signal_line, histogram = indicators.macd(df["close"])
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_histogram"] = histogram

    plus_di, minus_di, adx_value = indicators.adx(df, 14)
    df["plus_di_14"] = plus_di
    df["minus_di_14"] = minus_di
    df["adx_14"] = adx_value

    upper, middle, lower = indicators.bollinger_bands(df["close"], 20, 2.0)
    df["bollinger_upper"] = upper
    df["bollinger_middle"] = middle
    df["bollinger_lower"] = lower

    df["volatility"] = market_metrics.compute_volatility(df)
    df["momentum"] = market_metrics.compute_momentum(df)

    swing_high, swing_low = price_action.compute_swing_points(df)
    market_structure = price_action.compute_market_structure(df, swing_high, swing_low)
    liquidity_sweep = price_action.compute_liquidity_sweeps(df, swing_high, swing_low)
    order_block = price_action.compute_order_blocks(df, df["atr_14"])
    fair_value_gap = price_action.compute_fair_value_gaps(df)

    rows: list[dict] = []
    for i in range(len(df)):
        rows.append(
            {
                "timestamp": df["timestamp"].iloc[i],
                "open": float(df["open"].iloc[i]),
                "high": float(df["high"].iloc[i]),
                "low": float(df["low"].iloc[i]),
                "close": float(df["close"].iloc[i]),
                "sma_20": _nan_to_none(df["sma_20"].iloc[i]),
                "ema_20": _nan_to_none(df["ema_20"].iloc[i]),
                "vwap": _nan_to_none(df["vwap"].iloc[i]),
                "atr_14": _nan_to_none(df["atr_14"].iloc[i]),
                "rsi_14": _nan_to_none(df["rsi_14"].iloc[i]),
                "macd": _nan_to_none(df["macd"].iloc[i]),
                "macd_signal": _nan_to_none(df["macd_signal"].iloc[i]),
                "macd_histogram": _nan_to_none(df["macd_histogram"].iloc[i]),
                "adx_14": _nan_to_none(df["adx_14"].iloc[i]),
                "plus_di_14": _nan_to_none(df["plus_di_14"].iloc[i]),
                "minus_di_14": _nan_to_none(df["minus_di_14"].iloc[i]),
                "bollinger_upper": _nan_to_none(df["bollinger_upper"].iloc[i]),
                "bollinger_middle": _nan_to_none(df["bollinger_middle"].iloc[i]),
                "bollinger_lower": _nan_to_none(df["bollinger_lower"].iloc[i]),
                "swing_high": bool(swing_high[i]),
                "swing_low": bool(swing_low[i]),
                "market_structure": market_structure[i],
                "liquidity_sweep": liquidity_sweep[i],
                "order_block": order_block[i],
                "fair_value_gap": fair_value_gap[i],
                "volatility": _nan_to_none(df["volatility"].iloc[i]),
                "trend_strength": _nan_to_none(df["adx_14"].iloc[i]),
                "momentum": _nan_to_none(df["momentum"].iloc[i]),
                "active_sessions": get_active_sessions(df["timestamp"].iloc[i].to_pydatetime()),
            }
        )

    return rows
