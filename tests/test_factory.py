from batip.config import settings
from batip.providers.factory import create_market_data_provider
from batip.providers.mock_provider import MockProvider


def test_factory_creates_mock_provider(monkeypatch):
    monkeypatch.setattr(
        settings,
        "DATA_PROVIDER",
        "mock",
    )

    provider = create_market_data_provider()

    assert isinstance(provider, MockProvider)