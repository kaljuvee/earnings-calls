#!/usr/bin/env python3
"""Test Finnhub API endpoints to see what's available"""

import requests
import json

API_KEY = "d4a8ev9r01qnehvtefd0d4a8ev9r01qnehvtefdg"
BASE_URL = "https://finnhub.io/api/v1"

print("=" * 70)
print("TESTING FINNHUB API ENDPOINTS")
print("=" * 70)

endpoints = [
    ("Company Profile", f"{BASE_URL}/stock/profile2?symbol=AAPL&token={API_KEY}"),
    ("Quote", f"{BASE_URL}/quote?symbol=AAPL&token={API_KEY}"),
    ("Earnings Calendar", f"{BASE_URL}/calendar/earnings?from=2024-01-01&to=2024-12-31&symbol=AAPL&token={API_KEY}"),
    ("Earnings", f"{BASE_URL}/stock/earnings?symbol=AAPL&token={API_KEY}"),
    ("Financials", f"{BASE_URL}/stock/financials-reported?symbol=AAPL&token={API_KEY}"),
    ("News", f"{BASE_URL}/company-news?symbol=AAPL&from=2024-01-01&to=2024-12-31&token={API_KEY}"),
    ("Transcripts List", f"{BASE_URL}/stock/transcripts?symbol=AAPL&token={API_KEY}"),
    ("Earnings Call Transcripts", f"{BASE_URL}/stock/earnings-call-transcripts?symbol=AAPL&token={API_KEY}"),
]

for name, url in endpoints:
    print(f"\n{name}:")
    print(f"URL: {url[:80]}...")
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code} OK")
            
            if isinstance(data, dict):
                print(f"  Keys: {list(data.keys())[:5]}")
                if data:
                    print(f"  Sample: {str(data)[:200]}...")
            elif isinstance(data, list):
                print(f"  Items: {len(data)}")
                if data:
                    print(f"  Sample: {str(data[0])[:200]}...")
            else:
                print(f"  Data: {str(data)[:200]}...")
        else:
            print(f"✗ Status: {response.status_code}")
            print(f"  Error: {response.text[:200]}")
    
    except Exception as e:
        print(f"✗ Exception: {e}")

print("\n" + "=" * 70)
