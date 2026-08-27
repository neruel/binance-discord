#!/usr/bin/env python3
"""
Test script to verify Binance API integration and Korean search functionality
"""
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.binance import BinanceAPI

def test_binance_api():
    print("Testing Binance API & Search Service...")
    api = BinanceAPI()

    # Test 1: Get exchange info
    print("\n1. Fetching exchange info...")
    try:
        info = api.get_exchange_info()
        print(f"   Success! Found {len(info['symbols'])} symbols")
    except Exception as e:
        print(f"   Failed: {e}")
        return False

    # Test 2: Test single match search - "SK하이닉스"
    print("\n2. Searching for 'SK하이닉스'...")
    results_skhy = api.search_symbols("SK하이닉스")
    print(f"   Matched count: {len(results_skhy)}")
    if results_skhy:
        first = results_skhy[0]
        print(f"   Found: {first['korean_name']} ({first['symbol']}) - {first['market_type']}")
        if first['symbol'] != "SKHYBUSDT":
            print(f"   FAILED: expected SKHYBUSDT, got {first['symbol']}")
            return False
        print("   [OK] 'SK하이닉스' single match passed!")
    else:
        print("   FAILED: 'SK하이닉스' search returned 0 results")
        return False

    # Test 3: Test single match search - "테슬라"
    print("\n3. Searching for '테슬라'...")
    results_tsla = api.search_symbols("테슬라")
    if results_tsla and results_tsla[0]['symbol'] == "TSLABUSDT":
        print(f"   Found: {results_tsla[0]['korean_name']} ({results_tsla[0]['symbol']})")
        print("   [OK] '테슬라' search passed!")
    else:
        print("   FAILED: '테슬라' search failed")
        return False

    # Test 4: Test multi-match search - "SK"
    print("\n4. Searching for multi-match query 'SK'...")
    results_sk = api.search_symbols("SK")
    print(f"   Matched count for 'SK': {len(results_sk)}")
    for item in results_sk:
        print(f"   - {item.get('korean_name', item['display'])} ({item['symbol']})")
    if len(results_sk) >= 2:
        print(f"   [OK] Multi-match test passed! Returned {len(results_sk)} items (>= 2).")
    else:
        print(f"   WARNING: Expected >= 2 matches for 'SK', got {len(results_sk)}")

    # Test 5: Fetch live ticker for SKHYBUSDT
    print("\n5. Testing live price ticker for SKHYBUSDT...")
    ticker = api.get_24hr_ticker("SKHYBUSDT")
    if ticker and "lastPrice" in ticker:
        price = float(ticker["lastPrice"])
        change = float(ticker["priceChangePercent"])
        print(f"   SKHYBUSDT Price: ${price:,.2f} USDT | 24h Change: {change:+.2f}%")
        print("   [OK] Live ticker test passed!")
    else:
        print("   FAILED: Unable to fetch live ticker for SKHYBUSDT")
        return False

    print("\nAll Binance API & Search tests PASSED successfully!")
    return True

if __name__ == "__main__":
    success = test_binance_api()
    sys.exit(0 if success else 1)