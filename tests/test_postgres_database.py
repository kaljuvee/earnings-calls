#!/usr/bin/env python3
"""
Test PostgreSQL Database Operations
Tests all CRUD operations for transcripts and analyses
"""

from dotenv import load_dotenv
load_dotenv()

import os
from datetime import date, datetime
from utils.database import Database

def test_database():
    """Test all database operations"""
    
    print("=" * 70)
    print("TESTING POSTGRESQL DATABASE OPERATIONS")
    print("=" * 70)
    
    try:
        # Initialize database
        print("\n1️⃣ Initializing database connection...")
        db = Database()
        print("✅ Database connected")
        
        # Test 1: Insert transcript
        print("\n2️⃣ Testing transcript insertion...")
        
        transcript_text = """
        Apple Inc. Q3 2024 Earnings Call Transcript
        
        CEO Tim Cook: Thank you for joining us today. We're pleased to report 
        strong results for Q3 2024, with revenue of $85.8 billion, up 10% year-over-year...
        
        CFO Luca Maestri: Our gross margin was 46.3%, reflecting strong operational 
        efficiency despite headwinds from tariffs...
        """
        
        transcript_id = db.insert_transcript(
            ticker="AAPL",
            quarter=3,
            year=2024,
            transcript_date=date(2024, 7, 31),
            transcript_text=transcript_text,
            source="api_ninjas",
            company_name="Apple Inc.",
            source_metadata={"api_version": "1.0", "quality": "high"}
        )
        
        print(f"✅ Transcript inserted with ID: {transcript_id}")
        
        # Test 2: Retrieve transcript
        print("\n3️⃣ Testing transcript retrieval...")
        
        transcript = db.get_transcript("AAPL", 3, 2024)
        
        if transcript:
            print(f"✅ Transcript retrieved:")
            print(f"   Ticker: {transcript['ticker']}")
            print(f"   Quarter: Q{transcript['quarter']} {transcript['year']}")
            print(f"   Date: {transcript['transcript_date']}")
            print(f"   Word count: {transcript['word_count']}")
            print(f"   Source: {transcript['source']}")
        else:
            print("❌ Transcript not found")
            return False
        
        # Test 3: Insert analysis
        print("\n4️⃣ Testing analysis insertion...")
        
        analysis_markdown = """
# Apple Inc. Q3 2024 Earnings Analysis

## 📊 Price Movement Score
**Score: +3/5**
**Justification:** Strong revenue beat and margin resilience despite tariff headwinds.

## 🐂 Bull Case
- Revenue up 10% YoY
- Strong iPhone and Services growth
- Margin resilience

## 🐻 Bear Case
- Tariff concerns
- China weakness
- Margin pressure

## ⚖️ Verdict
Solid beat with positive momentum. Stock should move higher.
"""
        
        analysis_json = {
            "bull_points": ["Revenue beat", "Margin resilience"],
            "bear_points": ["Tariff concerns", "China weakness"],
            "verdict": "Bullish"
        }
        
        analysis_id = db.insert_analysis(
            ticker="AAPL",
            quarter=3,
            year=2024,
            analysis_markdown=analysis_markdown,
            score=3,
            score_justification="Strong revenue beat and margin resilience despite tariff headwinds.",
            provider="openai",
            model="gpt-4.1-mini",
            analysis_type="Standard Analysis",
            transcript_id=transcript_id,
            analysis_json=analysis_json,
            financial_context_included=True,
            processing_time_seconds=32.5
        )
        
        print(f"✅ Analysis inserted with ID: {analysis_id}")
        
        # Test 4: Retrieve analysis
        print("\n5️⃣ Testing analysis retrieval...")
        
        analysis = db.get_analysis(analysis_id)
        
        if analysis:
            print(f"✅ Analysis retrieved:")
            print(f"   Ticker: {analysis['ticker']}")
            print(f"   Score: {analysis['score']}/5")
            print(f"   Provider: {analysis['provider']}")
            print(f"   Model: {analysis['model']}")
            print(f"   Type: {analysis['analysis_type']}")
        else:
            print("❌ Analysis not found")
            return False
        
        # Test 5: Insert price movement
        print("\n6️⃣ Testing price movement insertion...")
        
        price_id = db.insert_price_movement(
            ticker="AAPL",
            earnings_date=date(2024, 7, 31),
            price_before=225.00,
            price_after_1d=230.50,
            price_after_3d=232.75,
            price_after_5d=235.00,
            price_after_10d=238.25,
            volume_before=50000000,
            volume_after_1d=75000000
        )
        
        print(f"✅ Price movement inserted with ID: {price_id}")
        
        # Test 6: Get analysis performance
        print("\n7️⃣ Testing analysis performance query...")
        
        df = db.get_analysis_performance("AAPL")
        
        if not df.empty:
            print(f"✅ Analysis performance retrieved:")
            print(f"   Records: {len(df)}")
            print(f"   Columns: {', '.join(df.columns[:5])}...")
            
            # Show first record
            if len(df) > 0:
                record = df.iloc[0]
                print(f"\n   Latest record:")
                print(f"   - Ticker: {record['ticker']}")
                print(f"   - Score: {record['score']}")
                movement_1d = record['movement_1d_pct']
                movement_5d = record['movement_5d_pct']
                print(f"   - 1D Movement: {movement_1d:.2f}%" if movement_1d is not None else "   - 1D Movement: N/A")
                print(f"   - 5D Movement: {movement_5d:.2f}%" if movement_5d is not None else "   - 5D Movement: N/A")
                print(f"   - Direction Correct (1D): {record['direction_correct_1d']}")
        else:
            print("⚠️ No analysis performance data (this is expected for first run)")
        
        # Test 7: Calculate correlation
        print("\n8️⃣ Testing correlation calculation...")
        
        correlation, sample_size = db.calculate_correlation("AAPL", period_days=5)
        
        print(f"✅ Correlation calculated:")
        print(f"   Coefficient: {correlation:.3f}")
        print(f"   Sample size: {sample_size}")
        
        # Test 8: Get all tickers
        print("\n9️⃣ Testing ticker list retrieval...")
        
        tickers = db.get_all_tickers()
        
        print(f"✅ Tickers retrieved: {', '.join(tickers)}")
        
        # Test 9: Get database stats
        print("\n🔟 Testing database statistics...")
        
        stats = db.get_database_stats()
        
        print(f"✅ Database statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test 10: Get all analyses
        print("\n1️⃣1️⃣ Testing all analyses retrieval...")
        
        df_analyses = db.get_all_analyses(limit=10)
        
        print(f"✅ Analyses retrieved: {len(df_analyses)} records")
        
        if not df_analyses.empty:
            print(f"   Columns: {', '.join(df_analyses.columns)}")
        
        # Test 11: Get latest analysis
        print("\n1️⃣2️⃣ Testing latest analysis retrieval...")
        
        latest = db.get_latest_analysis("AAPL")
        
        if latest:
            print(f"✅ Latest analysis:")
            print(f"   Ticker: {latest['ticker']}")
            print(f"   Quarter: Q{latest['quarter']} {latest['year']}")
            print(f"   Score: {latest['score']}/5")
            print(f"   Date: {latest['analysis_date']}")
        
        print("\n" + "=" * 70)
        print("✅ ALL DATABASE TESTS PASSED")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_database()
    sys.exit(0 if success else 1)
