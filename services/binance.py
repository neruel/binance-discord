import requests
import logging
from typing import Dict, List, Optional
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET

logger = logging.getLogger(__name__)

BASE_URL = "https://api.binance.com"


class BinanceAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": BINANCE_API_KEY
        })

    def get_exchange_info(self) -> Dict:
        """Get exchange information including symbols and their status."""
        endpoint = f"{BASE_URL}/api/v3/exchangeInfo"
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch exchange info: {e}")
            raise

    def get_symbol_price(self, symbol: str) -> Optional[Dict]:
        """Get the latest price for a symbol."""
        endpoint = f"{BASE_URL}/api/v3/ticker/price"
        params = {"symbol": symbol}
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None

    def get_24hr_ticker(self, symbol: str) -> Optional[Dict]:
        """Get 24hr ticker price change statistics."""
        endpoint = f"{BASE_URL}/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get 24hr ticker for {symbol}: {e}")
            return None

    def get_active_symbols(self, quote_asset: str = "USDT") -> List[str]:
        """Get list of active symbols for a given quote asset."""
        exchange_info = self.get_exchange_info()
        symbols = []
        for s in exchange_info.get("symbols", []):
            if s.get("quoteAsset") == quote_asset and s.get("status") == "TRADING":
                symbols.append(s["symbol"])
        return symbols

    def is_valid_symbol(self, symbol: str) -> bool:
        """Check if a symbol exists and is trading."""
        try:
            exchange_info = self.get_exchange_info()
            for s in exchange_info.get("symbols", []):
                if s["symbol"] == symbol and s["status"] == "TRADING":
                    return True
            return False
        except Exception:
            return False