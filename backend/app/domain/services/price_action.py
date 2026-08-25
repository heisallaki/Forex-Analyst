import pandas as pd


def compute_swing_points(df: pd.DataFrame, lookback: int = 2) -> tuple[list[bool], list[bool]]:
    highs = df["high"].values
    lows = df["low"].values
    n = len(df)
    swing_high = [False] * n
    swing_low = [False] * n

    for i in range(lookback, n - lookback):
        window_high = highs[i - lookback : i + lookback + 1]
        if highs[i] == window_high.max() and (window_high == highs[i]).sum() == 1:
            swing_high[i] = True
        window_low = lows[i - lookback : i + lookback + 1]
        if lows[i] == window_low.min() and (window_low == lows[i]).sum() == 1:
            swing_low[i] = True

    return swing_high, swing_low


def compute_market_structure(
    df: pd.DataFrame, swing_high: list[bool], swing_low: list[bool]
) -> list[str]:
    n = len(df)
    structure = ["undetermined"] * n
    last_highs: list[float] = []
    last_lows: list[float] = []
    current = "undetermined"

    for i in range(n):
        if swing_high[i]:
            last_highs.append(float(df["high"].iloc[i]))
            if len(last_highs) >= 2:
                current = "uptrend" if last_highs[-1] > last_highs[-2] else "downtrend"
        if swing_low[i]:
            last_lows.append(float(df["low"].iloc[i]))
            if len(last_lows) >= 2:
                if last_lows[-1] < last_lows[-2]:
                    current = "downtrend"
                elif last_lows[-1] > last_lows[-2] and current != "downtrend":
                    current = "uptrend"
        structure[i] = current

    return structure


def compute_liquidity_sweeps(
    df: pd.DataFrame, swing_high: list[bool], swing_low: list[bool]
) -> list[str | None]:
    n = len(df)
    sweeps: list[str | None] = [None] * n
    recent_high: float | None = None
    recent_low: float | None = None

    for i in range(n):
        if i > 0:
            if swing_high[i - 1]:
                recent_high = float(df["high"].iloc[i - 1])
            if swing_low[i - 1]:
                recent_low = float(df["low"].iloc[i - 1])

        if (
            recent_high is not None
            and df["high"].iloc[i] > recent_high
            and df["close"].iloc[i] < recent_high
        ):
            sweeps[i] = "bearish_sweep"
        elif (
            recent_low is not None
            and df["low"].iloc[i] < recent_low
            and df["close"].iloc[i] > recent_low
        ):
            sweeps[i] = "bullish_sweep"

    return sweeps


def compute_order_blocks(
    df: pd.DataFrame, atr: pd.Series, threshold_multiplier: float = 1.5
) -> list[str | None]:
    n = len(df)
    blocks: list[str | None] = [None] * n

    for i in range(1, n):
        atr_value = atr.iloc[i]
        if pd.isna(atr_value):
            continue
        body = float(df["close"].iloc[i]) - float(df["open"].iloc[i])
        if (
            body > atr_value * threshold_multiplier
            and df["close"].iloc[i - 1] < df["open"].iloc[i - 1]
        ):
            blocks[i - 1] = "bullish_order_block"
        elif (
            body < -atr_value * threshold_multiplier
            and df["close"].iloc[i - 1] > df["open"].iloc[i - 1]
        ):
            blocks[i - 1] = "bearish_order_block"

    return blocks


def compute_fair_value_gaps(df: pd.DataFrame) -> list[str | None]:
    n = len(df)
    gaps: list[str | None] = [None] * n

    for i in range(1, n - 1):
        if df["low"].iloc[i + 1] > df["high"].iloc[i - 1]:
            gaps[i] = "bullish_fvg"
        elif df["high"].iloc[i + 1] < df["low"].iloc[i - 1]:
            gaps[i] = "bearish_fvg"

    return gaps
