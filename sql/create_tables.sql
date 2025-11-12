-- Earnings Call Analysis Scores Database Schema
-- SQLite database for tracking analysis scores and correlating with price movements

-- Main scores table
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    earnings_date DATE NOT NULL,
    analysis_timestamp DATETIME NOT NULL,
    score INTEGER NOT NULL CHECK(score >= -5 AND score <= 5),
    score_justification TEXT,
    provider TEXT NOT NULL,
    model TEXT,
    analysis_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, quarter, year, analysis_timestamp)
);

-- Price movements table
CREATE TABLE IF NOT EXISTS price_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    earnings_date DATE NOT NULL,
    price_before REAL,
    price_after_1d REAL,
    price_after_3d REAL,
    price_after_5d REAL,
    price_after_10d REAL,
    movement_1d_pct REAL,
    movement_3d_pct REAL,
    movement_5d_pct REAL,
    movement_10d_pct REAL,
    volume_before INTEGER,
    volume_after_1d INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, earnings_date)
);

-- Correlation analysis table
CREATE TABLE IF NOT EXISTS correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    period_days INTEGER NOT NULL,
    correlation_coefficient REAL,
    sample_size INTEGER,
    mean_absolute_error REAL,
    r_squared REAL,
    analysis_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, period_days, analysis_date)
);

-- Analysis metadata table
CREATE TABLE IF NOT EXISTS analysis_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    company_name TEXT,
    analysis_file_path TEXT,
    json_file_path TEXT,
    financial_context_included BOOLEAN,
    predictions_included BOOLEAN,
    analysis_length INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker, quarter, year) REFERENCES scores(ticker, quarter, year)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_scores_ticker ON scores(ticker);
CREATE INDEX IF NOT EXISTS idx_scores_date ON scores(earnings_date);
CREATE INDEX IF NOT EXISTS idx_scores_ticker_date ON scores(ticker, earnings_date);
CREATE INDEX IF NOT EXISTS idx_price_movements_ticker ON price_movements(ticker);
CREATE INDEX IF NOT EXISTS idx_price_movements_date ON price_movements(earnings_date);
CREATE INDEX IF NOT EXISTS idx_correlations_ticker ON correlations(ticker);
CREATE INDEX IF NOT EXISTS idx_analysis_metadata_ticker ON analysis_metadata(ticker);

-- View for easy score-price correlation queries
CREATE VIEW IF NOT EXISTS score_price_correlation AS
SELECT 
    s.ticker,
    s.quarter,
    s.year,
    s.earnings_date,
    s.score,
    s.score_justification,
    s.provider,
    s.model,
    pm.price_before,
    pm.price_after_1d,
    pm.price_after_3d,
    pm.price_after_5d,
    pm.price_after_10d,
    pm.movement_1d_pct,
    pm.movement_3d_pct,
    pm.movement_5d_pct,
    pm.movement_10d_pct,
    s.created_at
FROM scores s
LEFT JOIN price_movements pm ON s.ticker = pm.ticker AND s.earnings_date = pm.earnings_date
ORDER BY s.earnings_date DESC;
