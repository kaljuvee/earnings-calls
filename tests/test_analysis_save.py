#!/usr/bin/env python3
"""
Test Analysis Save Functionality
Tests saving analyses in both JSON and MD formats
"""

from dotenv import load_dotenv
load_dotenv()

import os
import json
from utils.llm_client import LLMClient
from datetime import datetime

def test_analysis_save():
    """Test saving analysis in both JSON and MD formats"""
    
    print("=" * 70)
    print("TESTING ANALYSIS SAVE FUNCTIONALITY")
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
    
    # Parse filename
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
    
    # Initialize LLM client
    print(f"\n🤖 Initializing OpenAI client...")
    try:
        llm_client = LLMClient(provider="openai", model="gpt-4.1-mini")
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
            company_name=ticker,
            transcript=transcript_content,
            financial_context="No additional financial context provided."
        )
        
        print("\n✅ Analysis completed!")
        print(f"📊 Analysis length: {len(analysis)} characters")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return False
    
    # Save in both formats
    print(f"\n💾 Saving analysis in both formats...")
    
    analyses_dir = "analyses"
    os.makedirs(analyses_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{ticker}_Q{quarter}_{year}_{timestamp}"
    
    # Save as Markdown
    md_file = f"{base_filename}.md"
    md_path = os.path.join(analyses_dir, md_file)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(analysis)
    
    print(f"✓ Markdown saved: {md_path}")
    print(f"  File size: {os.path.getsize(md_path)} bytes")
    
    # Save as JSON with metadata
    json_file = f"{base_filename}.json"
    json_path = os.path.join(analyses_dir, json_file)
    analysis_data = {
        "ticker": ticker,
        "quarter": quarter,
        "year": year,
        "company_name": ticker,
        "timestamp": timestamp,
        "provider": "openai",
        "model": "gpt-4.1-mini",
        "analysis_type": "Standard Analysis",
        "analysis_markdown": analysis,
        "financial_context_included": False
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"✓ JSON saved: {json_path}")
    print(f"  File size: {os.path.getsize(json_path)} bytes")
    
    # Verify files can be read back
    print(f"\n🔍 Verifying saved files...")
    
    # Verify MD
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    if md_content == analysis:
        print("✓ Markdown file verified")
    else:
        print("❌ Markdown file verification failed")
        return False
    
    # Verify JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        json_content = json.load(f)
    if json_content['analysis_markdown'] == analysis:
        print("✓ JSON file verified")
    else:
        print("❌ JSON file verification failed")
        return False
    
    # List all files in analyses directory
    print(f"\n📂 Files in analyses/ directory:")
    analyses_files = os.listdir(analyses_dir)
    for file in sorted(analyses_files):
        file_path = os.path.join(analyses_dir, file)
        size = os.path.getsize(file_path)
        print(f"  - {file} ({size} bytes)")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    import sys
    success = test_analysis_save()
    sys.exit(0 if success else 1)
