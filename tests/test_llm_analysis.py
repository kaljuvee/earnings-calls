#!/usr/bin/env python3
"""
Test LLM Analysis from Command Line
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
from utils.llm_client import LLMClient

def test_llm_analysis():
    """Test LLM analysis with a sample transcript"""
    
    print("=" * 70)
    print("TESTING LLM ANALYSIS")
    print("=" * 70)
    
    # Check if we have transcripts
    transcript_dir = "transcripts"
    if not os.path.exists(transcript_dir):
        print("❌ Transcripts directory not found")
        return False
    
    transcripts = [f for f in os.listdir(transcript_dir) if f.endswith('.md')]
    if not transcripts:
        print("❌ No transcripts found")
        return False
    
    # Use the first transcript
    transcript_file = transcripts[0]
    print(f"\n📄 Using transcript: {transcript_file}")
    
    # Parse filename (e.g., AAPL_Q3_2024.md)
    parts = transcript_file.replace('.md', '').split('_')
    if len(parts) != 3:
        print(f"❌ Invalid filename format: {transcript_file}")
        return False
    
    ticker = parts[0]
    quarter = int(parts[1].replace('Q', ''))
    year = int(parts[2])
    
    print(f"  Ticker: {ticker}")
    print(f"  Quarter: Q{quarter} {year}")
    
    # Read transcript
    with open(os.path.join(transcript_dir, transcript_file), 'r') as f:
        transcript_content = f.read()
    
    print(f"  Length: {len(transcript_content)} characters")
    
    # Check API keys
    print("\n🔑 Checking API Keys...")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    # Use OpenAI provider (pre-configured)
    provider = "openai"
    print(f"✓ Using OpenAI (gpt-4.1-mini)")
    
    # Initialize LLM client
    print(f"\n🤖 Initializing LLM client ({provider})...")
    try:
        llm_client = LLMClient(provider=provider, model="gpt-4.1-mini")
        print("✓ LLM client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize LLM client: {e}")
        return False
    
    # Run analysis
    print(f"\n🔍 Running analysis...")
    print("  This may take 30-60 seconds...")
    
    try:
        analysis = llm_client.analyze_transcript(
            ticker=ticker,
            quarter=quarter,
            year=year,
            company_name=ticker,  # Using ticker as company name for now
            transcript=transcript_content,
            financial_context="No additional financial context provided."
        )
        
        print("\n✅ Analysis completed successfully!")
        print(f"\n📊 Analysis length: {len(analysis)} characters")
        
        # Save analysis
        output_file = f"analysis_{ticker}_Q{quarter}_{year}.md"
        with open(output_file, 'w') as f:
            f.write(analysis)
        
        print(f"💾 Analysis saved to: {output_file}")
        
        # Show preview
        print("\n" + "=" * 70)
        print("ANALYSIS PREVIEW (first 500 characters)")
        print("=" * 70)
        print(analysis[:500])
        print("\n... (truncated)")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_analysis()
    sys.exit(0 if success else 1)
