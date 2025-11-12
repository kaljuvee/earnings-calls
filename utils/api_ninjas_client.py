"""
API Ninjas Client for Earnings Call Transcripts
Provides access to earnings call transcripts for S&P 100 companies (free tier)
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime

class APINinjasClient:
    """Client for API Ninjas Earnings Call Transcript API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API Ninjas client
        
        Args:
            api_key: API key for API Ninjas. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('API_NINJAS_KEY')
        if not self.api_key:
            raise ValueError("API_NINJAS_KEY not found in environment variables")
        
        self.base_url = "https://api.api-ninjas.com/v1"
        self.headers = {
            'X-Api-Key': self.api_key
        }
    
    def get_transcript(self, ticker: str, year: int, quarter: int) -> Optional[Dict]:
        """
        Get earnings call transcript for a specific company and quarter
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            year: Year of the earnings call (e.g., 2024)
            quarter: Quarter number (1, 2, 3, or 4)
        
        Returns:
            Dictionary containing transcript data or None if not found
        """
        try:
            url = f"{self.base_url}/earningstranscript"
            params = {
                'ticker': ticker.upper()
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter by year and quarter if data is returned
            if data and isinstance(data, dict):
                # Check if the transcript matches the requested quarter/year
                transcript_year = data.get('year')
                transcript_quarter = data.get('quarter')
                
                if transcript_year == str(year) and transcript_quarter == str(quarter):
                    return data
                else:
                    # Try searching for the specific quarter
                    return self._search_transcript(ticker, year, quarter)
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transcript: {e}")
            return None
    
    def _search_transcript(self, ticker: str, year: int, quarter: int) -> Optional[Dict]:
        """
        Search for a specific transcript by ticker, year, and quarter
        
        Args:
            ticker: Stock ticker symbol
            year: Year of the earnings call
            quarter: Quarter number (1, 2, 3, or 4)
        
        Returns:
            Dictionary containing transcript data or None if not found
        """
        try:
            url = f"{self.base_url}/earningstranscriptsearch"
            params = {
                'ticker': ticker.upper()
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            results = response.json()
            
            # Search through results for matching year/quarter
            if isinstance(results, list):
                for result in results:
                    if (result.get('year') == str(year) and 
                        result.get('quarter') == str(quarter)):
                        return result
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching transcript: {e}")
            return None
    
    def list_available_companies(self) -> List[Dict]:
        """
        Get list of all companies with available earnings transcripts
        
        Returns:
            List of dictionaries containing company information
        """
        try:
            url = f"{self.base_url}/earningstranscriptlist"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching company list: {e}")
            return []
    
    def search_transcripts(self, ticker: str) -> List[Dict]:
        """
        Search for all available transcripts for a given ticker
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            List of available transcripts
        """
        try:
            url = f"{self.base_url}/earningstranscriptsearch"
            params = {
                'ticker': ticker.upper()
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            results = response.json()
            return results if isinstance(results, list) else []
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching transcripts: {e}")
            return []
    
    def save_transcript_to_file(self, ticker: str, year: int, quarter: int, 
                                output_dir: str = "transcripts") -> Optional[str]:
        """
        Download and save transcript to a markdown file
        
        Args:
            ticker: Stock ticker symbol
            year: Year of the earnings call
            quarter: Quarter number
            output_dir: Directory to save the transcript
        
        Returns:
            Path to saved file or None if failed
        """
        transcript = self.get_transcript(ticker, year, quarter)
        
        if not transcript:
            print(f"No transcript found for {ticker} Q{quarter} {year}")
            return None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        filename = f"{ticker}_Q{quarter}_{year}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Format transcript as markdown
        markdown_content = self._format_transcript_as_markdown(transcript)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Transcript saved to: {filepath}")
        return filepath
    
    def _format_transcript_as_markdown(self, transcript: Dict) -> str:
        """
        Format transcript data as markdown
        
        Args:
            transcript: Transcript data dictionary
        
        Returns:
            Formatted markdown string
        """
        ticker = transcript.get('ticker', 'Unknown')
        year = transcript.get('year', 'Unknown')
        quarter = transcript.get('quarter', 'Unknown')
        date = transcript.get('date', 'Unknown')
        
        # Start with header
        markdown = f"# {ticker} Q{quarter} {year} Earnings Call Transcript\n\n"
        markdown += f"**Date:** {date}\n"
        markdown += f"**Company:** {ticker}\n"
        markdown += f"**Quarter:** Q{quarter} {year}\n\n"
        markdown += "---\n\n"
        
        # Add transcript text
        transcript_text = transcript.get('transcript', '')
        if isinstance(transcript_text, list):
            # If transcript is a list of segments
            for segment in transcript_text:
                if isinstance(segment, dict):
                    speaker = segment.get('name', 'Unknown Speaker')
                    text = segment.get('speech', '')
                    markdown += f"## {speaker}\n\n{text}\n\n"
                else:
                    markdown += f"{segment}\n\n"
        else:
            # If transcript is a single text block
            markdown += f"{transcript_text}\n"
        
        return markdown


def test_api_ninjas_client():
    """Test function for API Ninjas client"""
    try:
        client = APINinjasClient()
        
        print("Testing API Ninjas Client...")
        print("=" * 50)
        
        # Test 1: List available companies
        print("\n1. Testing list_available_companies()...")
        companies = client.list_available_companies()
        if companies:
            print(f"✓ Found {len(companies)} companies")
            if len(companies) > 0:
                print(f"  Sample: {companies[0]}")
        else:
            print("✗ No companies found")
        
        # Test 2: Search for Apple transcripts
        print("\n2. Testing search_transcripts('AAPL')...")
        transcripts = client.search_transcripts('AAPL')
        if transcripts:
            print(f"✓ Found {len(transcripts)} transcripts for AAPL")
            if len(transcripts) > 0:
                print(f"  Latest: Q{transcripts[0].get('quarter')} {transcripts[0].get('year')}")
        else:
            print("✗ No transcripts found for AAPL")
        
        # Test 3: Get specific transcript
        print("\n3. Testing get_transcript('MSFT', 2024, 3)...")
        transcript = client.get_transcript('MSFT', 2024, 3)
        if transcript:
            print(f"✓ Retrieved transcript for MSFT Q3 2024")
            print(f"  Date: {transcript.get('date')}")
            print(f"  Length: {len(str(transcript.get('transcript', '')))} characters")
        else:
            print("✗ Transcript not found")
        
        # Test 4: Save transcript to file
        print("\n4. Testing save_transcript_to_file('AAPL', 2024, 4)...")
        filepath = client.save_transcript_to_file('AAPL', 2024, 4)
        if filepath:
            print(f"✓ Transcript saved to: {filepath}")
        else:
            print("✗ Failed to save transcript")
        
        print("\n" + "=" * 50)
        print("Testing completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")


if __name__ == "__main__":
    test_api_ninjas_client()
