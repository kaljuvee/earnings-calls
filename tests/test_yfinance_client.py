"""
Test Yahoo Finance Client
Simple functional tests for Yahoo Finance integration
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.yfinance_client import YFinanceClient

def test_yfinance_client():
    """Test Yahoo Finance client functionality"""
    
    results = {
        "test_name": "Yahoo Finance Client Test",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    client = YFinanceClient()
    test_ticker = "AAPL"
    
    # Test 1: Get company info
    print(f"Test 1: Getting company info for {test_ticker}...")
    try:
        info = client.get_company_info(test_ticker)
        
        if info:
            results["tests"].append({
                "name": "Get Company Info",
                "status": "PASSED",
                "message": f"Retrieved info for {info.get('longName', test_ticker)}",
                "data": {
                    "company": info.get('longName'),
                    "sector": info.get('sector'),
                    "market_cap": info.get('marketCap')
                }
            })
        else:
            results["tests"].append({
                "name": "Get Company Info",
                "status": "FAILED",
                "message": "No company info returned"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Get Company Info",
            "status": "ERROR",
            "message": str(e)
        })
    
    # Test 2: Get analyst estimates
    print(f"Test 2: Getting analyst estimates for {test_ticker}...")
    try:
        estimates = client.get_analyst_estimates(test_ticker)
        
        if estimates:
            results["tests"].append({
                "name": "Get Analyst Estimates",
                "status": "PASSED",
                "message": "Retrieved analyst estimates",
                "data": {
                    "has_earnings_estimate": estimates.get('earnings_estimate') is not None,
                    "has_revenue_estimate": estimates.get('revenue_estimate') is not None
                }
            })
        else:
            results["tests"].append({
                "name": "Get Analyst Estimates",
                "status": "WARNING",
                "message": "No analyst estimates available"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Get Analyst Estimates",
            "status": "ERROR",
            "message": str(e)
        })
    
    # Test 3: Get analyst recommendations
    print(f"Test 3: Getting analyst recommendations for {test_ticker}...")
    try:
        recommendations = client.get_analyst_recommendations(test_ticker)
        
        if recommendations is not None and not recommendations.empty:
            results["tests"].append({
                "name": "Get Analyst Recommendations",
                "status": "PASSED",
                "message": f"Retrieved {len(recommendations)} recommendations",
                "data": {
                    "count": len(recommendations),
                    "most_recent": str(recommendations.index[0]) if len(recommendations) > 0 else None
                }
            })
        else:
            results["tests"].append({
                "name": "Get Analyst Recommendations",
                "status": "WARNING",
                "message": "No recommendations available"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Get Analyst Recommendations",
            "status": "ERROR",
            "message": str(e)
        })
    
    # Test 4: Get price data
    print(f"Test 4: Getting price data for {test_ticker}...")
    try:
        price_data = client.get_price_data(test_ticker, period="1mo")
        
        if price_data is not None and not price_data.empty:
            results["tests"].append({
                "name": "Get Price Data",
                "status": "PASSED",
                "message": f"Retrieved {len(price_data)} days of price data",
                "data": {
                    "days": len(price_data),
                    "latest_close": float(price_data['Close'].iloc[-1]),
                    "high": float(price_data['High'].max()),
                    "low": float(price_data['Low'].min())
                }
            })
        else:
            results["tests"].append({
                "name": "Get Price Data",
                "status": "FAILED",
                "message": "No price data returned"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Get Price Data",
            "status": "ERROR",
            "message": str(e)
        })
    
    # Test 5: Compare estimates vs actual
    print(f"Test 5: Comparing estimates vs actual for {test_ticker}...")
    try:
        comparison = client.compare_estimates_vs_actual(test_ticker)
        
        if comparison:
            results["tests"].append({
                "name": "Compare Estimates vs Actual",
                "status": "PASSED",
                "message": "Retrieved earnings comparison data",
                "data": {
                    "has_data": len(comparison.get('eps_surprise_percent', [])) > 0,
                    "quarters": len(comparison.get('eps_surprise_percent', []))
                }
            })
        else:
            results["tests"].append({
                "name": "Compare Estimates vs Actual",
                "status": "WARNING",
                "message": "No comparison data available"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Compare Estimates vs Actual",
            "status": "ERROR",
            "message": str(e)
        })
    
    return results

def main():
    """Run tests and save results"""
    
    print("=" * 60)
    print("Yahoo Finance Client Test Suite")
    print("=" * 60)
    
    results = test_yfinance_client()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for t in results["tests"] if t["status"] == "PASSED")
    failed = sum(1 for t in results["tests"] if t["status"] == "FAILED")
    errors = sum(1 for t in results["tests"] if t["status"] == "ERROR")
    warnings = sum(1 for t in results["tests"] if t["status"] == "WARNING")
    
    print(f"Total Tests: {len(results['tests'])}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
    
    for test in results["tests"]:
        status_icon = "✅" if test["status"] == "PASSED" else "❌" if test["status"] == "FAILED" else "⚠️" if test["status"] == "WARNING" else "🔴"
        print(f"\n{status_icon} {test['name']}: {test['message']}")
    
    # Save results
    os.makedirs("test-results", exist_ok=True)
    output_file = f"test-results/test_yfinance_client_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
