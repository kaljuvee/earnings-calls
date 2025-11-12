#!/usr/bin/env python3
"""
Test script for transcript download functionality
"""

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from utils.finnhub_client import FinnhubClient

def test_finnhub():
    """Test Finnhub client"""
    print('\n' + '=' * 70)
    print('TESTING FINNHUB CLIENT')
    print('=' * 70)
    
    try:
        client = FinnhubClient()
        api_key = os.getenv("FINNHUB_API_KEY")
        print(f'✓ Client initialized')
        print(f'  API Key: {api_key[:20]}...' if api_key else '  API Key: None')
        print()
        
        # Test companies
        test_companies = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        
        for ticker in test_companies:
            print(f'Testing {ticker}...')
            transcripts = client.get_transcripts_list(ticker)
            
            if transcripts:
                print(f'  ✓ Found {len(transcripts)} transcripts')
                if len(transcripts) > 0 and isinstance(transcripts, list):
                    print(f'    Latest: {transcripts[0]}')
            else:
                print(f'  ✗ No transcripts found or access denied')
            print()
        
        return True
        
    except Exception as e:
        print(f'✗ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_api_ninjas():
    """Test API Ninjas client"""
    print('\n' + '=' * 70)
    print('TESTING API NINJAS CLIENT')
    print('=' * 70)
    
    try:
        from utils.api_ninjas_client import APINinjasClient
        
        api_key = os.getenv("API_NINJAS_KEY")
        
        if not api_key or 'placeholder' in api_key.lower():
            print('⚠️  API Ninjas API key not configured')
            print('   Get your free API key at: https://api-ninjas.com/register')
            print('   Free tier covers S&P 100 companies')
            return False
        
        client = APINinjasClient()
        print(f'✓ Client initialized')
        print(f'  API Key: {api_key[:20]}...')
        print()
        
        # Test 1: List available companies
        print('Test 1: Listing available companies...')
        companies = client.list_available_companies()
        if companies:
            print(f'  ✓ Found {len(companies)} companies')
            if len(companies) > 0:
                print(f'    Sample: {companies[0]}')
        else:
            print(f'  ✗ No companies found')
        print()
        
        # Test 2: Search for specific transcripts
        test_companies = ['AAPL', 'MSFT', 'GOOGL']
        
        for ticker in test_companies:
            print(f'Test: Searching transcripts for {ticker}...')
            transcripts = client.search_transcripts(ticker)
            
            if transcripts:
                print(f'  ✓ Found {len(transcripts)} transcripts')
                if len(transcripts) > 0:
                    latest = transcripts[0]
                    print(f'    Latest: Q{latest.get("quarter")} {latest.get("year")}')
            else:
                print(f'  ✗ No transcripts found')
            print()
        
        return True
        
    except Exception as e:
        print(f'✗ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print('\n' + '=' * 70)
    print('EARNINGS CALL TRANSCRIPT DOWNLOAD - TEST SUITE')
    print('=' * 70)
    
    results = {
        'finnhub': test_finnhub(),
        'api_ninjas': test_api_ninjas()
    }
    
    print('\n' + '=' * 70)
    print('TEST SUMMARY')
    print('=' * 70)
    print(f'Finnhub:    {"✓ PASS" if results["finnhub"] else "✗ FAIL"}')
    print(f'API Ninjas: {"✓ PASS" if results["api_ninjas"] else "✗ FAIL (needs API key)"}')
    print('=' * 70)
    print()
    
    if not results['api_ninjas']:
        print('💡 TIP: Sign up for a free API Ninjas account to test S&P 100 companies')
        print('   URL: https://api-ninjas.com/register')
        print()

if __name__ == '__main__':
    main()
