#!/usr/bin/env python3
"""Test downloading transcripts from API Ninjas"""

from dotenv import load_dotenv
load_dotenv()

from utils.api_ninjas_client import APINinjasClient
import os

print('=' * 70)
print('TESTING API NINJAS TRANSCRIPT DOWNLOAD')
print('=' * 70)

client = APINinjasClient()

# Test companies (S&P 100)
test_cases = [
    ('AAPL', 2024, 3),  # Apple Q3 2024
    ('MSFT', 2024, 3),  # Microsoft Q3 2024
    ('GOOGL', 2024, 3), # Google Q3 2024
    ('AMZN', 2024, 3),  # Amazon Q3 2024
    ('TSLA', 2024, 3),  # Tesla Q3 2024
]

results = []

for ticker, year, quarter in test_cases:
    print(f'\nTesting {ticker} Q{quarter} {year}...')
    
    try:
        # Try to get transcript
        transcript = client.get_transcript(ticker, year, quarter)
        
        if transcript:
            print(f'  ✓ Transcript found!')
            print(f'    Date: {transcript.get("date", "N/A")}')
            
            # Get transcript content
            content = transcript.get('transcript', '')
            if content:
                print(f'    Length: {len(content)} characters')
                print(f'    Preview: {content[:200]}...')
                
                # Try to save it
                filepath = client.save_transcript_to_file(ticker, year, quarter)
                if filepath:
                    print(f'    ✓ Saved to: {filepath}')
                    results.append({'ticker': ticker, 'status': 'SUCCESS', 'file': filepath})
                else:
                    print(f'    ✗ Failed to save')
                    results.append({'ticker': ticker, 'status': 'SAVE_FAILED', 'file': None})
            else:
                print(f'    ⚠️  No transcript content')
                results.append({'ticker': ticker, 'status': 'NO_CONTENT', 'file': None})
        else:
            print(f'  ✗ Transcript not found')
            results.append({'ticker': ticker, 'status': 'NOT_FOUND', 'file': None})
    
    except Exception as e:
        print(f'  ✗ Error: {e}')
        results.append({'ticker': ticker, 'status': 'ERROR', 'file': None})

print('\n' + '=' * 70)
print('SUMMARY')
print('=' * 70)

success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
print(f'\n✓ Successfully downloaded: {success_count}/{len(results)} transcripts\n')

for result in results:
    status_icon = '✓' if result['status'] == 'SUCCESS' else '✗'
    print(f"{status_icon} {result['ticker']}: {result['status']}")
    if result['file']:
        print(f"   File: {result['file']}")

# Check transcripts directory
transcripts_dir = 'transcripts'
if os.path.exists(transcripts_dir):
    files = [f for f in os.listdir(transcripts_dir) if f.endswith('.md')]
    print(f'\n📁 Total transcripts in directory: {len(files)}')
    for f in files[:10]:  # Show first 10
        file_path = os.path.join(transcripts_dir, f)
        size = os.path.getsize(file_path)
        print(f'   - {f} ({size:,} bytes)')
    if len(files) > 10:
        print(f'   ... and {len(files) - 10} more')

print('=' * 70)
