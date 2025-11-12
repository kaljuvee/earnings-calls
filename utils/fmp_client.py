"""
Financial Modeling Prep API Client
Handles downloading earnings call transcripts
"""

import requests
import os
from typing import Optional, List, Dict
import json


class FMPClient:
    """Client for Financial Modeling Prep API"""
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    
    def __init__(self, api_key: str):
        """Initialize FMP client with API key"""
        self.api_key = api_key
        
    def get_transcript(self, ticker: str, quarter: int, year: int) -> Optional[str]:
        """
        Download earnings call transcript for a specific ticker, quarter, and year
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            quarter: Quarter number (1-4)
            year: Year (e.g., 2024)
            
        Returns:
            Transcript text or None if not found
        """
        endpoint = f"{self.BASE_URL}/earning_call_transcript/{ticker}"
        params = {
            "quarter": quarter,
            "year": year,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("content", "")
            elif isinstance(data, dict):
                return data.get("content", "")
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading transcript: {e}")
            return None
    
    def get_available_transcripts(self, ticker: str) -> List[Dict]:
        """
        Get list of available transcripts for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of available transcripts with metadata
        """
        # FMP doesn't have a direct endpoint for listing transcripts
        # We'll try to fetch recent quarters
        transcripts = []
        current_year = 2025
        
        for year in range(current_year, current_year - 3, -1):
            for quarter in range(4, 0, -1):
                endpoint = f"{self.BASE_URL}/earning_call_transcript/{ticker}"
                params = {
                    "quarter": quarter,
                    "year": year,
                    "apikey": self.api_key
                }
                
                try:
                    response = requests.get(endpoint, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            transcripts.append({
                                "ticker": ticker,
                                "quarter": quarter,
                                "year": year,
                                "date": data[0].get("date", ""),
                                "symbol": data[0].get("symbol", ticker)
                            })
                except:
                    continue
                    
        return transcripts
    
    def save_transcript(self, ticker: str, quarter: int, year: int, 
                       output_dir: str = "transcripts") -> Optional[str]:
        """
        Download and save transcript to file
        
        Args:
            ticker: Stock ticker symbol
            quarter: Quarter number (1-4)
            year: Year
            output_dir: Directory to save transcripts
            
        Returns:
            Path to saved file or None if failed
        """
        transcript = self.get_transcript(ticker, quarter, year)
        
        if not transcript:
            return None
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as text file
        txt_filename = f"{ticker}_Q{quarter}_{year}.txt"
        txt_path = os.path.join(output_dir, txt_filename)
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        # Convert to markdown format
        md_filename = f"{ticker}_Q{quarter}_{year}.md"
        md_path = os.path.join(output_dir, md_filename)
        
        markdown_content = self._convert_to_markdown(transcript, ticker, quarter, year)
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return md_path
    
    def _convert_to_markdown(self, transcript: str, ticker: str, 
                            quarter: int, year: int) -> str:
        """
        Convert plain text transcript to markdown format
        
        Args:
            transcript: Plain text transcript
            ticker: Stock ticker
            quarter: Quarter number
            year: Year
            
        Returns:
            Markdown formatted transcript
        """
        lines = transcript.split('\n')
        markdown_lines = [
            f"# {ticker} Q{quarter} {year} Earnings Call Transcript\n",
            f"**Ticker:** {ticker}  ",
            f"**Quarter:** Q{quarter} {year}\n",
            "---\n"
        ]
        
        # Process transcript lines
        for line in lines:
            line = line.strip()
            if not line:
                markdown_lines.append("")
                continue
                
            # Detect speaker names (usually in format "Name Title:")
            if ':' in line and len(line.split(':')[0].split()) <= 5:
                # Likely a speaker
                markdown_lines.append(f"\n**{line}**\n")
            else:
                markdown_lines.append(line)
        
        return '\n'.join(markdown_lines)
    
    def get_company_profile(self, ticker: str) -> Optional[Dict]:
        """
        Get company profile information
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Company profile data
        """
        endpoint = f"{self.BASE_URL}/profile/{ticker}"
        params = {"apikey": self.api_key}
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                return data[0]
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching company profile: {e}")
            return None
