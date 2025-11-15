"""
SQLAlchemy Models for Earnings Call Analyzer
Database: PostgreSQL
Schema: earnings
"""

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, Boolean, BigInteger, ForeignKey, CheckConstraint, UniqueConstraint, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Transcript(Base):
    """
    Stores raw earnings call transcripts
    """
    __tablename__ = 'transcripts'
    __table_args__ = (
        UniqueConstraint('ticker', 'quarter', 'year', name='uq_transcript_ticker_quarter_year'),
        CheckConstraint('quarter >= 1 AND quarter <= 4', name='ck_transcript_quarter'),
        CheckConstraint('year >= 2000 AND year <= 2100', name='ck_transcript_year'),
        {'schema': 'earnings'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255))
    quarter = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    transcript_date = Column(Date, nullable=False, index=True)
    transcript_text = Column(Text, nullable=False)
    source = Column(String(50), nullable=False)  # 'api_ninjas', 'finnhub', 'manual_upload'
    source_metadata = Column(JSONB)
    word_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    analyses = relationship("Analysis", back_populates="transcript", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Transcript(ticker='{self.ticker}', Q{self.quarter} {self.year})>"


class Analysis(Base):
    """
    Stores LLM-generated analyses of transcripts
    """
    __tablename__ = 'analyses'
    __table_args__ = (
        CheckConstraint('quarter >= 1 AND quarter <= 4', name='ck_analysis_quarter'),
        CheckConstraint('year >= 2000 AND year <= 2100', name='ck_analysis_year'),
        CheckConstraint('score >= -5 AND score <= 5', name='ck_analysis_score'),
        {'schema': 'earnings'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transcript_id = Column(Integer, ForeignKey('earnings.transcripts.id', ondelete='CASCADE'), index=True)
    ticker = Column(String(10), nullable=False, index=True)
    quarter = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    score = Column(Integer, index=True)
    score_justification = Column(Text)
    analysis_markdown = Column(Text, nullable=False)
    analysis_json = Column(JSONB)
    provider = Column(String(50), nullable=False)  # 'openai', 'xai', 'gemini'
    model = Column(String(100))  # 'gpt-4.1-mini', 'grok-3', etc.
    analysis_type = Column(String(50), nullable=False)  # 'Standard Analysis', 'Agentic Workflow'
    financial_context_included = Column(Boolean, default=False)
    processing_time_seconds = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    transcript = relationship("Transcript", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis(ticker='{self.ticker}', Q{self.quarter} {self.year}, score={self.score})>"


class PriceMovement(Base):
    """
    Stores actual stock price movements after earnings
    """
    __tablename__ = 'price_movements'
    __table_args__ = (
        UniqueConstraint('ticker', 'earnings_date', name='uq_price_movement_ticker_date'),
        {'schema': 'earnings'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    earnings_date = Column(Date, nullable=False, index=True)
    price_before = Column(Numeric(10, 2))
    price_after_1d = Column(Numeric(10, 2))
    price_after_3d = Column(Numeric(10, 2))
    price_after_5d = Column(Numeric(10, 2))
    price_after_10d = Column(Numeric(10, 2))
    movement_1d_pct = Column(Numeric(6, 2))
    movement_3d_pct = Column(Numeric(6, 2))
    movement_5d_pct = Column(Numeric(6, 2))
    movement_10d_pct = Column(Numeric(6, 2))
    volume_before = Column(BigInteger)
    volume_after_1d = Column(BigInteger)
    data_source = Column(String(50), default='yfinance')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<PriceMovement(ticker='{self.ticker}', date={self.earnings_date})>"


class Correlation(Base):
    """
    Stores correlation analysis results
    """
    __tablename__ = 'correlations'
    __table_args__ = (
        UniqueConstraint('ticker', 'period_days', 'analysis_date', name='uq_correlation_ticker_period_date'),
        CheckConstraint('period_days > 0', name='ck_correlation_period'),
        {'schema': 'earnings'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), index=True)
    period_days = Column(Integer, nullable=False)
    correlation_coefficient = Column(Numeric(5, 3))
    sample_size = Column(Integer)
    mean_absolute_error = Column(Numeric(6, 2))
    r_squared = Column(Numeric(5, 3))
    direction_accuracy = Column(Numeric(5, 2))  # Percentage
    analysis_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Correlation(ticker='{self.ticker}', period={self.period_days}d, corr={self.correlation_coefficient})>"
