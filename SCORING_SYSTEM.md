# Scoring System Documentation

## Overview

The Earnings Call Analyzer now includes a comprehensive **-5 to +5 scoring system** that predicts expected stock price movement following earnings calls. The system includes:

1. **Scoring Rules** embedded in the analysis prompt
2. **Automatic Score Extraction** from analysis text
3. **SQLite Database** for tracking scores over time
4. **Correlations Page** for analyzing score accuracy vs actual price movements

## Scoring Scale

### Score Range: -5 to +5

| Score | Label | Expected Movement | Criteria |
|-------|-------|-------------------|----------|
| **+5** | Very Bullish | >+10% | Exceptional results; significantly exceeded expectations across all metrics; raised guidance substantially; major positive strategic announcements |
| **+4** | Bullish | +7% to +10% | Very strong results; beat on most key metrics; positive guidance revision; strong growth drivers |
| **+3** | Bullish | +4% to +7% | Solid beat; exceeded expectations on key metrics; maintained or slightly raised guidance; positive momentum |
| **+2** | Slightly Bullish | +2% to +4% | Modest beat; met or slightly exceeded expectations; stable outlook; some positive signals |
| **+1** | Slightly Bullish | 0% to +2% | Mixed results with slight positive bias; met expectations; neutral guidance |
| **0** | Neutral | -1% to +1% | In-line results; met expectations across the board; no major surprises; neutral guidance |
| **-1** | Slightly Bearish | 0% to -2% | Slight miss or concerns; met most but missed on 1-2 key metrics; cautious guidance |
| **-2** | Bearish | -2% to -4% | Modest miss; missed expectations on several metrics; lowered guidance slightly; emerging concerns |
| **-3** | Bearish | -4% to -7% | Clear miss; significantly missed on key metrics; reduced guidance; multiple concerns; negative momentum |
| **-4** | Very Bearish | -7% to -10% | Major miss; missed badly on most metrics; cut guidance substantially; serious operational issues |
| **-5** | Very Bearish | <-10% | Catastrophic results; massive misses across all metrics; slashed guidance; existential concerns |

## Scoring Factors

The LLM considers these factors when assigning a score:

1. **Earnings Beat/Miss**: Magnitude of actual results vs analyst expectations
2. **Guidance Changes**: Raised, maintained, or lowered forward guidance
3. **Margin Trends**: Expanding or contracting profit margins
4. **Growth Momentum**: Acceleration or deceleration in key metrics
5. **Strategic Developments**: Major announcements, partnerships, or initiatives
6. **Management Tone**: Confidence level and forward-looking sentiment

## Database Schema

### Scores Table

```sql
CREATE TABLE scores (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    earnings_date DATE NOT NULL,
    analysis_timestamp DATETIME NOT NULL,
    score INTEGER CHECK(score >= -5 AND score <= 5),
    score_justification TEXT,
    provider TEXT NOT NULL,
    model TEXT,
    analysis_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Price Movements Table

```sql
CREATE TABLE price_movements (
    id INTEGER PRIMARY KEY,
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
    volume_after_1d INTEGER
);
```

### Correlations Table

```sql
CREATE TABLE correlations (
    id INTEGER PRIMARY KEY,
    ticker TEXT,
    period_days INTEGER NOT NULL,
    correlation_coefficient REAL,
    sample_size INTEGER,
    mean_absolute_error REAL,
    r_squared REAL,
    analysis_date DATE NOT NULL
);
```

## Usage

### 1. Running Analysis with Scoring

When you run an analysis on the **Analyze Transcripts** page:

1. The LLM generates a comprehensive analysis including a score
2. The score is automatically extracted from the analysis text
3. The score is displayed prominently with:
   - Score value (e.g., +3/5)
   - Label (e.g., "Bullish")
   - Expected movement range (e.g., "+4% to +7%")
4. The score is automatically saved to the SQLite database

### 2. Viewing Correlations

Navigate to the **Correlations** page (page 4) to:

- View scatter plots of scores vs actual price movements
- Analyze correlation coefficients
- See performance by score range
- Check direction accuracy
- Calculate mean absolute error
- Filter by ticker and time period (1, 3, 5, or 10 days)

### 3. Programmatic Access

```python
from utils.db_util import DatabaseUtil

# Initialize database
db = DatabaseUtil()

# Insert a score
db.insert_score(
    ticker="AAPL",
    quarter=3,
    year=2024,
    earnings_date=date(2024, 7, 31),
    score=3,
    score_justification="Solid beat with strong growth...",
    provider="openai",
    model="gpt-4.1-mini",
    analysis_type="Standard Analysis"
)

# Get scores for a ticker
df = db.get_scores_by_ticker("AAPL")

# Get score-price correlation data
df = db.get_score_price_correlation("AAPL")

# Calculate correlation
correlation, sample_size = db.calculate_correlation("AAPL", period_days=1)
```

## Score Extraction

The system uses regex pattern matching to extract scores from analysis text:

```python
from utils.score_extractor import extract_score_from_analysis

score, justification = extract_score_from_analysis(analysis_text)
```

**Pattern matched:** `**Score: [+/-]X/5**`

The extractor handles:
- Positive scores: `+3/5`
- Negative scores: `-2/5`
- Bracketed scores: `[+3]/5`
- Plain scores: `3/5`

## Analysis Output Format

The analysis now includes a dedicated scoring section:

```markdown
## 📊 𝗣𝗿𝗶𝗰𝗲 𝗠𝗼𝘃𝗲𝗺𝗲𝗻𝘁 𝗦𝗰𝗼𝗿𝗲

**Score: +3/5**

**Justification:**
Apple delivered a solid beat on revenue (+10% YoY) and EPS (+12%), 
with broad-based strength in iPhone, Mac, and Services setting new records. 
Despite tariff-related margin pressure, margins held up well...
```

## Correlation Analysis

### Metrics Tracked

1. **Correlation Coefficient**: Pearson correlation between scores and price movements
2. **Direction Accuracy**: Percentage of times the score correctly predicted direction (up/down)
3. **Mean Absolute Error**: Average absolute difference between expected and actual movements
4. **R-Squared**: Proportion of variance in price movements explained by scores

### Interpretation

- **Correlation > 0.5**: Strong positive correlation; scores are good predictors
- **Correlation 0.3-0.5**: Moderate correlation; some predictive power
- **Correlation 0-0.3**: Weak correlation; limited predictive power
- **Correlation < 0**: Negative correlation; model needs recalibration

### Direction Accuracy

- **>70%**: High accuracy; model reliably predicts direction
- **50-70%**: Moderate accuracy; better than random
- **<50%**: Low accuracy; model needs improvement

## Testing

Run the comprehensive test suite:

```bash
python3 test_scoring_system.py
```

This tests:
1. ✅ Analysis generation with scoring
2. ✅ Score extraction from analysis text
3. ✅ Database insertion
4. ✅ Database retrieval and verification
5. ✅ Correlation query functionality

## Files Added

### Core System
- `prompts/analysis_prompt.py` - Updated with scoring section
- `utils/score_extractor.py` - Score extraction utilities
- `utils/db_util.py` - Database operations
- `sql/create_tables.sql` - Database schema

### UI
- `pages/4_Correlations.py` - Correlations analysis page
- `pages/1_Analyze_Transcripts.py` - Updated with score display and DB saving

### Testing
- `test_scoring_system.py` - Comprehensive test suite

### Data
- `data/earnings_analysis.db` - SQLite database (gitignored)

## Future Enhancements

1. **Automatic Price Fetching**: Integrate with Yahoo Finance to automatically fetch price movements after earnings dates
2. **Model Calibration**: Use historical data to calibrate scoring thresholds
3. **Ensemble Scoring**: Combine scores from multiple LLM providers
4. **Confidence Intervals**: Add confidence ranges to score predictions
5. **Sector Adjustments**: Adjust scoring based on sector-specific volatility
6. **Backtesting**: Automated backtesting of historical analyses vs actual movements

## Example Workflow

1. **Download Transcript** (Page 0)
   - Search for AAPL Q3 2024
   - Download transcript

2. **Analyze Transcript** (Page 1)
   - Select OpenAI provider
   - Run Standard Analysis
   - View score: **+3/5** (Bullish, +4% to +7%)
   - Score automatically saved to database

3. **Add Price Data** (Programmatically or via future UI)
   ```python
   db.insert_price_movement(
       ticker="AAPL",
       earnings_date=date(2024, 7, 31),
       price_before=225.00,
       price_after_1d=230.50,  # +2.4%
       price_after_3d=232.75,  # +3.4%
       price_after_5d=235.00   # +4.4%
   )
   ```

4. **View Correlations** (Page 4)
   - Filter by AAPL
   - Select 5-day period
   - See actual movement (+4.4%) vs predicted (+4% to +7%)
   - View correlation metrics

## Benefits

1. **Quantifiable Predictions**: Converts qualitative analysis into actionable scores
2. **Historical Tracking**: Build database of predictions for model improvement
3. **Accuracy Measurement**: Objectively measure prediction accuracy over time
4. **Pattern Recognition**: Identify which factors correlate with price movements
5. **Model Comparison**: Compare accuracy across different LLM providers/models
6. **Continuous Improvement**: Use historical data to refine scoring rules
