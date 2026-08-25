import numpy as np
import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def vwap(df: pd.DataFrame) -> pd.Series:
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cumulative_pv = (typical_price * df["volume"]).cumsum()
    cumulative_volume = df["volume"].cumsum()
    result = cumulative_pv / cumulative_volume
    fallback = typical_price.expanding().mean()
    return result.where(cumulative_volume > 0, fallback)


def true_range(df: pd.DataFrame) -> pd.Series:
    previous_close = df["close"].shift(1)
    ranges = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - previous_close).abs(),
            (df["low"] - previous_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def atr(df: pd.DataFrame, period: int) -> pd.Series:
    tr = true_range(df)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    average_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    average_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    relative_strength = average_gain / average_loss
    return 100 - (100 / (1 + relative_strength))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    fast_ema = ema(series, fast)
    slow_ema = ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def adx(df: pd.DataFrame, period: int):
    up_move = df["high"].diff()
    down_move = -df["low"].diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    tr = true_range(df)
    smoothed_tr = tr.ewm(alpha=1 / period, adjust=False).mean()
    smoothed_plus_dm = pd.Series(plus_dm, index=df.index).ewm(alpha=1 / period, adjust=False).mean()
    smoothed_minus_dm = (
        pd.Series(minus_dm, index=df.index).ewm(alpha=1 / period, adjust=False).mean()
    )
    plus_di = 100 * (smoothed_plus_dm / smoothed_tr)
    minus_di = 100 * (smoothed_minus_dm / smoothed_tr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx_value = dx.ewm(alpha=1 / period, adjust=False).mean()
    return plus_di, minus_di, adx_value


def bollinger_bands(series: pd.Series, period: int, std_dev: float):
    middle = sma(series, period)
    std = series.rolling(window=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower
