"""
PostgreSQL Database Utility using SQLAlchemy
Handles all database operations for transcripts and analyses
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from contextlib import contextmanager

from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import pandas as pd

from utils.models import Base, Transcript, Analysis, PriceMovement, Correlation


class Database:
    """
    PostgreSQL database manager using SQLAlchemy
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            db_url: PostgreSQL connection URL. If None, reads from environment variable DB_URL
        """
        self.db_url = db_url or os.getenv('DB_URL')
        
        if not self.db_url:
            raise ValueError("Database URL not provided. Set DB_URL environment variable or pass db_url parameter.")
        
        # Create engine
        self.engine = create_engine(
            self.db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialize database (create tables if they don't exist)
        self._init_database()
    
    def _init_database(self):
        """
        Initialize database schema and tables
        """
        try:
            # Create schema if not exists
            with self.engine.connect() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS earnings"))
                conn.commit()
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions
        
        Usage:
            with db.get_session() as session:
                # Do database operations
                pass
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    # ============================================================================
    # Transcript Operations
    # ============================================================================
    
    def insert_transcript(
        self,
        ticker: str,
        quarter: int,
        year: int,
        transcript_date: date,
        transcript_text: str,
        source: str,
        company_name: Optional[str] = None,
        source_metadata: Optional[Dict] = None
    ) -> int:
        """
        Insert a new transcript
        
        Returns:
            transcript_id: ID of inserted transcript
        """
        with self.get_session() as session:
            # Calculate word count
            word_count = len(transcript_text.split())
            
            transcript = Transcript(
                ticker=ticker.upper(),
                company_name=company_name,
                quarter=quarter,
                year=year,
                transcript_date=transcript_date,
                transcript_text=transcript_text,
                source=source,
                source_metadata=source_metadata,
                word_count=word_count
            )
            
            try:
                session.add(transcript)
                session.flush()
                return transcript.id
            except IntegrityError:
                # Transcript already exists, rollback and update
                session.rollback()
                
                existing = session.query(Transcript).filter_by(
                    ticker=ticker.upper(),
                    quarter=quarter,
                    year=year
                ).first()
                
                if existing:
                    existing.transcript_text = transcript_text
                    existing.transcript_date = transcript_date
                    existing.source = source
                    existing.company_name = company_name
                    existing.source_metadata = source_metadata
                    existing.word_count = word_count
                    session.commit()
                    return existing.id
                else:
                    raise
    
    def get_transcript(self, ticker: str, quarter: int, year: int) -> Optional[Dict]:
        """
        Get transcript by ticker, quarter, and year
        
        Returns:
            Dictionary with transcript data or None if not found
        """
        with self.get_session() as session:
            transcript = session.query(Transcript).filter_by(
                ticker=ticker.upper(),
                quarter=quarter,
                year=year
            ).first()
            
            if transcript:
                return {
                    'id': transcript.id,
                    'ticker': transcript.ticker,
                    'company_name': transcript.company_name,
                    'quarter': transcript.quarter,
                    'year': transcript.year,
                    'transcript_date': transcript.transcript_date,
                    'transcript_text': transcript.transcript_text,
                    'source': transcript.source,
                    'word_count': transcript.word_count,
                    'created_at': transcript.created_at
                }
            return None
    
    def get_all_transcripts(self, ticker: Optional[str] = None) -> pd.DataFrame:
        """
        Get all transcripts, optionally filtered by ticker
        
        Returns:
            DataFrame with transcript metadata (not full text)
        """
        with self.get_session() as session:
            query = session.query(
                Transcript.id,
                Transcript.ticker,
                Transcript.company_name,
                Transcript.quarter,
                Transcript.year,
                Transcript.transcript_date,
                Transcript.source,
                Transcript.word_count,
                Transcript.created_at
            )
            
            if ticker:
                query = query.filter(Transcript.ticker == ticker.upper())
            
            query = query.order_by(Transcript.transcript_date.desc())
            
            df = pd.read_sql(query.statement, session.bind)
            return df
    
    # ============================================================================
    # Analysis Operations
    # ============================================================================
    
    def insert_analysis(
        self,
        ticker: str,
        quarter: int,
        year: int,
        analysis_markdown: str,
        score: int,
        provider: str,
        analysis_type: str,
        transcript_id: Optional[int] = None,
        score_justification: Optional[str] = None,
        analysis_json: Optional[Dict] = None,
        model: Optional[str] = None,
        financial_context_included: bool = False,
        processing_time_seconds: Optional[float] = None
    ) -> int:
        """
        Insert a new analysis
        
        Returns:
            analysis_id: ID of inserted analysis
        """
        with self.get_session() as session:
            # If transcript_id not provided, try to find it
            if transcript_id is None:
                transcript = session.query(Transcript).filter_by(
                    ticker=ticker.upper(),
                    quarter=quarter,
                    year=year
                ).first()
                if transcript:
                    transcript_id = transcript.id
            
            analysis = Analysis(
                transcript_id=transcript_id,
                ticker=ticker.upper(),
                quarter=quarter,
                year=year,
                score=score,
                score_justification=score_justification,
                analysis_markdown=analysis_markdown,
                analysis_json=analysis_json,
                provider=provider,
                model=model,
                analysis_type=analysis_type,
                financial_context_included=financial_context_included,
                processing_time_seconds=processing_time_seconds
            )
            
            session.add(analysis)
            session.flush()
            return analysis.id
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict]:
        """
        Get analysis by ID
        """
        with self.get_session() as session:
            analysis = session.query(Analysis).filter_by(id=analysis_id).first()
            
            if analysis:
                return {
                    'id': analysis.id,
                    'transcript_id': analysis.transcript_id,
                    'ticker': analysis.ticker,
                    'quarter': analysis.quarter,
                    'year': analysis.year,
                    'analysis_date': analysis.analysis_date,
                    'score': analysis.score,
                    'score_justification': analysis.score_justification,
                    'analysis_markdown': analysis.analysis_markdown,
                    'analysis_json': analysis.analysis_json,
                    'provider': analysis.provider,
                    'model': analysis.model,
                    'analysis_type': analysis.analysis_type,
                    'created_at': analysis.created_at
                }
            return None
    
    def get_analyses_by_ticker(self, ticker: str) -> pd.DataFrame:
        """
        Get all analyses for a ticker
        """
        with self.get_session() as session:
            query = session.query(Analysis).filter(
                Analysis.ticker == ticker.upper()
            ).order_by(Analysis.analysis_date.desc())
            
            df = pd.read_sql(query.statement, session.bind)
            return df
    
    def get_latest_analysis(self, ticker: str) -> Optional[Dict]:
        """
        Get the most recent analysis for a ticker
        """
        with self.get_session() as session:
            analysis = session.query(Analysis).filter(
                Analysis.ticker == ticker.upper()
            ).order_by(Analysis.analysis_date.desc()).first()
            
            if analysis:
                return {
                    'id': analysis.id,
                    'ticker': analysis.ticker,
                    'quarter': analysis.quarter,
                    'year': analysis.year,
                    'score': analysis.score,
                    'analysis_date': analysis.analysis_date,
                    'provider': analysis.provider,
                    'model': analysis.model
                }
            return None
    
    def get_all_analyses(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get all analyses with optional limit
        """
        with self.get_session() as session:
            query = session.query(
                Analysis.id,
                Analysis.ticker,
                Analysis.quarter,
                Analysis.year,
                Analysis.analysis_date,
                Analysis.score,
                Analysis.provider,
                Analysis.model,
                Analysis.analysis_type
            ).order_by(Analysis.analysis_date.desc())
            
            if limit:
                query = query.limit(limit)
            
            df = pd.read_sql(query.statement, session.bind)
            return df
    
    # ============================================================================
    # Price Movement Operations
    # ============================================================================
    
    def insert_price_movement(
        self,
        ticker: str,
        earnings_date: date,
        price_before: float,
        price_after_1d: Optional[float] = None,
        price_after_3d: Optional[float] = None,
        price_after_5d: Optional[float] = None,
        price_after_10d: Optional[float] = None,
        volume_before: Optional[int] = None,
        volume_after_1d: Optional[int] = None,
        data_source: str = 'yfinance'
    ) -> int:
        """
        Insert or update price movement data
        
        Returns:
            price_movement_id
        """
        with self.get_session() as session:
            # Calculate percentage movements
            movement_1d = ((price_after_1d - price_before) / price_before * 100) if price_after_1d else None
            movement_3d = ((price_after_3d - price_before) / price_before * 100) if price_after_3d else None
            movement_5d = ((price_after_5d - price_before) / price_before * 100) if price_after_5d else None
            movement_10d = ((price_after_10d - price_before) / price_before * 100) if price_after_10d else None
            
            # Check if exists
            existing = session.query(PriceMovement).filter_by(
                ticker=ticker.upper(),
                earnings_date=earnings_date
            ).first()
            
            if existing:
                # Update
                existing.price_before = price_before
                existing.price_after_1d = price_after_1d
                existing.price_after_3d = price_after_3d
                existing.price_after_5d = price_after_5d
                existing.price_after_10d = price_after_10d
                existing.movement_1d_pct = movement_1d
                existing.movement_3d_pct = movement_3d
                existing.movement_5d_pct = movement_5d
                existing.movement_10d_pct = movement_10d
                existing.volume_before = volume_before
                existing.volume_after_1d = volume_after_1d
                existing.data_source = data_source
                session.flush()
                return existing.id
            else:
                # Insert
                price_movement = PriceMovement(
                    ticker=ticker.upper(),
                    earnings_date=earnings_date,
                    price_before=price_before,
                    price_after_1d=price_after_1d,
                    price_after_3d=price_after_3d,
                    price_after_5d=price_after_5d,
                    price_after_10d=price_after_10d,
                    movement_1d_pct=movement_1d,
                    movement_3d_pct=movement_3d,
                    movement_5d_pct=movement_5d,
                    movement_10d_pct=movement_10d,
                    volume_before=volume_before,
                    volume_after_1d=volume_after_1d,
                    data_source=data_source
                )
                session.add(price_movement)
                session.flush()
                return price_movement.id
    
    # ============================================================================
    # Correlation and Analysis Operations
    # ============================================================================
    
    def get_analysis_performance(self, ticker: Optional[str] = None) -> pd.DataFrame:
        """
        Get analysis performance (scores vs actual price movements)
        Uses the analysis_performance view
        """
        with self.get_session() as session:
            query = "SELECT * FROM earnings.analysis_performance"
            
            if ticker:
                query += f" WHERE ticker = '{ticker.upper()}'"
            
            query += " ORDER BY analysis_date DESC"
            
            df = pd.read_sql(text(query), session.bind)
            return df
    
    def calculate_correlation(
        self,
        ticker: Optional[str] = None,
        period_days: int = 5
    ) -> Tuple[float, int]:
        """
        Calculate correlation between scores and price movements
        
        Returns:
            (correlation_coefficient, sample_size)
        """
        df = self.get_analysis_performance(ticker)
        
        movement_col = f'movement_{period_days}d_pct'
        
        if movement_col not in df.columns:
            return 0.0, 0
        
        # Filter out null values
        df_clean = df[df[movement_col].notna() & df['score'].notna()]
        
        if len(df_clean) < 2:
            return 0.0, len(df_clean)
        
        correlation = df_clean['score'].corr(df_clean[movement_col])
        
        return float(correlation), len(df_clean)
    
    def get_all_tickers(self) -> List[str]:
        """
        Get list of all unique tickers in database
        """
        with self.get_session() as session:
            tickers = session.query(Analysis.ticker).distinct().order_by(Analysis.ticker).all()
            return [t[0] for t in tickers]
    
    # ============================================================================
    # Utility Methods
    # ============================================================================
    
    def execute_raw_sql(self, sql: str) -> pd.DataFrame:
        """
        Execute raw SQL query and return DataFrame
        """
        with self.get_session() as session:
            return pd.read_sql(text(sql), session.bind)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        """
        with self.get_session() as session:
            stats = {
                'transcripts_count': session.query(func.count(Transcript.id)).scalar(),
                'analyses_count': session.query(func.count(Analysis.id)).scalar(),
                'price_movements_count': session.query(func.count(PriceMovement.id)).scalar(),
                'unique_tickers': session.query(func.count(func.distinct(Analysis.ticker))).scalar(),
                'latest_analysis': session.query(func.max(Analysis.analysis_date)).scalar(),
                'earliest_transcript': session.query(func.min(Transcript.transcript_date)).scalar()
            }
            return stats
