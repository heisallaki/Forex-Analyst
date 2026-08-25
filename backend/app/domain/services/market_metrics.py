import numpy as np
import pandas as pd


def compute_volatility(df: pd.DataFrame, period: int = 14) -> pd.Series:
    log_returns = np.log(df["close"] / df["close"].shift(1))
    return log_returns.rolling(window=period).std()


def compute_momentum(df: pd.DataFrame, period: int = 10) -> pd.Series:
    return (df["close"] - df["close"].shift(period)) / df["close"].shift(period) * 100
