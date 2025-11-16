# PostgreSQL Database Documentation

## Overview

The Earnings Call Analyzer uses **PostgreSQL** as its primary database for storing transcripts, analyses, price movements, and correlations. The database is hosted on **Render.com** and uses **SQLAlchemy ORM** for all operations.

## Database Connection

**Host:** `dpg-d40gneur433s738clpeg-a.frankfurt-postgres.render.com`  
**Database:** `indurent_db`  
**Schema:** `earnings`  
**User:** `indurent_db_user`

Connection string is stored in environment variable:
```bash
DB_URL=postgresql://user:password@host:port/database
```

## Database Schema

### Tables

#### 1. `earnings.transcripts`
Stores raw earnings call transcripts.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `ticker` | VARCHAR(10) | Stock ticker symbol |
| `company_name` | VARCHAR(255) | Company name |
| `quarter` | INTEGER | Quarter (1-4) |
| `year` | INTEGER | Year (2000-2100) |
| `transcript_date` | DATE | Date of earnings call |
| `transcript_text` | TEXT | Full transcript content |
| `source` | VARCHAR(50) | Data source (api_ninjas, finnhub, manual_upload) |
| `source_metadata` | JSONB | Additional metadata from source |
| `word_count` | INTEGER | Number of words in transcript |
| `created_at` | TIMESTAMP WITH TIME ZONE | Record creation time |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Last update time |

**Constraints:**
- Unique: `(ticker, quarter, year)`
- Check: `quarter BETWEEN 1 AND 4`
- Check: `year BETWEEN 2000 AND 2100`

**Indexes:**
- `idx_transcripts_ticker`
- `idx_transcripts_date`
- `idx_transcripts_ticker_quarter_year`

#### 2. `earnings.analyses`
Stores LLM-generated analyses of transcripts.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `transcript_id` | INTEGER | Foreign key to transcripts |
| `ticker` | VARCHAR(10) | Stock ticker symbol |
| `quarter` | INTEGER | Quarter (1-4) |
| `year` | INTEGER | Year (2000-2100) |
| `analysis_date` | TIMESTAMP WITH TIME ZONE | When analysis was performed |
| `score` | INTEGER | Price movement score (-5 to +5) |
| `score_justification` | TEXT | Explanation of score |
| `analysis_markdown` | TEXT | Full analysis in markdown |
| `analysis_json` | JSONB | Structured analysis data |
| `provider` | VARCHAR(50) | LLM provider (openai, xai, gemini) |
| `model` | VARCHAR(100) | Model name (gpt-4.1-mini, grok-3, etc.) |
| `analysis_type` | VARCHAR(50) | Type (Standard Analysis, Agentic Workflow) |
| `financial_context_included` | BOOLEAN | Whether financial data was included |
| `processing_time_seconds` | REAL | Time taken to generate analysis |
| `created_at` | TIMESTAMP WITH TIME ZONE | Record creation time |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Last update time |

**Constraints:**
- Check: `quarter BETWEEN 1 AND 4`
- Check: `year BETWEEN 2000 AND 2100`
- Check: `score BETWEEN -5 AND 5`
- Foreign key: `transcript_id` → `earnings.transcripts(id)` ON DELETE CASCADE

**Indexes:**
- `idx_analyses_ticker`
- `idx_analyses_transcript_id`
- `idx_analyses_date`
- `idx_analyses_score`
- `idx_analyses_ticker_quarter_year`

#### 3. `earnings.price_movements`
Stores actual stock price movements after earnings.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `ticker` | VARCHAR(10) | Stock ticker symbol |
| `earnings_date` | DATE | Date of earnings announcement |
| `price_before` | NUMERIC(10,2) | Price before earnings |
| `price_after_1d` | NUMERIC(10,2) | Price 1 day after |
| `price_after_3d` | NUMERIC(10,2) | Price 3 days after |
| `price_after_5d` | NUMERIC(10,2) | Price 5 days after |
| `price_after_10d` | NUMERIC(10,2) | Price 10 days after |
| `movement_1d_pct` | NUMERIC(6,2) | 1-day movement percentage |
| `movement_3d_pct` | NUMERIC(6,2) | 3-day movement percentage |
| `movement_5d_pct` | NUMERIC(6,2) | 5-day movement percentage |
| `movement_10d_pct` | NUMERIC(6,2) | 10-day movement percentage |
| `volume_before` | BIGINT | Volume before earnings |
| `volume_after_1d` | BIGINT | Volume 1 day after |
| `data_source` | VARCHAR(50) | Data source (default: yfinance) |
| `created_at` | TIMESTAMP WITH TIME ZONE | Record creation time |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Last update time |

**Constraints:**
- Unique: `(ticker, earnings_date)`

**Indexes:**
- `idx_price_movements_ticker`
- `idx_price_movements_date`

#### 4. `earnings.correlations`
Stores correlation analysis results.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `ticker` | VARCHAR(10) | Stock ticker (NULL for all tickers) |
| `period_days` | INTEGER | Period for correlation (1, 3, 5, 10) |
| `correlation_coefficient` | NUMERIC(5,3) | Pearson correlation coefficient |
| `sample_size` | INTEGER | Number of data points |
| `mean_absolute_error` | NUMERIC(6,2) | MAE of predictions |
| `r_squared` | NUMERIC(5,3) | R-squared value |
| `direction_accuracy` | NUMERIC(5,2) | Percentage of correct directions |
| `analysis_date` | DATE | Date of correlation analysis |
| `created_at` | TIMESTAMP WITH TIME ZONE | Record creation time |

**Constraints:**
- Unique: `(ticker, period_days, analysis_date)`
- Check: `period_days > 0`

**Indexes:**
- `idx_correlations_ticker`
- `idx_correlations_date`

### Views

#### 1. `earnings.analysis_performance`
Combines analyses with actual price movements for performance evaluation.

```sql
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
    -- Direction correctness
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
LEFT JOIN earnings.price_movements pm 
    ON a.ticker = pm.ticker 
    AND DATE(a.analysis_date) = pm.earnings_date;
```

#### 2. `earnings.latest_analyses`
Shows the most recent analysis for each ticker.

```sql
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
```

#### 3. `earnings.transcript_summary`
Provides summary statistics for each transcript.

```sql
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
GROUP BY t.id, t.ticker, t.company_name, t.quarter, 
         t.year, t.transcript_date, t.source, t.word_count;
```

### Functions and Triggers

#### `earnings.update_updated_at_column()`
Automatically updates the `updated_at` timestamp when a record is modified.

**Triggers:**
- `update_transcripts_updated_at` on `earnings.transcripts`
- `update_analyses_updated_at` on `earnings.analyses`
- `update_price_movements_updated_at` on `earnings.price_movements`

## Python API (SQLAlchemy)

### Database Class

Located in `utils/database.py`, provides high-level interface to database operations.

#### Initialization

```python
from utils.database import Database

# Uses DB_URL from environment
db = Database()

# Or provide URL explicitly
db = Database(db_url="postgresql://...")
```

#### Transcript Operations

```python
# Insert transcript
transcript_id = db.insert_transcript(
    ticker="AAPL",
    quarter=3,
    year=2024,
    transcript_date=date(2024, 7, 31),
    transcript_text="...",
    source="api_ninjas",
    company_name="Apple Inc."
)

# Get transcript
transcript = db.get_transcript("AAPL", 3, 2024)

# Get all transcripts (returns DataFrame)
df = db.get_all_transcripts(ticker="AAPL")
```

#### Analysis Operations

```python
# Insert analysis
analysis_id = db.insert_analysis(
    ticker="AAPL",
    quarter=3,
    year=2024,
    analysis_markdown="...",
    score=3,
    score_justification="...",
    provider="openai",
    model="gpt-4.1-mini",
    analysis_type="Standard Analysis",
    transcript_id=transcript_id
)

# Get analysis
analysis = db.get_analysis(analysis_id)

# Get analyses by ticker
df = db.get_analyses_by_ticker("AAPL")

# Get latest analysis
latest = db.get_latest_analysis("AAPL")

# Get all analyses
df = db.get_all_analyses(limit=100)
```

#### Price Movement Operations

```python
# Insert price movement
price_id = db.insert_price_movement(
    ticker="AAPL",
    earnings_date=date(2024, 7, 31),
    price_before=225.00,
    price_after_1d=230.50,
    price_after_5d=235.00
)
```

#### Analysis Performance

```python
# Get analysis performance (scores vs actual movements)
df = db.get_analysis_performance(ticker="AAPL")

# Calculate correlation
correlation, sample_size = db.calculate_correlation("AAPL", period_days=5)

# Get all tickers
tickers = db.get_all_tickers()

# Get database statistics
stats = db.get_database_stats()
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install psycopg2-binary sqlalchemy pandas
```

### 2. Set Environment Variable

Add to `.env` file:
```bash
DB_URL=postgresql://indurent_db_user:password@host/indurent_db
```

### 3. Initialize Database

```bash
python3 init_database.py
```

This will:
- Create the `earnings` schema
- Create all tables with indexes
- Create views and functions
- Set up triggers

### 4. Run SQL Initialization (for views/functions)

```bash
python3 run_sql_init.py
```

### 5. Test Database

```bash
python3 test_postgres_database.py
```

## Migration from SQLite

The application previously used SQLite (`data/earnings.db`). The PostgreSQL schema is designed to be compatible with the existing data model while adding:

1. **Better data types** (JSONB for metadata, proper TIMESTAMP WITH TIME ZONE)
2. **Foreign key constraints** (CASCADE delete)
3. **Views** for common queries
4. **Triggers** for automatic timestamp updates
5. **Proper indexing** for performance

### Migration Steps

1. Export data from SQLite
2. Transform to PostgreSQL format
3. Import using `Database` class methods

## Performance Considerations

### Indexes

All frequently queried columns are indexed:
- Tickers
- Dates
- Scores
- Foreign keys

### Connection Pooling

SQLAlchemy engine uses connection pooling:
- Pool size: 10
- Max overflow: 20
- Pre-ping enabled for connection health checks

### Query Optimization

Use views for complex queries:
- `analysis_performance` - Pre-joined analysis and price data
- `latest_analyses` - Most recent analysis per ticker
- `transcript_summary` - Aggregated transcript statistics

## Backup and Maintenance

### Backup

Render.com provides automatic daily backups. Manual backup:

```bash
pg_dump -h host -U user -d indurent_db -n earnings > backup.sql
```

### Restore

```bash
psql -h host -U user -d indurent_db < backup.sql
```

### Monitoring

Check database statistics:

```python
db = Database()
stats = db.get_database_stats()
print(stats)
```

## Security

1. **Connection string** stored in environment variable (not in code)
2. **Schema isolation** - All tables in `earnings` schema
3. **User permissions** - Granted only to `indurent_db_user`
4. **SSL connection** - Render.com enforces SSL by default

## Troubleshooting

### Connection Issues

```python
# Test connection
from utils.database import Database
db = Database()
stats = db.get_database_stats()
```

### View Not Found

Run SQL initialization:
```bash
python3 run_sql_init.py
```

### Constraint Violations

Check unique constraints:
- Transcripts: `(ticker, quarter, year)`
- Price movements: `(ticker, earnings_date)`
- Correlations: `(ticker, period_days, analysis_date)`

## Future Enhancements

1. **Partitioning** - Partition tables by year for better performance
2. **Materialized views** - Cache expensive aggregations
3. **Full-text search** - Add text search on transcripts
4. **Time-series data** - Add TimescaleDB extension for price data
5. **Replication** - Set up read replicas for analytics queries

## References

- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Render PostgreSQL**: https://render.com/docs/databases
