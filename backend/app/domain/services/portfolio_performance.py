from app.domain.entities.paper_trading import PaperTrade, Portfolio


def compute_portfolio_performance(portfolio: Portfolio, trades: list[PaperTrade]) -> dict:
    closed_trades = [
        trade for trade in trades if trade.status == "closed" and trade.pnl is not None
    ]
    open_trades = [trade for trade in trades if trade.status == "open"]

    if not closed_trades:
        return {
            "current_balance": portfolio.current_balance,
            "initial_balance": portfolio.initial_balance,
            "return_pct": 0.0,
            "total_trades": 0,
            "open_trades": len(open_trades),
            "win_rate": None,
            "profit_factor": None,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "total_pnl": 0.0,
        }

    wins = [trade for trade in closed_trades if trade.pnl > 0]
    losses = [trade for trade in closed_trades if trade.pnl <= 0]
    gross_profit = sum(trade.pnl for trade in wins)
    gross_loss = sum(trade.pnl for trade in losses)
    total_pnl = sum(trade.pnl for trade in closed_trades)

    return {
        "current_balance": portfolio.current_balance,
        "initial_balance": portfolio.initial_balance,
        "return_pct": (portfolio.current_balance - portfolio.initial_balance)
        / portfolio.initial_balance
        * 100,
        "total_trades": len(closed_trades),
        "open_trades": len(open_trades),
        "win_rate": len(wins) / len(closed_trades) * 100,
        "profit_factor": gross_profit / abs(gross_loss) if gross_loss != 0 else None,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "total_pnl": total_pnl,
    }
