-- PostgreSQL Schema Initialization for Earnings Call Analyzer
-- Schema: earnings
-- Database: indurent_db

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS earnings;

-- Set search path
SET search_path TO earnings, public;

-- ============================================================================
-- Table: transcripts
-- Stores raw earnings call transcripts
-- ============================================================================
CREATE TABLE IF NOT EXISTS earnings.transcripts (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255),
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year INTEGER NOT NULL CHECK (year >= 2000 AND year <= 2100),
    transcript_date DATE NOT NULL,
    transcript_text TEXT NOT NULL,
    source VARCHAR(50) NOT NULL, -- 'api_ninjas', 'finnhub', 'manual_upload', etc.
    source_metadata JSONB, -- Additional metadata from source
    word_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, quarter, year)
);

-- ============================================================================
-- Table: analyses
-- Stores LLM-generated analyses of transcripts
-- ============================================================================
CREATE TABLE IF NOT EXISTS earnings.analyses (
    id SERIAL PRIMARY KEY,
    transcript_id INTEGER REFERENCES earnings.transcripts(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year INTEGER NOT NULL CHECK (year >= 2000 AND year <= 2100),
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    score INTEGER CHECK (score >= -5 AND score <= 5),
    score_justification TEXT,
    analysis_markdown TEXT NOT NULL,
    analysis_json JSONB, -- Full analysis in structured format
    provider VARCHAR(50) NOT NULL, -- 'openai', 'xai', 'gemini'
    model VARCHAR(100), -- 'gpt-4.1-mini', 'grok-3', etc.
    analysis_type VARCHAR(50) NOT NULL, -- 'Standard Analysis', 'Agentic Workflow', 'Quick Summary'
    financial_context_included BOOLEAN DEFAULT FALSE,
    processing_time_seconds REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Table: price_movements
-- Stores actual stock price movements after earnings
-- ============================================================================
CREATE TABLE IF NOT EXISTS earnings.price_movements (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    earnings_date DATE NOT NULL,
    price_before NUMERIC(10, 2),
    price_after_1d NUMERIC(10, 2),
    price_after_3d NUMERIC(10, 2),
    price_after_5d NUMERIC(10, 2),
    price_after_10d NUMERIC(10, 2),
    movement_1d_pct NUMERIC(6, 2),
    movement_3d_pct NUMERIC(6, 2),
    movement_5d_pct NUMERIC(6, 2),
    movement_10d_pct NUMERIC(6, 2),
    volume_before BIGINT,
    volume_after_1d BIGINT,
    data_source VARCHAR(50) DEFAULT 'yfinance',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, earnings_date)
);

-- ============================================================================
-- Table: correlations
-- Stores correlation analysis results
-- ============================================================================
CREATE TABLE IF NOT EXISTS earnings.correlations (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10),
    period_days INTEGER NOT NULL CHECK (period_days > 0),
    correlation_coefficient NUMERIC(5, 3),
    sample_size INTEGER,
    mean_absolute_error NUMERIC(6, 2),
    r_squared NUMERIC(5, 3),
    direction_accuracy NUMERIC(5, 2), -- Percentage
    analysis_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, period_days, analysis_date)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Transcripts indexes
CREATE INDEX IF NOT EXISTS idx_transcripts_ticker ON earnings.transcripts(ticker);
CREATE INDEX IF NOT EXISTS idx_transcripts_date ON earnings.transcripts(transcript_date);
CREATE INDEX IF NOT EXISTS idx_transcripts_ticker_quarter_year ON earnings.transcripts(ticker, quarter, year);

-- Analyses indexes
CREATE INDEX IF NOT EXISTS idx_analyses_ticker ON earnings.analyses(ticker);
CREATE INDEX IF NOT EXISTS idx_analyses_transcript_id ON earnings.analyses(transcript_id);
CREATE INDEX IF NOT EXISTS idx_analyses_date ON earnings.analyses(analysis_date);
CREATE INDEX IF NOT EXISTS idx_analyses_score ON earnings.analyses(score);
CREATE INDEX IF NOT EXISTS idx_analyses_ticker_quarter_year ON earnings.analyses(ticker, quarter, year);

-- Price movements indexes
CREATE INDEX IF NOT EXISTS idx_price_movements_ticker ON earnings.price_movements(ticker);
CREATE INDEX IF NOT EXISTS idx_price_movements_date ON earnings.price_movements(earnings_date);

-- Correlations indexes
CREATE INDEX IF NOT EXISTS idx_correlations_ticker ON earnings.correlations(ticker);
CREATE INDEX IF NOT EXISTS idx_correlations_date ON earnings.correlations(analysis_date);

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- View: Analysis with price movement correlation
CREATE OR REPLACE VIEW earnings.analysis_performance AS
SELECT 
    a.id AS analysis_id,
    a.ticker,
    a.quarter,
    a.year,
    a.analysis_date,
    a.score,
    a.score_justification,
    a.provider,
    a.model,
    a.analysis_type,
    pm.earnings_date,
    pm.movement_1d_pct,
    pm.movement_3d_pct,
    pm.movement_5d_pct,
    pm.movement_10d_pct,
    -- Calculate if direction was correct
    CASE 
        WHEN a.score > 0 AND pm.movement_1d_pct > 0 THEN true
        WHEN a.score < 0 AND pm.movement_1d_pct < 0 THEN true
        WHEN a.score = 0 AND pm.movement_1d_pct BETWEEN -1 AND 1 THEN true
        ELSE false
    END AS direction_correct_1d,
    CASE 
        WHEN a.score > 0 AND pm.movement_5d_pct > 0 THEN true
        WHEN a.score < 0 AND pm.movement_5d_pct < 0 THEN true
        WHEN a.score = 0 AND pm.movement_5d_pct BETWEEN -1 AND 1 THEN true
        ELSE false
    END AS direction_correct_5d
FROM earnings.analyses a
LEFT JOIN earnings.price_movements pm ON a.ticker = pm.ticker 
    AND DATE(a.analysis_date) = pm.earnings_date;

-- View: Latest analysis per ticker
CREATE OR REPLACE VIEW earnings.latest_analyses AS
SELECT DISTINCT ON (ticker)
    id,
    transcript_id,
    ticker,
    quarter,
    year,
    analysis_date,
    score,
    score_justification,
    provider,
    model,
    analysis_type
FROM earnings.analyses
ORDER BY ticker, analysis_date DESC;

-- View: Transcript summary
CREATE OR REPLACE VIEW earnings.transcript_summary AS
SELECT 
    t.id,
    t.ticker,
    t.company_name,
    t.quarter,
    t.year,
    t.transcript_date,
    t.source,
    t.word_count,
    COUNT(a.id) AS analysis_count,
    MAX(a.analysis_date) AS latest_analysis_date,
    AVG(a.score) AS avg_score
FROM earnings.transcripts t
LEFT JOIN earnings.analyses a ON t.id = a.transcript_id
GROUP BY t.id, t.ticker, t.company_name, t.quarter, t.year, t.transcript_date, t.source, t.word_count;

-- ============================================================================
-- Functions
-- ============================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION earnings.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_transcripts_updated_at ON earnings.transcripts;
CREATE TRIGGER update_transcripts_updated_at
    BEFORE UPDATE ON earnings.transcripts
    FOR EACH ROW
    EXECUTE FUNCTION earnings.update_updated_at_column();

DROP TRIGGER IF EXISTS update_analyses_updated_at ON earnings.analyses;
CREATE TRIGGER update_analyses_updated_at
    BEFORE UPDATE ON earnings.analyses
    FOR EACH ROW
    EXECUTE FUNCTION earnings.update_updated_at_column();

DROP TRIGGER IF EXISTS update_price_movements_updated_at ON earnings.price_movements;
CREATE TRIGGER update_price_movements_updated_at
    BEFORE UPDATE ON earnings.price_movements
    FOR EACH ROW
    EXECUTE FUNCTION earnings.update_updated_at_column();

-- ============================================================================
-- Grants (adjust as needed for your user)
-- ============================================================================

GRANT USAGE ON SCHEMA earnings TO indurent_db_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA earnings TO indurent_db_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA earnings TO indurent_db_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA earnings TO indurent_db_user;

-- ============================================================================
-- Sample Queries for Testing
-- ============================================================================

-- Get all transcripts with analysis count
-- SELECT * FROM earnings.transcript_summary ORDER BY transcript_date DESC;

-- Get analysis performance
-- SELECT * FROM earnings.analysis_performance WHERE ticker = 'AAPL' ORDER BY analysis_date DESC;

-- Get latest analyses
-- SELECT * FROM earnings.latest_analyses ORDER BY analysis_date DESC;

-- Calculate correlation for a ticker
-- SELECT 
--     ticker,
--     CORR(score, movement_5d_pct) AS correlation,
--     COUNT(*) AS sample_size
-- FROM earnings.analysis_performance
-- WHERE ticker = 'AAPL' AND movement_5d_pct IS NOT NULL
-- GROUP BY ticker;
