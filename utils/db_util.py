"""
Database Utility for Earnings Call Analysis Scores
Handles SQLite database operations for storing and querying analysis scores and price movements
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Tuple
import pandas as pd


class DatabaseUtil:
    """Utility class for database operations"""
    
    def __init__(self, db_path: str = "data/earnings_analysis.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema from SQL file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_path = "sql/create_tables.sql"
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema = f.read()
                cursor.executescript(schema)
        
        conn.commit()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def insert_score(self, ticker: str, quarter: int, year: int, 
                    earnings_date: date, score: int, score_justification: str,
                    provider: str, model: Optional[str], analysis_type: str,
                    analysis_timestamp: Optional[datetime] = None) -> int:
        """
        Insert analysis score into database
        
        Args:
            ticker: Stock ticker symbol
            quarter: Quarter number (1-4)
            year: Year
            earnings_date: Date of earnings call
            score: Score from -5 to +5
            score_justification: Explanation of the score
            provider: LLM provider (openai, xai, gemini)
            model: Model name
            analysis_type: Type of analysis
            analysis_timestamp: Timestamp of analysis (defaults to now)
            
        Returns:
            ID of inserted record
        """
        if analysis_timestamp is None:
            analysis_timestamp = datetime.now()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO scores 
                (ticker, quarter, year, earnings_date, analysis_timestamp, score, 
                 score_justification, provider, model, analysis_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticker, quarter, year, earnings_date, analysis_timestamp, score,
                  score_justification, provider, model, analysis_type))
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            # Record already exists, update instead
            cursor.execute("""
                UPDATE scores 
                SET score = ?, score_justification = ?, provider = ?, model = ?, 
                    analysis_type = ?
                WHERE ticker = ? AND quarter = ? AND year = ? AND analysis_timestamp = ?
            """, (score, score_justification, provider, model, analysis_type,
                  ticker, quarter, year, analysis_timestamp))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def insert_price_movement(self, ticker: str, earnings_date: date,
                             price_before: float, price_after_1d: Optional[float] = None,
                             price_after_3d: Optional[float] = None,
                             price_after_5d: Optional[float] = None,
                             price_after_10d: Optional[float] = None,
                             volume_before: Optional[int] = None,
                             volume_after_1d: Optional[int] = None) -> int:
        """
        Insert or update price movement data
        
        Args:
            ticker: Stock ticker symbol
            earnings_date: Date of earnings call
            price_before: Stock price before earnings
            price_after_1d: Price 1 day after
            price_after_3d: Price 3 days after
            price_after_5d: Price 5 days after
            price_after_10d: Price 10 days after
            volume_before: Volume before earnings
            volume_after_1d: Volume 1 day after
            
        Returns:
            ID of inserted/updated record
        """
        # Calculate percentage movements
        movement_1d = ((price_after_1d - price_before) / price_before * 100) if price_after_1d else None
        movement_3d = ((price_after_3d - price_before) / price_before * 100) if price_after_3d else None
        movement_5d = ((price_after_5d - price_before) / price_before * 100) if price_after_5d else None
        movement_10d = ((price_after_10d - price_before) / price_before * 100) if price_after_10d else None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO price_movements 
                (ticker, earnings_date, price_before, price_after_1d, price_after_3d, 
                 price_after_5d, price_after_10d, movement_1d_pct, movement_3d_pct, 
                 movement_5d_pct, movement_10d_pct, volume_before, volume_after_1d)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticker, earnings_date, price_before, price_after_1d, price_after_3d,
                  price_after_5d, price_after_10d, movement_1d, movement_3d,
                  movement_5d, movement_10d, volume_before, volume_after_1d))
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Update existing record
            cursor.execute("""
                UPDATE price_movements 
                SET price_before = ?, price_after_1d = ?, price_after_3d = ?, 
                    price_after_5d = ?, price_after_10d = ?, movement_1d_pct = ?, 
                    movement_3d_pct = ?, movement_5d_pct = ?, movement_10d_pct = ?,
                    volume_before = ?, volume_after_1d = ?, updated_at = CURRENT_TIMESTAMP
                WHERE ticker = ? AND earnings_date = ?
            """, (price_before, price_after_1d, price_after_3d, price_after_5d,
                  price_after_10d, movement_1d, movement_3d, movement_5d, movement_10d,
                  volume_before, volume_after_1d, ticker, earnings_date))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_scores_by_ticker(self, ticker: str) -> pd.DataFrame:
        """
        Get all scores for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with scores
        """
        conn = self.get_connection()
        query = """
            SELECT * FROM scores 
            WHERE ticker = ? 
            ORDER BY earnings_date DESC
        """
        df = pd.read_sql_query(query, conn, params=(ticker,))
        conn.close()
        return df
    
    def get_score_price_correlation(self, ticker: Optional[str] = None) -> pd.DataFrame:
        """
        Get score-price correlation data
        
        Args:
            ticker: Optional ticker to filter by
            
        Returns:
            DataFrame with scores and price movements
        """
        conn = self.get_connection()
        
        if ticker:
            query = """
                SELECT * FROM score_price_correlation 
                WHERE ticker = ?
                ORDER BY earnings_date DESC
            """
            df = pd.read_sql_query(query, conn, params=(ticker,))
        else:
            query = """
                SELECT * FROM score_price_correlation 
                ORDER BY earnings_date DESC
            """
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def calculate_correlation(self, ticker: Optional[str] = None, 
                            period_days: int = 1) -> Tuple[float, int]:
        """
        Calculate correlation between scores and price movements
        
        Args:
            ticker: Optional ticker to filter by
            period_days: Period to analyze (1, 3, 5, or 10 days)
            
        Returns:
            Tuple of (correlation coefficient, sample size)
        """
        df = self.get_score_price_correlation(ticker)
        
        # Select appropriate movement column
        movement_col = f'movement_{period_days}d_pct'
        
        # Filter out rows with missing data
        df_clean = df[['score', movement_col]].dropna()
        
        if len(df_clean) < 2:
            return 0.0, 0
        
        correlation = df_clean['score'].corr(df_clean[movement_col])
        sample_size = len(df_clean)
        
        return correlation, sample_size
    
    def insert_analysis_metadata(self, ticker: str, quarter: int, year: int,
                                company_name: str, analysis_file_path: str,
                                json_file_path: str, financial_context_included: bool,
                                predictions_included: bool, analysis_length: int) -> int:
        """
        Insert analysis metadata
        
        Args:
            ticker: Stock ticker
            quarter: Quarter number
            year: Year
            company_name: Company name
            analysis_file_path: Path to markdown file
            json_file_path: Path to JSON file
            financial_context_included: Whether financial context was included
            predictions_included: Whether predictions were included
            analysis_length: Length of analysis in characters
            
        Returns:
            ID of inserted record
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO analysis_metadata 
            (ticker, quarter, year, company_name, analysis_file_path, json_file_path,
             financial_context_included, predictions_included, analysis_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticker, quarter, year, company_name, analysis_file_path, json_file_path,
              financial_context_included, predictions_included, analysis_length))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return record_id
    
    def get_all_tickers(self) -> List[str]:
        """Get list of all tickers in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ticker FROM scores ORDER BY ticker")
        tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tickers
    
    def get_latest_score(self, ticker: str) -> Optional[Dict]:
        """
        Get latest score for a ticker
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with score data or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM scores 
            WHERE ticker = ? 
            ORDER BY earnings_date DESC, created_at DESC 
            LIMIT 1
        """, (ticker,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
