from unittest.mock import MagicMock

from app.domain.repositories.paper_trading_repository import PaperTradingRepository
from app.infrastructure.repositories.paper_trading_repository_impl import (
    SqlAlchemyPaperTradingRepository,
)


def test_repository_can_be_instantiated_without_error():
    fake_session = MagicMock()
    repository = SqlAlchemyPaperTradingRepository(fake_session)
    assert isinstance(repository, PaperTradingRepository)


def test_repository_implements_every_abstract_method():
    fake_session = MagicMock()
    repository = SqlAlchemyPaperTradingRepository(fake_session)
    for method_name in PaperTradingRepository.__abstractmethods__:
        assert hasattr(repository, method_name)
        assert callable(getattr(repository, method_name))
