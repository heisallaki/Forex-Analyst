import statistics

MIN_CONFIDENCE_THRESHOLD = 0.55
MIN_REWARD_RISK_RATIO = 1.2


def _classify_risk(predicted_mae_atr: float) -> str:
    if predicted_mae_atr <= 1.0:
        return "low"
    if predicted_mae_atr <= 2.0:
        return "medium"
    return "high"


def _describe_rsi(rsi: float | None) -> str:
    if rsi is None:
        return "RSI unavailable"
    if rsi >= 70:
        return f"RSI at {rsi:.1f} (overbought)"
    if rsi <= 30:
        return f"RSI at {rsi:.1f} (oversold)"
    return f"RSI at {rsi:.1f} (neutral)"


def _describe_macd(histogram: float | None) -> str:
    if histogram is None:
        return "MACD histogram unavailable"
    direction = "bullish" if histogram > 0 else "bearish" if histogram < 0 else "flat"
    return f"MACD histogram {direction} ({histogram:.5f})"


def _describe_trend_strength(adx: float | None) -> str:
    if adx is None:
        return "ADX unavailable"
    strength = "strong" if adx >= 25 else "weak"
    return f"ADX at {adx:.1f} ({strength} trend strength)"


def build_supporting_indicators(latest_row: dict) -> list[str]:
    indicators = [
        _describe_rsi(latest_row.get("rsi_14")),
        _describe_macd(latest_row.get("macd_histogram")),
        _describe_trend_strength(latest_row.get("adx_14")),
        f"Market structure: {latest_row.get('market_structure', 'undetermined')}",
    ]
    active_sessions = latest_row.get("active_sessions") or []
    if active_sessions:
        indicators.append(f"Active sessions: {', '.join(active_sessions)}")
    return indicators


def build_reasoning(
    action: str,
    predicted_trend: str,
    combined_confidence: float,
    reward_risk_ratio: float | None,
    predicted_regime: str,
    rejection_reasons: list[str],
) -> str:
    if action == "no_trade":
        reason_text = (
            "; ".join(rejection_reasons)
            if rejection_reasons
            else "signals did not meet the minimum quality bar"
        )
        return (
            f"No trade is recommended. The trend model leans {predicted_trend} with "
            f"{combined_confidence:.0%} combined confidence, but {reason_text}. "
            f"Current market regime: {predicted_regime}."
        )

    direction_word = "bullish" if action == "long" else "bearish"
    rr_text = (
        f"a reward-to-risk ratio of {reward_risk_ratio:.2f}"
        if reward_risk_ratio is not None
        else "an undetermined reward-to-risk ratio"
    )
    return (
        f"The trend model identifies a {direction_word} bias with "
        f"{combined_confidence:.0%} combined confidence across the trend, "
        f"entry quality, and confidence scoring models, offering {rr_text} "
        f"in the current {predicted_regime} regime. This meets the minimum "
        f"confidence and reward-to-risk thresholds required to surface as a "
        f"recommendation."
    )


def build_alternative_scenarios(
    trend_probabilities: dict[str, float], predicted_regime: str
) -> list[str]:
    scenarios = []
    ranked = sorted(trend_probabilities.items(), key=lambda item: item[1], reverse=True)
    for label, probability in ranked[1:]:
        scenarios.append(
            f"There is a {probability:.0%} model-estimated probability the market "
            f"instead moves {label}."
        )
    scenarios.append(
        f"If the market regime shifts away from {predicted_regime}, "
        f"this setup's follow-through probability should be reassessed "
        f"rather than assumed to hold."
    )
    return scenarios


def build_invalidation_conditions(
    action: str, entry_price: float, atr: float, predicted_mae_atr: float, pip_precision: int
) -> list[str]:
    if action == "no_trade" or not atr:
        return ["Not applicable — no position is recommended."]

    stop_distance = atr * max(predicted_mae_atr, 0.5)
    if action == "long":
        stop_price = entry_price - stop_distance
        return [
            f"Invalidated if price closes below {stop_price:.{pip_precision}f}.",
            "Invalidated if the trend model's directional bias flips to "
            "down or flat on the next evaluation.",
        ]
    stop_price = entry_price + stop_distance
    return [
        f"Invalidated if price closes above {stop_price:.{pip_precision}f}.",
        "Invalidated if the trend model's directional bias flips to "
        "up or flat on the next evaluation.",
    ]


def build_recommendation(
    symbol: str, interval: str, latest_row: dict, predictions: dict[str, dict]
) -> dict:
    trend_output = predictions.get("trend_classifier", {})
    entry_quality_output = predictions.get("entry_quality", {})
    confidence_output = predictions.get("confidence_scoring", {})
    risk_output = predictions.get("risk_prediction", {})
    reward_output = predictions.get("reward_prediction", {})
    regime_output = predictions.get("market_regime", {})

    missing = [
        name
        for name, output in [
            ("trend_classifier", trend_output),
            ("entry_quality", entry_quality_output),
            ("confidence_scoring", confidence_output),
            ("risk_prediction", risk_output),
            ("reward_prediction", reward_output),
            ("market_regime", regime_output),
        ]
        if "error" in output
    ]

    if missing:
        return {
            "action": "no_trade",
            "trend": "unknown",
            "confidence": 0.0,
            "risk_level": "unknown",
            "expected_reward_atr": 0.0,
            "expected_risk_atr": 0.0,
            "reward_risk_ratio": None,
            "market_regime": "unknown",
            "supporting_indicators": build_supporting_indicators(latest_row),
            "reasoning": (
                f"No trade is recommended because the following models are not yet "
                f"trained for {symbol}{interval}: {', '.join(missing)}. "
                "Run POST /ai/train first."
            ),
            "alternative_scenarios": [],
            "invalidation_conditions": ["Not applicable — insufficient trained models."],
        }

    predicted_trend = trend_output["predicted_trend"]
    trend_probabilities = trend_output["probabilities"]
    opportunity_probability = entry_quality_output.get("opportunity_probability", 0.0)
    target_before_stop_probability = confidence_output.get("target_before_stop_probability", 0.0)
    predicted_mae_atr = risk_output.get("predicted_max_adverse_excursion_atr", 0.0)
    predicted_mfe_atr = reward_output.get("predicted_max_favorable_excursion_atr", 0.0)
    predicted_regime = regime_output.get("predicted_regime", "unknown")

    reward_risk_ratio = predicted_mfe_atr / predicted_mae_atr if predicted_mae_atr > 0 else None
    combined_confidence = statistics.mean(
        [
            trend_probabilities.get(predicted_trend, 0.0),
            opportunity_probability,
            target_before_stop_probability,
        ]
    )

    direction = (
        "long" if predicted_trend == "up" else "short" if predicted_trend == "down" else None
    )

    action = "no_trade"
    rejection_reasons: list[str] = []

    if direction is None:
        rejection_reasons.append("the trend model shows no clear directional bias (flat)")
    elif combined_confidence < MIN_CONFIDENCE_THRESHOLD:
        rejection_reasons.append(
            f"combined confidence ({combined_confidence:.0%}) is below the "
            f"{MIN_CONFIDENCE_THRESHOLD:.0%} minimum"
        )
    elif reward_risk_ratio is not None and reward_risk_ratio < MIN_REWARD_RISK_RATIO:
        rejection_reasons.append(
            f"the expected reward-to-risk ratio ({reward_risk_ratio:.2f}) is below the "
            f"{MIN_REWARD_RISK_RATIO:.2f} minimum"
        )
    else:
        action = direction

    risk_level = _classify_risk(predicted_mae_atr)
    supporting_indicators = build_supporting_indicators(latest_row)
    reasoning = build_reasoning(
        action,
        predicted_trend,
        combined_confidence,
        reward_risk_ratio,
        predicted_regime,
        rejection_reasons,
    )
    alternative_scenarios = build_alternative_scenarios(trend_probabilities, predicted_regime)
    pip_precision = 3 if "JPY" in symbol.upper() else 5
    invalidation_conditions = build_invalidation_conditions(
        action,
        latest_row["close"],
        latest_row.get("atr_14") or 0.0,
        predicted_mae_atr,
        pip_precision,
    )

    return {
        "action": action,
        "trend": predicted_trend,
        "confidence": combined_confidence,
        "risk_level": risk_level,
        "expected_reward_atr": predicted_mfe_atr,
        "expected_risk_atr": predicted_mae_atr,
        "reward_risk_ratio": reward_risk_ratio,
        "market_regime": predicted_regime,
        "supporting_indicators": supporting_indicators,
        "reasoning": reasoning,
        "alternative_scenarios": alternative_scenarios,
        "invalidation_conditions": invalidation_conditions,
    }
