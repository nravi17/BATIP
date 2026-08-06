from batip.providers.nse_provider import NSEProvider


def test_provider_creation():
    provider = NSEProvider()

    assert provider is not None