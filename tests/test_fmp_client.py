"""
Test FMP Client
Simple functional tests for FMP API client
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.fmp_client import FMPClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_fmp_client():
    """Test FMP client functionality"""
    
    results = {
        "test_name": "FMP Client Test",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    # Initialize client
    api_key = os.getenv("FMP_API_KEY")
    
    if not api_key:
        results["tests"].append({
            "name": "API Key Check",
            "status": "FAILED",
            "message": "FMP_API_KEY not found in environment"
        })
        return results
    
    results["tests"].append({
        "name": "API Key Check",
        "status": "PASSED",
        "message": "API key found"
    })
    
    client = FMPClient(api_key)
    
    # Test 1: Get company profile
    print("Test 1: Getting company profile for AAPL...")
    try:
        profile = client.get_company_profile("AAPL")
        
        if profile:
            results["tests"].append({
                "name": "Get Company Profile",
                "status": "PASSED",
                "message": f"Retrieved profile for {profile.get('companyName', 'AAPL')}",
                "data": {
                    "company": profile.get('companyName'),
                    "sector": profile.get('sector'),
                    "industry": profile.get('industry')
                }
            })
        else:
            results["tests"].append({
                "name": "Get Company Profile",
                "status": "FAILED",
                "message": "No profile data returned"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Get Company Profile",
            "status": "ERROR",
            "message": str(e)
        })
    
    # Test 2: Get transcript
    print("Test 2: Getting transcript for AAPL Q3 2024...")
    try:
        transcript = client.get_transcript("AAPL", 3, 2024)
        
        if transcript:
            results["tests"].append({
                "name": "Get Transcript",
                "status": "PASSED",
                "message": f"Retrieved transcript ({len(transcript)} characters)",
                "data": {
                    "length": len(transcript),
                    "preview": transcript[:200]
                }
            })
        else:
            results["tests"].append({
                "name": "Get Transcript",
                "status": "WARNING",
                "message": "No transcript found (may not be available for this quarter)"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Get Transcript",
            "status": "ERROR",
            "message": str(e)
        })
    
    # Test 3: Save transcript
    print("Test 3: Saving transcript...")
    try:
        saved_path = client.save_transcript("AAPL", 3, 2024, output_dir="test-results")
        
        if saved_path and os.path.exists(saved_path):
            results["tests"].append({
                "name": "Save Transcript",
                "status": "PASSED",
                "message": f"Transcript saved to {saved_path}",
                "data": {
                    "path": saved_path,
                    "exists": True
                }
            })
        else:
            results["tests"].append({
                "name": "Save Transcript",
                "status": "WARNING",
                "message": "Transcript not saved (may not be available)"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Save Transcript",
            "status": "ERROR",
            "message": str(e)
        })
    
    return results

def main():
    """Run tests and save results"""
    
    print("=" * 60)
    print("FMP Client Test Suite")
    print("=" * 60)
    
    results = test_fmp_client()
    
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
    output_file = f"test-results/test_fmp_client_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
