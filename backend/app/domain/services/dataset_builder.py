import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ML_FEATURE_COLUMNS = [
    "rsi_14",
    "macd",
    "macd_signal",
    "macd_histogram",
    "adx_14",
    "plus_di_14",
    "minus_di_14",
    "volatility",
    "momentum",
    "bollinger_bandwidth",
    "close_to_ema_atr",
    "close_to_vwap_atr",
    "swing_high_flag",
    "swing_low_flag",
]

REGIME_FEATURE_COLUMNS = ["adx_14", "volatility", "bollinger_bandwidth"]


def row_to_ml_features(row: dict) -> dict | None:
    atr = row.get("atr_14")
    if atr is None or atr <= 0:
        return None
    ema = row.get("ema_20")
    vwap = row.get("vwap")
    upper = row.get("bollinger_upper")
    lower = row.get("bollinger_lower")
    middle = row.get("bollinger_middle")
    if None in (ema, vwap, upper, lower, middle):
        return None

    return {
        "rsi_14": row.get("rsi_14"),
        "macd": row.get("macd"),
        "macd_signal": row.get("macd_signal"),
        "macd_histogram": row.get("macd_histogram"),
        "adx_14": row.get("adx_14"),
        "plus_di_14": row.get("plus_di_14"),
        "minus_di_14": row.get("minus_di_14"),
        "volatility": row.get("volatility"),
        "momentum": row.get("momentum"),
        "bollinger_bandwidth": (upper - lower) / middle if middle else None,
        "close_to_ema_atr": (row["close"] - ema) / atr,
        "close_to_vwap_atr": (row["close"] - vwap) / atr,
        "swing_high_flag": 1 if row.get("swing_high") else 0,
        "swing_low_flag": 1 if row.get("swing_low") else 0,
    }


def build_training_dataset(
    feature_rows: list[dict],
    horizon: int = 20,
    trend_threshold: float = 0.0006,
    stop_atr_multiple: float = 1.0,
    target_atr_multiple: float = 2.0,
) -> pd.DataFrame:
    records: list[dict] = []

    for i in range(len(feature_rows) - horizon - 1):
        row = feature_rows[i]
        ml_features = row_to_ml_features(row)
        if ml_features is None or any(value is None for value in ml_features.values()):
            continue

        atr = row["atr_14"]
        entry_price = row["close"]
        future_window = feature_rows[i + 1 : i + 1 + horizon]

        future_close = future_window[-1]["close"]
        future_return = (future_close - entry_price) / entry_price
        if future_return > trend_threshold:
            trend_label = "up"
        elif future_return < -trend_threshold:
            trend_label = "down"
        else:
            trend_label = "flat"

        stop_price = entry_price - stop_atr_multiple * atr
        target_price = entry_price + target_atr_multiple * atr
        outcome = "neither"
        max_favorable = 0.0
        max_adverse = 0.0
        for bar in future_window:
            max_favorable = max(max_favorable, (bar["high"] - entry_price) / atr)
            max_adverse = max(max_adverse, (entry_price - bar["low"]) / atr)
            if bar["low"] <= stop_price:
                outcome = "stop"
                break
            if bar["high"] >= target_price:
                outcome = "target"
                break

        opportunity_label = 1 if max(max_favorable, max_adverse) >= target_atr_multiple else 0
        confidence_label = 1 if outcome == "target" else 0

        record = dict(ml_features)
        record["trend_label"] = trend_label
        record["mfe_atr"] = max_favorable
        record["mae_atr"] = max_adverse
        record["opportunity_label"] = opportunity_label
        record["confidence_label"] = confidence_label
        records.append(record)

    return pd.DataFrame.from_records(records)


def label_market_regimes(dataset: pd.DataFrame) -> pd.Series:
    regime_data = dataset[REGIME_FEATURE_COLUMNS].dropna()
    if len(regime_data) < 30:
        return pd.Series(index=dataset.index, dtype=object)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(regime_data)
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    cluster_labels = kmeans.fit_predict(scaled)

    cluster_frame = regime_data.copy()
    cluster_frame["cluster"] = cluster_labels
    cluster_means = cluster_frame.groupby("cluster").mean()

    trending_cluster = cluster_means["adx_14"].idxmax()
    remaining = cluster_means.drop(index=trending_cluster)
    volatile_cluster = remaining["volatility"].idxmax()
    ranging_cluster = remaining.drop(index=volatile_cluster).index[0]

    label_map = {
        trending_cluster: "trending",
        volatile_cluster: "volatile",
        ranging_cluster: "ranging",
    }
    named_labels = pd.Series(cluster_labels, index=regime_data.index).map(label_map)
    return named_labels.reindex(dataset.index)
