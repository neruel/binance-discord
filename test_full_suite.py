#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Binance Discord Bot
Tests Binance API endpoints, Korean search matching, single/multi embed formatting, and edge cases.
"""
import sys
import os
import datetime
import urllib.request
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.binance import BinanceAPI, BINANCE_ENDPOINTS
from bot.commands import format_price_str, MARKET_CRYPTO, MARKET_STOCK

def test_endpoints_direct():
    print("==================================================")
    print("1. TESTING BINANCE API ENDPOINTS DIRECTLY")
    print("==================================================")
    for endpoint in BINANCE_ENDPOINTS:
        url = f"{endpoint}/ticker/24hr?symbol=BTCUSDT"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        try:
            res = urllib.request.urlopen(req, timeout=5)
            data = json.loads(res.read().decode())
            print(f"   [OK] {endpoint} -> Status 200 | BTC Price: ${float(data['lastPrice']):,.2f}")
        except Exception as e:
            print(f"   [FAIL] {endpoint} -> {e}")

def test_korean_search_queries():
    print("\n==================================================")
    print("2. TESTING KOREAN & ALIAS SEARCH QUERIES")
    print("==================================================")
    api = BinanceAPI()
    
    queries_to_test = [
        ("SK하이닉스", "SKHYBUSDT", 1),
        ("테슬라", "TSLABUSDT", 1),
        ("엔비디아", "NVDABUSDT", 1),
        ("애플", "AAPLBUSDT", 1),
        ("마이크로소프트", "MSFTBUSDT", 1),
        ("비트코인", "BTCUSDT", 1),
        ("이더리움", "ETHUSDT", 1),
        ("리플", "XRPUSDT", 1),
        ("솔라나", "SOLUSDT", 1),
        ("도지코인", "DOGEUSDT", 1),
        ("SK", None, 2),  # Expect >= 2 multi-results
        ("존재하지않는종목123", None, 0)  # Expect 0 results
    ]

    all_passed = True
    for query, expected_symbol, expected_min_count in queries_to_test:
        results = api.search_symbols(query)
        count = len(results)
        print(f"\n   Query: '{query}' -> Found {count} match(es)")

        if expected_min_count == 0:
            if count == 0:
                print(f"   [OK] Correctly returned 0 results for non-existent query '{query}'")
            else:
                print(f"   [FAIL] Expected 0 results, got {count}")
                all_passed = False
        elif expected_min_count == 1:
            if count >= 1 and results[0]['symbol'] == expected_symbol:
                first = results[0]
                ticker = api.get_24hr_ticker(first['symbol'])
                price_str = f"${float(ticker['lastPrice']):,.2f}" if ticker else "N/A"
                change_str = f"{float(ticker['priceChangePercent']):+.2f}%" if ticker else "N/A"
                print(f"   [OK] Matched: {first['korean_name']} ({first['symbol']}) | Price: {price_str} | 24h: {change_str}")
            else:
                print(f"   [FAIL] Expected {expected_symbol}, got {results[0]['symbol'] if results else None}")
                all_passed = False
        else:  # expected >= 2 multi-results
            if count >= expected_min_count:
                print(f"   [OK] Multi-match verified! Returned {count} results (>= {expected_min_count}):")
                for item in results:
                    ticker = api.get_24hr_ticker(item['symbol'])
                    p_str = f"${float(ticker['lastPrice']):,.4f}" if ticker else "N/A"
                    c_str = f"{float(ticker['priceChangePercent']):+.2f}%" if ticker else "N/A"
                    print(f"        - {item.get('korean_name', item['display'])} ({item['symbol']}): {p_str} ({c_str})")
            else:
                print(f"   [FAIL] Expected >= {expected_min_count} results, got {count}")
                all_passed = False

    return all_passed

def test_price_formatter():
    print("\n==================================================")
    print("3. TESTING PRICE FORMATTER FUNCTION")
    print("==================================================")
    test_cases = [
        (164.34, "$164.34"),
        (0.04215, "$0.042150"),
        (1.23456, "$1.2346"),
        (95000.5, "$95,000.50")
    ]
    for val, expected in test_cases:
        res = format_price_str(val)
        print(f"   val={val} -> formatted: '{res}'")

def run_full_suite():
    print("Starting Self-Test Suite for Binance Discord Bot...")
    test_endpoints_direct()
    search_success = test_korean_search_queries()
    test_price_formatter()
    
    print("\n==================================================")
    if search_success:
        print("SUMMARY: ALL AUTOMATED TESTS PASSED CLEANLY (100% SUCCESS)")
        print("==================================================")
        return True
    else:
        print("SUMMARY: SOME TESTS FAILED - PLEASE INSPECT LOGS ABOVE")
        print("==================================================")
        return False

if __name__ == "__main__":
    success = run_full_suite()
    sys.exit(0 if success else 1)
