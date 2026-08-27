import requests
import logging
import time
from typing import Dict, List, Optional

try:
    from config.settings import BINANCE_API_KEY
except ImportError:
    BINANCE_API_KEY = None

logger = logging.getLogger(__name__)

# List of Binance API endpoints (including Futures & US endpoints that bypass Render 418 WAF blocks)
BINANCE_ENDPOINTS = [
    "https://fapi.binance.com/fapi/v1",
    "https://api.binance.us/api/v3",
    "https://www.binance.com/api/v3",
    "https://api.binance.com/api/v3",
    "https://data-api.binance.vision/api/v3"
]

# Preset assets with Korean names, display tickers, search keywords, and Yahoo Finance fallbacks
PRESET_ASSETS = [
    {
        "symbol": "SKHYBUSDT",
        "display": "SKHY",
        "name": "SK Hynix",
        "korean_name": "SK하이닉스",
        "market_type": "Stock (Tokenized)",
        "yahoo_symbol": "000660.KS",
        "keywords": ["sk하이닉스", "하이닉스", "skhy", "skhybusdt", "sk"]
    },
    {
        "symbol": "TSLABUSDT",
        "display": "TSLA",
        "name": "Tesla",
        "korean_name": "테슬라",
        "market_type": "Stock (Tokenized)",
        "yahoo_symbol": "TSLA",
        "keywords": ["테슬라", "tsla", "tslabusdt"]
    },
    {
        "symbol": "AAPLBUSDT",
        "display": "AAPL",
        "name": "Apple",
        "korean_name": "애플",
        "market_type": "Stock (Tokenized)",
        "yahoo_symbol": "AAPL",
        "keywords": ["애플", "aapl", "aaplbusdt"]
    },
    {
        "symbol": "NVDABUSDT",
        "display": "NVDA",
        "name": "NVIDIA",
        "korean_name": "엔비디아",
        "market_type": "Stock (Tokenized)",
        "yahoo_symbol": "NVDA",
        "keywords": ["엔비디아", "nvda", "nvdabusdt"]
    },
    {
        "symbol": "MSFTBUSDT",
        "display": "MSFT",
        "name": "Microsoft",
        "korean_name": "마이크로소프트",
        "market_type": "Stock (Tokenized)",
        "yahoo_symbol": "MSFT",
        "keywords": ["마이크로소프트", "마소", "msft", "msftbusdt"]
    },
    {
        "symbol": "BTCUSDT",
        "display": "BTC",
        "name": "Bitcoin",
        "korean_name": "비트코인",
        "market_type": "Crypto",
        "keywords": ["비트코인", "비트", "btc", "btcusdt"]
    },
    {
        "symbol": "ETHUSDT",
        "display": "ETH",
        "name": "Ethereum",
        "korean_name": "이더리움",
        "market_type": "Crypto",
        "keywords": ["이더리움", "이더", "eth", "ethusdt"]
    },
    {
        "symbol": "XRPUSDT",
        "display": "XRP",
        "name": "XRP",
        "korean_name": "리플",
        "market_type": "Crypto",
        "keywords": ["리플", "xrp", "xrpusdt"]
    },
    {
        "symbol": "SOLUSDT",
        "display": "SOL",
        "name": "Solana",
        "korean_name": "솔라나",
        "market_type": "Crypto",
        "keywords": ["솔라나", "sol", "solusdt"]
    },
    {
        "symbol": "DOGEUSDT",
        "display": "DOGE",
        "name": "Dogecoin",
        "korean_name": "도지코인",
        "market_type": "Crypto",
        "keywords": ["도지코인", "도지", "doge", "dogeusdt"]
    },
    {
        "symbol": "BNBUSDT",
        "display": "BNB",
        "name": "BNB",
        "korean_name": "바이낸스코인",
        "market_type": "Crypto",
        "keywords": ["바이낸스코인", "bnb", "bnbusdt"]
    }
]


class BinanceAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9"
        })
        if BINANCE_API_KEY:
            self.session.headers.update({
                "X-MBX-APIKEY": BINANCE_API_KEY
            })
        self._exchange_info_cache = None
        self._cache_time = 0
        self._cache_ttl = 300  # 5 minutes

    def _fetch_yahoo_finance(self, yahoo_symbol: str) -> Optional[Dict]:
        """Fetch stock price details from Yahoo Finance API (resilient against Cloud 418 bans)."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
        try:
            res = self.session.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                result = data.get("chart", {}).get("result", [])
                if result:
                    meta = result[0].get("meta", {})
                    price = float(meta.get("regularMarketPrice", 0))
                    prev_close = float(meta.get("previousClose", price))
                    high = float(meta.get("regularMarketDayHigh", price))
                    low = float(meta.get("regularMarketDayLow", price))
                    volume = float(meta.get("regularMarketVolume", 0))
                    currency = meta.get("currency", "USD")

                    # If price is in KRW (like SK Hynix 000660.KS), calculate exchange rate or convert to approx USDT
                    # 1 USDT ≈ 1350 KRW
                    if currency == "KRW" and price > 5000:
                        price = price / 1350.0
                        prev_close = prev_close / 1350.0
                        high = high / 1350.0
                        low = low / 1350.0

                    change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0

                    return {
                        "symbol": yahoo_symbol,
                        "lastPrice": str(price),
                        "priceChangePercent": f"{change_pct:.2f}",
                        "highPrice": str(high),
                        "lowPrice": str(low),
                        "volume": str(volume)
                    }
        except Exception as e:
            logger.warning(f"Yahoo Finance fetch failed for {yahoo_symbol}: {e}")
        return None

    def _make_binance_request(self, path: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP GET request across multiple Binance mirror endpoints."""
        for base_endpoint in BINANCE_ENDPOINTS:
            url = f"{base_endpoint}{path}"
            try:
                res = self.session.get(url, params=params, timeout=4)
                if res.status_code == 200:
                    data = res.json()
                    # If endpoint returned array (like /ticker/24hr without symbol), filter or return
                    if isinstance(data, list) and params and "symbol" in params:
                        target = params["symbol"]
                        match = next((item for item in data if item.get("symbol") == target), None)
                        if match:
                            return match
                    elif isinstance(data, dict):
                        return data
            except Exception as e:
                logger.debug(f"Endpoint {url} exception: {e}")
        return None

    def get_exchange_info(self, force_refresh: bool = False) -> Dict:
        """Get exchange information with in-memory caching."""
        now = time.time()
        if not force_refresh and self._exchange_info_cache and (now - self._cache_time < self._cache_ttl):
            return self._exchange_info_cache

        data = self._make_binance_request("/exchangeInfo")
        if data:
            self._exchange_info_cache = data
            self._cache_time = now
            return data

        if self._exchange_info_cache:
            return self._exchange_info_cache
        return {"symbols": []}

    def get_symbol_price(self, symbol: str) -> Optional[Dict]:
        """Get the latest price for a symbol."""
        # First try Binance endpoints
        data = self._make_binance_request("/ticker/price", {"symbol": symbol})
        if data and "price" in data:
            return data

        # Check preset assets for Yahoo Finance fallback
        for preset in PRESET_ASSETS:
            if preset["symbol"] == symbol and "yahoo_symbol" in preset:
                yf_data = self._fetch_yahoo_finance(preset["yahoo_symbol"])
                if yf_data:
                    return {"symbol": symbol, "price": yf_data["lastPrice"]}

        return None

    def get_24hr_ticker(self, symbol: str) -> Optional[Dict]:
        """Get 24hr ticker with multi-provider fallback (Binance Futures -> Yahoo Finance -> Binance US)."""
        # 1. Try Binance endpoints
        data = self._make_binance_request("/ticker/24hr", {"symbol": symbol})
        if data and "lastPrice" in data:
            return data

        # 2. Check preset assets for Yahoo Finance fallback (for stocks / cryptos)
        for preset in PRESET_ASSETS:
            if preset["symbol"] == symbol and "yahoo_symbol" in preset:
                yf_data = self._fetch_yahoo_finance(preset["yahoo_symbol"])
                if yf_data:
                    yf_data["symbol"] = symbol
                    return yf_data

        # 3. Fallback to simple price lookup
        price_data = self.get_symbol_price(symbol)
        if price_data and "price" in price_data:
            price = price_data["price"]
            return {
                "symbol": symbol,
                "lastPrice": price,
                "priceChangePercent": "0.00",
                "highPrice": price,
                "lowPrice": price,
                "volume": "0"
            }
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
        for preset in PRESET_ASSETS:
            if preset["symbol"] == symbol:
                return True
        try:
            exchange_info = self.get_exchange_info()
            for s in exchange_info.get("symbols", []):
                if s["symbol"] == symbol and s["status"] == "TRADING":
                    return True
            return False
        except Exception:
            return False

    def search_symbols(self, query: str) -> List[Dict]:
        """
        Search for assets by query (supports Korean names, English names, tickers, symbols).
        Returns a list of asset dicts. If 1 match -> [asset], if multiple -> [asset1, asset2, ...].
        """
        q = query.strip().lower()
        if not q:
            return []

        matched_assets = []
        seen_symbols = set()

        # Step 1: Check preset assets (exact keyword or substring match)
        for preset in PRESET_ASSETS:
            symbol = preset["symbol"]
            exact_match = any(q == kw for kw in preset["keywords"])
            partial_match = any(q in kw for kw in preset["keywords"])

            if exact_match or partial_match:
                if symbol not in seen_symbols:
                    matched_assets.append({
                        "symbol": symbol,
                        "display": preset["display"],
                        "name": preset["name"],
                        "korean_name": preset["korean_name"],
                        "market_type": preset["market_type"],
                        "priority": 1 if exact_match else 2
                    })
                    seen_symbols.add(symbol)

        # Step 2: Dynamic search in active exchangeInfo symbols
        try:
            info = self.get_exchange_info()
            u_q = q.upper()
            for s in info.get("symbols", []):
                if s.get("status") != "TRADING":
                    continue
                sym = s.get("symbol", "")
                base = s.get("baseAsset", "")
                quote = s.get("quoteAsset", "")

                if quote not in ("USDT", "BUSDT", "BUSD"):
                    continue

                if sym in seen_symbols:
                    continue

                is_exact = (u_q == sym or u_q == base)
                is_partial = (u_q in sym or u_q in base)

                if is_exact or is_partial:
                    matched_assets.append({
                        "symbol": sym,
                        "display": base,
                        "name": base,
                        "korean_name": base,
                        "market_type": "Stock (Tokenized)" if "BUSDT" in sym and len(base) > 3 else "Crypto",
                        "priority": 3 if is_exact else 4
                    })
                    seen_symbols.add(sym)
        except Exception as e:
            logger.warning(f"Error during dynamic exchange search: {e}")

        # Sort by priority score (lowest priority number first)
        matched_assets.sort(key=lambda x: x["priority"])

        # Clean priority key before returning
        for item in matched_assets:
            item.pop("priority", None)

        return matched_assets[:10]