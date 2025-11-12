"""
Run All Tests
Execute all test suites and generate summary report
"""

import os
import sys
import json
from datetime import datetime
import subprocess

def run_test_file(test_file):
    """Run a single test file and return results"""
    
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return {
            "file": test_file,
            "status": "COMPLETED" if result.returncode == 0 else "FAILED",
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            "file": test_file,
            "status": "TIMEOUT",
            "return_code": -1,
            "stdout": "",
            "stderr": "Test timed out after 120 seconds"
        }
    except Exception as e:
        return {
            "file": test_file,
            "status": "ERROR",
            "return_code": -1,
            "stdout": "",
            "stderr": str(e)
        }

def main():
    """Run all tests"""
    
    print("="*60)
    print("EARNINGS CALL ANALYZER - TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Get test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all test files
    test_files = [
        os.path.join(test_dir, f)
        for f in os.listdir(test_dir)
        if f.startswith('test_') and f.endswith('.py')
    ]
    
    if not test_files:
        print("⚠️ No test files found!")
        return
    
    print(f"\nFound {len(test_files)} test files:")
    for f in test_files:
        print(f"  - {os.path.basename(f)}")
    
    # Run all tests
    results = []
    
    for test_file in test_files:
        result = run_test_file(test_file)
        results.append(result)
    
    # Generate summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    completed = sum(1 for r in results if r["status"] == "COMPLETED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    timeouts = sum(1 for r in results if r["status"] == "TIMEOUT")
    
    print(f"\nTotal Test Files: {len(results)}")
    print(f"✅ Completed: {completed}")
    print(f"❌ Failed: {failed}")
    print(f"🔴 Errors: {errors}")
    print(f"⏱️ Timeouts: {timeouts}")
    
    print("\nDetailed Results:")
    for result in results:
        status_icon = "✅" if result["status"] == "COMPLETED" else "❌"
        print(f"{status_icon} {os.path.basename(result['file'])}: {result['status']}")
    
    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "completed": completed,
        "failed": failed,
        "errors": errors,
        "timeouts": timeouts,
        "results": results
    }
    
    os.makedirs("test-results", exist_ok=True)
    summary_file = f"test-results/test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Summary saved to: {summary_file}")
    print("="*60)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    main()
