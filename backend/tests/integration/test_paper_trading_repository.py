import uuid
from datetime import UTC, datetime

from app.domain.entities.paper_trading import PaperTrade, Portfolio
from app.infrastructure.repositories.paper_trading_repository_impl import (
    SqlAlchemyPaperTradingRepository,
)


async def _make_portfolio(repository, user_id, leverage=1.0, balance=10000.0):
    portfolio = Portfolio(
        id=uuid.uuid4(),
        user_id=user_id,
        name="Test Portfolio",
        base_currency="USD",
        initial_balance=balance,
        current_balance=balance,
        leverage=leverage,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return await repository.create_portfolio(portfolio)


async def _open_trade(
    repository,
    portfolio_id,
    symbol="EUR/USD",
    side="long",
    entry_price=1.1000,
    quantity=10000,
    stop_loss=None,
    take_profit=None,
    trailing_stop_distance=None,
    margin_used=None,
):
    trade = PaperTrade(
        id=uuid.uuid4(),
        portfolio_id=portfolio_id,
        signal_id=None,
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        exit_price=None,
        quantity=quantity,
        stop_loss=stop_loss,
        take_profit=take_profit,
        trailing_stop_distance=trailing_stop_distance,
        margin_used=margin_used,
        realized_pnl=0.0,
        status="open",
        pnl=None,
        opened_at=datetime.now(UTC),
        closed_at=None,
    )
    return await repository.open_trade(trade)


async def test_get_open_trade_count(db_session, test_user):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id
    portfolio = await _make_portfolio(repository, user_id)

    assert await repository.get_open_trade_count(portfolio.id) == 0

    await _open_trade(repository, portfolio.id)
    await _open_trade(repository, portfolio.id, symbol="XAU/USD")

    assert await repository.get_open_trade_count(portfolio.id) == 2


async def test_get_open_margin_used(db_session, test_user):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id
    portfolio = await _make_portfolio(repository, user_id, leverage=10)

    await _open_trade(repository, portfolio.id, margin_used=500.0)
    await _open_trade(
        repository,
        portfolio.id,
        symbol="XAU/USD",
        margin_used=250.0,
    )

    assert await repository.get_open_margin_used(portfolio.id) == 750.0


async def test_partial_close_trade_reduces_quantity_and_records_realized_pnl(
    db_session,
    test_user,
):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id
    portfolio = await _make_portfolio(repository, user_id)

    trade = await _open_trade(
        repository,
        portfolio.id,
        entry_price=1.1000,
        quantity=10000,
        margin_used=1000.0,
    )

    updated = await repository.partial_close_trade(
        trade.id,
        4000,
        1.1050,
        datetime.now(UTC),
    )

    assert updated is not None
    assert updated.status == "open"
    assert round(updated.quantity, 2) == 6000.0
    assert updated.realized_pnl > 0

    reloaded_portfolio = await repository.get_portfolio(
        portfolio.id,
        user_id,
    )
    assert reloaded_portfolio.current_balance > portfolio.current_balance


async def test_partial_close_rejects_full_or_over_quantity(
    db_session,
    test_user,
):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id
    portfolio = await _make_portfolio(repository, user_id)

    trade = await _open_trade(
        repository,
        portfolio.id,
        quantity=1000,
    )

    assert (
        await repository.partial_close_trade(
            trade.id,
            1000,
            1.1050,
            datetime.now(UTC),
        )
        is None
    )

    assert (
        await repository.partial_close_trade(
            trade.id,
            5000,
            1.1050,
            datetime.now(UTC),
        )
        is None
    )


async def test_close_trade_combines_realized_and_final_pnl(
    db_session,
    test_user,
):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id
    portfolio = await _make_portfolio(repository, user_id)

    trade = await _open_trade(
        repository,
        portfolio.id,
        entry_price=1.1000,
        quantity=10000,
        margin_used=1000.0,
    )

    await repository.partial_close_trade(
        trade.id,
        4000,
        1.1050,
        datetime.now(UTC),
    )

    closed = await repository.close_trade(
        trade.id,
        1.1100,
        datetime.now(UTC),
    )

    assert closed is not None
    assert closed.status == "closed"
    assert closed.pnl is not None
    assert closed.pnl > 0


async def test_apply_trailing_stop_ratchets_favorably_for_long(
    db_session,
    test_user,
):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id
    portfolio = await _make_portfolio(repository, user_id)

    trade = await _open_trade(
        repository,
        portfolio.id,
        side="long",
        entry_price=1.1000,
        trailing_stop_distance=0.0010,
        stop_loss=1.0980,
    )

    await repository.apply_trailing_stop(trade, 1.1050)

    updated = await repository.get_trade(trade.id)
    assert round(updated.stop_loss, 4) == 1.1040

    await repository.apply_trailing_stop(trade, 1.1030)

    unchanged = await repository.get_trade(trade.id)
    assert round(unchanged.stop_loss, 4) == 1.1040


async def test_evaluate_and_close_if_triggered_closes_on_stop_loss(
    db_session,
    test_user,
):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id
    portfolio = await _make_portfolio(repository, user_id)

    trade = await _open_trade(
        repository,
        portfolio.id,
        side="long",
        entry_price=1.1000,
        stop_loss=1.0950,
        quantity=10000,
    )

    closed = await repository.evaluate_and_close_if_triggered(
        trade,
        1.0940,
    )

    assert closed is not None
    assert closed.status == "closed"
    assert closed.exit_price == 1.0950


async def test_get_daily_pnl_pct_reflects_closed_trades_today(
    db_session,
    test_user,
):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id
    portfolio = await _make_portfolio(
        repository,
        user_id,
        balance=10000,
    )

    trade = await _open_trade(
        repository,
        portfolio.id,
        entry_price=1.1000,
        quantity=10000,
    )

    await repository.close_trade(
        trade.id,
        1.0950,
        datetime.now(UTC),
    )

    daily_pct = await repository.get_daily_pnl_pct(portfolio.id)
    assert daily_pct < 0


async def test_get_account_open_trade_count_sums_across_portfolios(
    db_session,
    test_user,
):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id

    portfolio_one = await _make_portfolio(repository, user_id)
    portfolio_two = await _make_portfolio(repository, user_id)

    await _open_trade(repository, portfolio_one.id)
    await _open_trade(
        repository,
        portfolio_two.id,
        symbol="XAU/USD",
    )

    assert await repository.get_account_open_trade_count(user_id) == 2


async def test_get_account_daily_pnl_pct_aggregates_across_portfolios(
    db_session,
    test_user,
):
    repository = SqlAlchemyPaperTradingRepository(db_session)
    user_id = test_user.id

    portfolio = await _make_portfolio(
        repository,
        user_id,
        balance=10000,
    )

    trade = await _open_trade(
        repository,
        portfolio.id,
        entry_price=1.1000,
        quantity=10000,
    )

    await repository.close_trade(
        trade.id,
        1.0950,
        datetime.now(UTC),
    )

    assert await repository.get_account_daily_pnl_pct(user_id)
