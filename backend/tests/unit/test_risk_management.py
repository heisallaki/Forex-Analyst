from app.domain.services.risk_management import validate_risk


def test_validate_risk_flags_missing_stop_loss():
    violations = validate_risk(
        quantity=1000, stop_loss=None, max_position_size=10000,
        open_positions_count=0, max_open_positions=3, daily_loss_pct=0, max_daily_loss_pct=5,
    )
    assert any("stop_loss" in violation for violation in violations)


def test_validate_risk_flags_oversized_position():
    violations = validate_risk(
        quantity=20000, stop_loss=1.05, max_position_size=10000,
        open_positions_count=0, max_open_positions=3, daily_loss_pct=0, max_daily_loss_pct=5,
    )
    assert any("exceeds" in violation for violation in violations)


def test_validate_risk_flags_max_open_positions_reached():
    violations = validate_risk(
        quantity=1000, stop_loss=1.05, max_position_size=10000,
        open_positions_count=3, max_open_positions=3, daily_loss_pct=0, max_daily_loss_pct=5,
    )
    assert any("Maximum open positions" in violation for violation in violations)


def test_validate_risk_flags_daily_loss_limit_reached():
    violations = validate_risk(
        quantity=1000, stop_loss=1.05, max_position_size=10000,
        open_positions_count=0, max_open_positions=3, daily_loss_pct=-6, max_daily_loss_pct=5,
    )
    assert any("Daily loss limit" in violation for violation in violations)


def test_validate_risk_passes_with_no_violations():
    violations = validate_risk(
        quantity=1000, stop_loss=1.05, max_position_size=10000,
        open_positions_count=0, max_open_positions=3, daily_loss_pct=0, max_daily_loss_pct=5,
    )
    assert violations == []