def is_usd_base_pair(symbol: str) -> bool:
    return symbol.upper().startswith("USD/")


def pip_size(symbol: str) -> float:
    upper_symbol = symbol.upper()
    if "JPY" in upper_symbol:
        return 0.01
    if "XAU" in upper_symbol:
        return 0.01
    return 0.0001


def compute_pnl(
    symbol: str, side: str, entry_price: float, exit_price: float, quantity: float
) -> float:
    direction_multiplier = 1 if side == "long" else -1
    raw_pnl = (exit_price - entry_price) * direction_multiplier * quantity
    if is_usd_base_pair(symbol):
        return raw_pnl / exit_price
    return raw_pnl


def compute_pips(symbol: str, side: str, entry_price: float, exit_price: float) -> float:
    direction_multiplier = 1 if side == "long" else -1
    return (exit_price - entry_price) * direction_multiplier / pip_size(symbol)


def size_quantity_for_risk(
    symbol: str, risk_amount_usd: float, stop_distance: float, reference_price: float
) -> float:
    if stop_distance <= 0:
        return 0.0
    if is_usd_base_pair(symbol):
        return (risk_amount_usd * reference_price) / stop_distance
    return risk_amount_usd / stop_distance
