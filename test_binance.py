#!/usr/bin/env python3
"""
Test script to verify Binance API integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.binance import BinanceAPI

def test_binance_api():
    print("Testing Binance API...")
    api = BinanceAPI()

    # Test 1: Get exchange info
    print("\n1. Fetching exchange info...")
    try:
        info = api.get_exchange_info()
        print(f"   Success! Found {len(info['symbols'])} symbols")
        usdt_symbols = [s['symbol'] for s in info['symbols'] if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING']
        print(f"   Active USDT pairs: {len(usdt_symbols)}")
    except Exception as e:
        print(f"   Failed: {e}")
        return False

    # Test 2: Check known crypto symbols
    print("\n2. Checking known crypto symbols...")
    known_crypto = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
    for symbol in known_crypto:
        if api.is_valid_symbol(symbol):
            print(f"   {symbol}: AVAILABLE")
        else:
            print(f"   {symbol}: NOT AVAILABLE")

    # Test 3: Check known stock tokens (from our discoveries)
    print("\n3. Checking known stock tokens...")
    known_stocks = ["TSLABUSDT", "AAPLBUSDT", "MSFTBUSDT", "NVDABUSDT", "SKHYBUSDT"]
    for symbol in known_stocks:
        if api.is_valid_symbol(symbol):
            print(f"   {symbol}: AVAILABLE")
        else:
            print(f"   {symbol}: NOT AVAILABLE")

    # Test 4: Get price for a symbol
    print("\n4. Testing price fetch for BTCUSDT...")
    try:
        price_data = api.get_symbol_price("BTCUSDT")
        if price_data:
            print(f"   BTCUSDT price: {price_data['price']} USDT")
        else:
            print("   Failed to get price data")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # Test 5: Get 24hr ticker
    print("\n5. Testing 24hr ticker for BTCUSDT...")
    try:
        ticker = api.get_24hr_ticker("BTCUSDT")
        if ticker:
            print(f"   BTCUSDT 24h change: {ticker['priceChangePercent']}%")
        else:
            print("   Failed to get ticker data")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    print("\nAll tests passed!")
    return True

if __name__ == "__main__":
    success = test_binance_api()
    sys.exit(0 if success else 1)