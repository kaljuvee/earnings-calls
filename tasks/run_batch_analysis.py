#!/usr/bin/env python3
"""
Batch Analysis Task: Mag 7 Stocks 2024
Downloads and analyzes earnings call transcripts for Magnificent 7 stocks
Stores results in PostgreSQL database
"""

import os
import sys
from datetime import datetime, date
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from utils.api_ninjas_client import APINinjasClient
from utils.llm_client import LLMClient
from utils.database import Database
from utils.score_extractor import extract_score_from_analysis

# Magnificent 7 stocks
MAG_7_STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'META': 'Meta Platforms Inc.',
    'TSLA': 'Tesla Inc.',
    'NVDA': 'NVIDIA Corporation'
}

# 2024 quarters
QUARTERS_2024 = [
    (1, 2024),  # Q1 2024
    (2, 2024),  # Q2 2024
    (3, 2024),  # Q3 2024
]


class BatchAnalyzer:
    """
    Batch analyzer for earnings call transcripts
    """
    
    def __init__(self):
        """Initialize clients"""
        self.api_ninjas = APINinjasClient()
        self.llm_client = LLMClient(provider='openai', model='gpt-4.1-mini')
        self.db = Database()
        
        # Create logs directory
        self.log_dir = Path(__file__).parent / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        
        # Log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f'batch_analysis_{timestamp}.log'
        
    def log(self, message: str):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')
    
    def download_transcript(self, ticker: str, quarter: int, year: int) -> tuple:
        """
        Download transcript from API Ninjas
        
        Returns:
            (success: bool, transcript_text: str, transcript_date: date)
        """
        try:
            self.log(f"Downloading {ticker} Q{quarter} {year}...")
            
            result = self.api_ninjas.get_transcript(ticker, quarter, year)
            
            if result and 'transcript' in result:
                transcript_text = result['transcript']
                transcript_date = result.get('date', date.today())
                
                # Convert date string to date object if needed
                if isinstance(transcript_date, str):
                    try:
                        transcript_date = datetime.strptime(transcript_date, '%Y-%m-%d').date()
                    except:
                        transcript_date = date.today()
                
                self.log(f"✅ Downloaded {ticker} Q{quarter} {year} ({len(transcript_text)} chars)")
                return True, transcript_text, transcript_date
            else:
                self.log(f"⚠️ No transcript found for {ticker} Q{quarter} {year}")
                return False, None, None
                
        except Exception as e:
            self.log(f"❌ Error downloading {ticker} Q{quarter} {year}: {e}")
            return False, None, None
    
    def analyze_transcript(self, ticker: str, quarter: int, year: int, transcript_text: str) -> tuple:
        """
        Analyze transcript with LLM
        
        Returns:
            (success: bool, analysis_markdown: str, score: int, justification: str)
        """
        try:
            self.log(f"Analyzing {ticker} Q{quarter} {year}...")
            
            start_time = time.time()
            
            analysis = self.llm_client.analyze_transcript(
                ticker=ticker,
                quarter=quarter,
                year=year,
                company_name=MAG_7_STOCKS.get(ticker, ticker),
                transcript=transcript_text,
                financial_context=""
            )
            
            processing_time = time.time() - start_time
            
            # Extract score
            score, justification = extract_score_from_analysis(analysis)
            
            if score is None:
                self.log(f"⚠️ Could not extract score from {ticker} Q{quarter} {year} analysis")
                score = 0
                justification = "Score extraction failed"
            
            self.log(f"✅ Analyzed {ticker} Q{quarter} {year} - Score: {score}/5 ({processing_time:.1f}s)")
            
            return True, analysis, score, justification, processing_time
            
        except Exception as e:
            self.log(f"❌ Error analyzing {ticker} Q{quarter} {year}: {e}")
            return False, None, None, None, None
    
    def save_to_database(
        self,
        ticker: str,
        quarter: int,
        year: int,
        company_name: str,
        transcript_text: str,
        transcript_date: date,
        analysis_markdown: str,
        score: int,
        score_justification: str,
        processing_time: float
    ) -> bool:
        """
        Save transcript and analysis to database
        
        Returns:
            success: bool
        """
        try:
            # Save transcript
            transcript_id = self.db.insert_transcript(
                ticker=ticker,
                quarter=quarter,
                year=year,
                transcript_date=transcript_date,
                transcript_text=transcript_text,
                source='api_ninjas',
                company_name=company_name
            )
            
            # Save analysis
            analysis_id = self.db.insert_analysis(
                ticker=ticker,
                quarter=quarter,
                year=year,
                analysis_markdown=analysis_markdown,
                score=score,
                score_justification=score_justification,
                provider='openai',
                model='gpt-4.1-mini',
                analysis_type='Standard Analysis',
                transcript_id=transcript_id,
                financial_context_included=False,
                processing_time_seconds=processing_time
            )
            
            self.log(f"💾 Saved {ticker} Q{quarter} {year} to database (transcript_id={transcript_id}, analysis_id={analysis_id})")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error saving {ticker} Q{quarter} {year} to database: {e}")
            return False
    
    def process_stock(self, ticker: str, quarter: int, year: int) -> dict:
        """
        Process a single stock/quarter combination
        
        Returns:
            result: dict with status and details
        """
        result = {
            'ticker': ticker,
            'quarter': quarter,
            'year': year,
            'success': False,
            'transcript_downloaded': False,
            'analysis_completed': False,
            'database_saved': False,
            'score': None,
            'error': None
        }
        
        try:
            # Download transcript
            success, transcript_text, transcript_date = self.download_transcript(ticker, quarter, year)
            
            if not success:
                result['error'] = 'Transcript download failed'
                return result
            
            result['transcript_downloaded'] = True
            
            # Analyze transcript
            success, analysis, score, justification, processing_time = self.analyze_transcript(
                ticker, quarter, year, transcript_text
            )
            
            if not success:
                result['error'] = 'Analysis failed'
                return result
            
            result['analysis_completed'] = True
            result['score'] = score
            
            # Save to database
            success = self.save_to_database(
                ticker=ticker,
                quarter=quarter,
                year=year,
                company_name=MAG_7_STOCKS.get(ticker, ticker),
                transcript_text=transcript_text,
                transcript_date=transcript_date,
                analysis_markdown=analysis,
                score=score,
                score_justification=justification,
                processing_time=processing_time
            )
            
            if not success:
                result['error'] = 'Database save failed'
                return result
            
            result['database_saved'] = True
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            self.log(f"❌ Error processing {ticker} Q{quarter} {year}: {e}")
        
        return result
    
    def run(self):
        """Run batch analysis for all Mag 7 stocks"""
        
        self.log("=" * 70)
        self.log("BATCH ANALYSIS: MAG 7 STOCKS 2024")
        self.log("=" * 70)
        
        self.log(f"\nStocks: {', '.join(MAG_7_STOCKS.keys())}")
        self.log(f"Quarters: Q1, Q2, Q3 2024")
        self.log(f"Total: {len(MAG_7_STOCKS) * len(QUARTERS_2024)} transcripts\n")
        
        results = []
        total = len(MAG_7_STOCKS) * len(QUARTERS_2024)
        current = 0
        
        start_time = time.time()
        
        for ticker in MAG_7_STOCKS.keys():
            for quarter, year in QUARTERS_2024:
                current += 1
                
                self.log(f"\n[{current}/{total}] Processing {ticker} Q{quarter} {year}")
                self.log("-" * 70)
                
                result = self.process_stock(ticker, quarter, year)
                results.append(result)
                
                # Small delay to avoid rate limiting
                time.sleep(2)
        
        total_time = time.time() - start_time
        
        # Generate summary
        self.log("\n" + "=" * 70)
        self.log("BATCH ANALYSIS SUMMARY")
        self.log("=" * 70)
        
        successful = sum(1 for r in results if r['success'])
        failed = total - successful
        
        self.log(f"\nTotal processed: {total}")
        self.log(f"Successful: {successful}")
        self.log(f"Failed: {failed}")
        self.log(f"Total time: {total_time/60:.1f} minutes")
        self.log(f"Average time per transcript: {total_time/total:.1f} seconds")
        
        # Score distribution
        scores = [r['score'] for r in results if r['score'] is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            self.log(f"\nAverage score: {avg_score:.2f}/5")
            self.log(f"Score range: {min(scores)} to {max(scores)}")
        
        # Failed transcripts
        if failed > 0:
            self.log(f"\n⚠️ Failed transcripts:")
            for r in results:
                if not r['success']:
                    self.log(f"  - {r['ticker']} Q{r['quarter']} {r['year']}: {r['error']}")
        
        # Database statistics
        self.log(f"\n📊 Database Statistics:")
        stats = self.db.get_database_stats()
        for key, value in stats.items():
            self.log(f"  {key}: {value}")
        
        self.log(f"\n✅ Batch analysis complete!")
        self.log(f"📄 Log file: {self.log_file}")
        self.log("=" * 70)
        
        return results


def main():
    """Main entry point"""
    
    # Check environment variables
    if not os.getenv('API_NINJAS_KEY'):
        print("❌ Error: API_NINJAS_KEY not found in environment")
        return False
    
    if not os.getenv('DB_URL'):
        print("❌ Error: DB_URL not found in environment")
        return False
    
    # Run batch analysis
    analyzer = BatchAnalyzer()
    results = analyzer.run()
    
    # Return success if at least one transcript was processed
    return any(r['success'] for r in results)


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
