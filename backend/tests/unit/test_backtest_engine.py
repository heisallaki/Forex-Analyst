from app.domain.services.backtest_engine import (
    Condition,
    RuleGroup,
    evaluate_condition,
    evaluate_rule_group,
)


def test_evaluate_condition_less_than():
    condition = Condition(field="rsi_14", operator="lt", value=30)
    assert evaluate_condition({"rsi_14": 25}, condition) is True
    assert evaluate_condition({"rsi_14": 35}, condition) is False


def test_evaluate_condition_field_vs_field_comparison():
    condition = Condition(field="close", operator="gt", compare_field="ema_20")
    assert evaluate_condition({"close": 1.10, "ema_20": 1.05}, condition) is True
    assert evaluate_condition({"close": 1.00, "ema_20": 1.05}, condition) is False


def test_evaluate_condition_missing_field_is_false():
    condition = Condition(field="rsi_14", operator="lt", value=30)
    assert evaluate_condition({}, condition) is False


def test_rule_group_match_all_requires_every_condition():
    group = RuleGroup(
        match="all",
        conditions=[
            Condition(field="rsi_14", operator="lt", value=30),
            Condition(field="adx_14", operator="gt", value=20),
        ],
    )
    assert evaluate_rule_group({"rsi_14": 25, "adx_14": 25}, group) is True
    assert evaluate_rule_group({"rsi_14": 25, "adx_14": 10}, group) is False


def test_rule_group_match_any_requires_one_condition():
    group = RuleGroup(
        match="any",
        conditions=[
            Condition(field="rsi_14", operator="lt", value=30),
            Condition(field="adx_14", operator="gt", value=20),
        ],
    )
    assert evaluate_rule_group({"rsi_14": 90, "adx_14": 25}, group) is True
