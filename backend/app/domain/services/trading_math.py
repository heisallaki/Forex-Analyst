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
    return (exit_price - entry_price) * direction_multiplier * quantity


def compute_pips(symbol: str, side: str, entry_price: float, exit_price: float) -> float:
    direction_multiplier = 1 if side == "long" else -1
    return (exit_price - entry_price) * direction_multiplier / pip_size(symbol)
