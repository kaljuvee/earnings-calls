"""
Finnhub Client for Earnings Call Transcripts
Provides access to earnings call transcripts via Finnhub API
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime

class FinnhubClient:
    """Client for Finnhub Earnings Call Transcript API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Finnhub client
        
        Args:
            api_key: API key for Finnhub. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('FINNHUB_API_KEY')
        if not self.api_key:
            raise ValueError("FINNHUB_API_KEY not found in environment variables")
        
        self.base_url = "https://finnhub.io/api/v1"
    
    def get_transcripts_list(self, symbol: str) -> List[Dict]:
        """
        Get list of available transcripts for a symbol
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
        
        Returns:
            List of available transcripts with metadata
        """
        try:
            url = f"{self.base_url}/stock/transcripts"
            params = {
                'symbol': symbol.upper(),
                'token': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for error message
            if isinstance(data, dict) and 'error' in data:
                print(f"API Error: {data['error']}")
                return []
            
            return data if isinstance(data, list) else []
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transcripts list: {e}")
            return []
    
    def get_transcript(self, transcript_id: str) -> Optional[Dict]:
        """
        Get full transcript by ID
        
        Args:
            transcript_id: Transcript ID from transcripts list
        
        Returns:
            Dictionary containing full transcript data
        """
        try:
            url = f"{self.base_url}/stock/transcripts"
            params = {
                'id': transcript_id,
                'token': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for error message
            if isinstance(data, dict) and 'error' in data:
                print(f"API Error: {data['error']}")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transcript: {e}")
            return None
    
    def find_transcript(self, symbol: str, year: int, quarter: int) -> Optional[Dict]:
        """
        Find transcript for specific symbol, year, and quarter
        
        Args:
            symbol: Stock ticker symbol
            year: Year of earnings call
            quarter: Quarter number (1-4)
        
        Returns:
            Transcript data or None if not found
        """
        transcripts = self.get_transcripts_list(symbol)
        
        if not transcripts:
            return None
        
        # Search for matching quarter/year
        for transcript in transcripts:
            # Parse quarter and year from transcript metadata
            transcript_quarter = transcript.get('quarter')
            transcript_year = transcript.get('year')
            
            if transcript_quarter == quarter and transcript_year == year:
                # Get full transcript
                transcript_id = transcript.get('id')
                if transcript_id:
                    return self.get_transcript(transcript_id)
        
        return None
    
    def save_transcript_to_file(self, symbol: str, year: int, quarter: int,
                                output_dir: str = "transcripts") -> Optional[str]:
        """
        Download and save transcript to a markdown file
        
        Args:
            symbol: Stock ticker symbol
            year: Year of earnings call
            quarter: Quarter number
            output_dir: Directory to save the transcript
        
        Returns:
            Path to saved file or None if failed
        """
        transcript = self.find_transcript(symbol, year, quarter)
        
        if not transcript:
            print(f"No transcript found for {symbol} Q{quarter} {year}")
            return None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        filename = f"{symbol}_Q{quarter}_{year}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Format transcript as markdown
        markdown_content = self._format_transcript_as_markdown(transcript, symbol, year, quarter)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Transcript saved to: {filepath}")
        return filepath
    
    def _format_transcript_as_markdown(self, transcript: Dict, symbol: str, 
                                      year: int, quarter: int) -> str:
        """
        Format transcript data as markdown
        
        Args:
            transcript: Transcript data dictionary
            symbol: Stock ticker symbol
            year: Year
            quarter: Quarter
        
        Returns:
            Formatted markdown string
        """
        # Start with header
        markdown = f"# {symbol} Q{quarter} {year} Earnings Call Transcript\n\n"
        markdown += f"**Company:** {symbol}\n"
        markdown += f"**Quarter:** Q{quarter} {year}\n"
        markdown += f"**Source:** Finnhub\n\n"
        markdown += "---\n\n"
        
        # Add transcript content
        if 'transcript' in transcript:
            transcript_data = transcript['transcript']
            
            if isinstance(transcript_data, list):
                # If transcript is structured with speakers
                for segment in transcript_data:
                    if isinstance(segment, dict):
                        speaker = segment.get('name', 'Unknown Speaker')
                        text = segment.get('speech', '')
                        markdown += f"## {speaker}\n\n{text}\n\n"
                    else:
                        markdown += f"{segment}\n\n"
            else:
                # If transcript is plain text
                markdown += f"{transcript_data}\n"
        else:
            markdown += "Transcript content not available.\n"
        
        return markdown


def test_finnhub_client():
    """Test function for Finnhub client"""
    try:
        client = FinnhubClient()
        
        print("Testing Finnhub Client...")
        print("=" * 50)
        
        # Test 1: Get transcripts list
        print("\n1. Testing get_transcripts_list('AAPL')...")
        transcripts = client.get_transcripts_list('AAPL')
        if transcripts:
            print(f"✓ Found {len(transcripts)} transcripts for AAPL")
            if len(transcripts) > 0:
                print(f"  Sample: {transcripts[0]}")
        else:
            print("✗ No transcripts found or API access denied")
        
        # Test 2: Find specific transcript
        print("\n2. Testing find_transcript('AAPL', 2024, 4)...")
        transcript = client.find_transcript('AAPL', 2024, 4)
        if transcript:
            print(f"✓ Found transcript for AAPL Q4 2024")
        else:
            print("✗ Transcript not found or API access denied")
        
        print("\n" + "=" * 50)
        print("Testing completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")


if __name__ == "__main__":
    test_finnhub_client()
