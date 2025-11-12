#!/usr/bin/env python3
"""
Test Scoring System
Tests the complete scoring workflow: analysis -> extraction -> database storage
"""

from dotenv import load_dotenv
load_dotenv()

import os
from utils.llm_client import LLMClient
from utils.score_extractor import extract_score_from_analysis, get_score_label, get_expected_movement_range
from utils.db_util import DatabaseUtil
from datetime import datetime, date

def test_scoring_system():
    """Test complete scoring workflow"""
    
    print("=" * 70)
    print("TESTING SCORING SYSTEM")
    print("=" * 70)
    
    # Check for transcripts
    transcript_dir = "transcripts"
    if not os.path.exists(transcript_dir):
        print("❌ Transcripts directory not found")
        return False
    
    transcripts = [f for f in os.listdir(transcript_dir) if f.endswith('.md')]
    if not transcripts:
        print("❌ No transcripts found")
        return False
    
    # Use first transcript
    transcript_file = transcripts[0]
    print(f"\n📄 Using transcript: {transcript_file}")
    
    # Parse filename
    parts = transcript_file.replace('.md', '').split('_')
    ticker = parts[0]
    quarter = int(parts[1].replace('Q', ''))
    year = int(parts[2])
    
    print(f"  Ticker: {ticker}")
    print(f"  Quarter: Q{quarter} {year}")
    
    # Read transcript
    with open(os.path.join(transcript_dir, transcript_file), 'r') as f:
        transcript_content = f.read()
    
    print(f"  Length: {len(transcript_content)} characters")
    
    # Initialize LLM client
    print(f"\n🤖 Running analysis with scoring...")
    print("  This may take 30-60 seconds...")
    
    try:
        llm_client = LLMClient(provider="openai", model="gpt-4.1-mini")
        
        analysis = llm_client.analyze_transcript(
            ticker=ticker,
            quarter=quarter,
            year=year,
            company_name=ticker,
            transcript=transcript_content,
            financial_context="No additional financial context provided."
        )
        
        print("\n✅ Analysis completed!")
        print(f"📊 Analysis length: {len(analysis)} characters")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return False
    
    # Extract score
    print(f"\n🔍 Extracting score from analysis...")
    
    score, justification = extract_score_from_analysis(analysis)
    
    if score is None:
        print("❌ Failed to extract score from analysis")
        print("\nSearching for score pattern in analysis...")
        if "**Score:" in analysis:
            print("✓ Found score pattern in text")
            # Print context around score
            idx = analysis.find("**Score:")
            print(f"\nContext:\n{analysis[max(0, idx-50):idx+200]}")
        else:
            print("❌ No score pattern found in analysis")
        return False
    
    print(f"✅ Score extracted: {score}/5")
    print(f"📝 Label: {get_score_label(score)}")
    print(f"📈 Expected movement: {get_expected_movement_range(score)}")
    print(f"💬 Justification: {justification[:200]}..." if len(justification) > 200 else f"💬 Justification: {justification}")
    
    # Save to database
    print(f"\n💾 Saving score to database...")
    
    try:
        db = DatabaseUtil()
        
        earnings_date = date.today()  # Use today for testing
        
        score_id = db.insert_score(
            ticker=ticker,
            quarter=quarter,
            year=year,
            earnings_date=earnings_date,
            score=score,
            score_justification=justification,
            provider="openai",
            model="gpt-4.1-mini",
            analysis_type="Standard Analysis"
        )
        
        print(f"✅ Score saved to database (ID: {score_id})")
        
    except Exception as e:
        print(f"❌ Database save failed: {e}")
        return False
    
    # Verify database entry
    print(f"\n🔍 Verifying database entry...")
    
    try:
        latest_score = db.get_latest_score(ticker)
        
        if latest_score:
            print(f"✅ Database entry verified:")
            print(f"  Ticker: {latest_score['ticker']}")
            print(f"  Score: {latest_score['score']}/5")
            print(f"  Quarter: Q{latest_score['quarter']} {latest_score['year']}")
            print(f"  Provider: {latest_score['provider']}")
            print(f"  Model: {latest_score['model']}")
        else:
            print("❌ Could not retrieve database entry")
            return False
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False
    
    # Test correlation query
    print(f"\n📊 Testing correlation query...")
    
    try:
        df = db.get_score_price_correlation(ticker)
        print(f"✅ Retrieved {len(df)} records for {ticker}")
        
        if len(df) > 0:
            print(f"\nLatest record:")
            latest = df.iloc[0]
            print(f"  Date: {latest['earnings_date']}")
            print(f"  Score: {latest['score']}")
            print(f"  Provider: {latest['provider']}")
    except Exception as e:
        print(f"❌ Correlation query failed: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    import sys
    success = test_scoring_system()
    sys.exit(0 if success else 1)
