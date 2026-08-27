REQUIRED_CONFIRMATION_PHRASE = "I UNDERSTAND THIS WILL PLACE A REAL TRADE WITH REAL MONEY"


def validate_risk(
    quantity: float,
    stop_loss: float | None,
    max_position_size: float,
    open_positions_count: int,
    max_open_positions: int,
    daily_loss_pct: float,
    max_daily_loss_pct: float,
) -> list[str]:
    violations: list[str] = []

    if stop_loss is None:
        violations.append("A stop_loss is required for every live order; none was provided.")

    if quantity > max_position_size:
        violations.append(
            f"Requested quantity {quantity} exceeds the maximum allowed "
            f"position size {max_position_size}."
        )

    if open_positions_count >= max_open_positions:
        violations.append(f"Maximum open positions ({max_open_positions}) already reached.")

    if daily_loss_pct <= -abs(max_daily_loss_pct):
        violations.append(
            f"Daily loss limit of {max_daily_loss_pct}% has been reached; "
            f"trading is halted for today."
        )

    return violations
