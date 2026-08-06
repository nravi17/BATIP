from batip.config import settings
from batip.data.base_http_client import BaseHttpClient
from batip.providers.nse_parser import NSEParser
from batip.providers.base_provider import MarketDataProvider


class NSEProvider(MarketDataProvider):

    def __init__(self):
        self.client = BaseHttpClient()
        self.parser = NSEParser()

    def fetch_payload(self, symbol="BANKNIFTY"):

        return self.client.get_json(
            settings.OPTION_CHAIN_URL,
            params={"symbol": symbol},
        )

    def get_option_chain(self, symbol="BANKNIFTY"):

        payload = self.fetch_payload(symbol)

        return self.parser.parse_option_chain(payload)