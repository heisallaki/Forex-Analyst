from app.domain.services.decision_engine import MIN_CONFIDENCE_THRESHOLD, build_recommendation

LATEST_ROW = {
    "close": 1.1,
    "atr_14": 0.001,
    "rsi_14": 50,
    "macd_histogram": 0.001,
    "adx_14": 25,
    "market_structure": "uptrend",
    "active_sessions": ["London"],
}


def _predictions(
    trend="up", trend_conf=0.9, opportunity=0.9, confidence=0.9, mae=1.0, mfe=3.0, regime="trending"
):
    return {
        "trend_classifier": {
            "predicted_trend": trend,
            "probabilities": {
                "up": trend_conf,
                "down": (1 - trend_conf) / 2,
                "flat": (1 - trend_conf) / 2,
            },
        },
        "entry_quality": {"opportunity_probability": opportunity},
        "confidence_scoring": {"target_before_stop_probability": confidence},
        "risk_prediction": {"predicted_max_adverse_excursion_atr": mae},
        "reward_prediction": {"predicted_max_favorable_excursion_atr": mfe},
        "market_regime": {"predicted_regime": regime},
    }


def test_strong_signal_recommends_long():
    result = build_recommendation("EUR/USD", "1min", LATEST_ROW, _predictions())
    assert result["action"] == "long"
    assert result["confidence"] >= MIN_CONFIDENCE_THRESHOLD


def test_flat_trend_never_recommends_a_trade():
    result = build_recommendation("EUR/USD", "1min", LATEST_ROW, _predictions(trend="flat"))
    assert result["action"] == "no_trade"


def test_low_confidence_recommends_no_trade():
    result = build_recommendation(
        "EUR/USD", "1min", LATEST_ROW, _predictions(trend_conf=0.3, opportunity=0.3, confidence=0.3)
    )
    assert result["action"] == "no_trade"


def test_low_reward_risk_ratio_recommends_no_trade():
    result = build_recommendation("EUR/USD", "1min", LATEST_ROW, _predictions(mae=3.0, mfe=1.0))
    assert result["action"] == "no_trade"


def test_missing_models_produce_no_trade_with_explanation():
    result = build_recommendation(
        "EUR/USD", "1min", LATEST_ROW, {"trend_classifier": {"error": "model not trained yet"}}
    )
    assert result["action"] == "no_trade"
    assert "not yet trained" in result["reasoning"]
