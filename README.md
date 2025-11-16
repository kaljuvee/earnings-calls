# Earnings Call Analyzer

AI-powered earnings call transcript analysis with LLM-based insights and price movement predictions.

## Features

- 📥 **Download Transcripts** - Fetch earnings call transcripts from API Ninjas and Finnhub
- 🤖 **AI Analysis** - LLM-powered analysis with scoring (-5 to +5) and justification
- 📊 **Financial Correlation** - Compare predictions with actual price movements
- 🔍 **View Results** - Browse and search all analyses
- 💾 **PostgreSQL Database** - Production-ready data storage
- 📈 **Batch Processing** - Analyze multiple transcripts at once

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.sample` to `.env` and add your API keys:

```bash
# LLM Providers
XAI_API_KEY=your_xai_api_key_here
GROK_MODEL=grok-3
GOOGLE_API_KEY=your_google_api_key_here

# Financial Data APIs
API_NINJAS_KEY=your_api_ninjas_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here

# PostgreSQL Database
DB_URL=postgresql://user:password@host:port/database
```

### 3. Initialize Database

```bash
python3 init_database.py
python3 run_sql_init.py
```

### 4. Run Application

```bash
streamlit run Home.py
```

## Project Structure

```
earnings-calls/
├── Home.py                 # Main Streamlit application
├── pages/                  # Streamlit pages
│   ├── 0_Download_Transcripts.py
│   ├── 1_Analyze_Transcripts.py
│   ├── 2_Financial_Correlation.py
│   ├── 3_View_Results.py
│   └── 4_Correlations.py
├── utils/                  # Utility modules
│   ├── database.py         # PostgreSQL database operations
│   ├── models.py           # SQLAlchemy ORM models
│   ├── llm_client.py       # LLM integration (OpenAI, XAI, Gemini)
│   ├── api_ninjas_client.py
│   ├── finnhub_client.py
│   ├── yfinance_client.py
│   ├── score_extractor.py
│   └── db_util.py          # SQLite utilities (legacy)
├── prompts/                # LLM prompt templates
│   └── analysis_prompt.py
├── sql/                    # Database schemas
│   ├── init_postgres.sql   # PostgreSQL schema
│   └── create_tables.sql   # SQLite schema (legacy)
├── tasks/                  # Batch processing tasks
│   └── run_batch_analysis.py
├── tests/                  # Test files
│   ├── test_postgres_database.py
│   ├── test_llm_analysis.py
│   └── ...
├── docs/                   # Documentation
│   ├── POSTGRES_DATABASE.md
│   ├── USER_GUIDE.md
│   ├── DEPLOYMENT.md
│   └── ...
├── media/                  # Screenshots and sample files
├── transcripts/            # Downloaded transcripts
├── analyses/               # Generated analyses
└── data/                   # SQLite database (legacy)
```

## API Keys

### Required

- **API Ninjas** (Free tier) - Earnings call transcripts for S&P 100
  - Sign up: https://api-ninjas.com/register
  - 10,000 requests/month free

### Optional

- **XAI** - Grok models for analysis
- **Google AI** - Gemini models for analysis
- **OpenAI** - GPT models (pre-configured in environment)
- **Finnhub** - Additional financial data (premium for transcripts)

## Database

The application uses **PostgreSQL** for production storage:

- **Schema:** `earnings`
- **Tables:** `transcripts`, `analyses`, `price_movements`, `correlations`
- **Views:** `analysis_performance`, `latest_analyses`, `transcript_summary`

See `docs/POSTGRES_DATABASE.md` for complete documentation.

## Scoring System

Analyses include a **-5 to +5 score** predicting price movement:

| Score | Label | Expected Movement |
|-------|-------|-------------------|
| +5 | Very Bullish | +10% to +15% |
| +4 | Bullish | +7% to +10% |
| +3 | Bullish | +4% to +7% |
| +2 | Moderately Bullish | +2% to +4% |
| +1 | Slightly Bullish | +1% to +2% |
| 0 | Neutral | -1% to +1% |
| -1 | Slightly Bearish | -2% to -1% |
| -2 | Moderately Bearish | -4% to -2% |
| -3 | Bearish | -7% to -4% |
| -4 | Bearish | -10% to -7% |
| -5 | Very Bearish | -15% to -10% |

See `docs/SCORING_SYSTEM.md` for scoring criteria.

## Batch Processing

Process multiple transcripts at once:

```bash
# Analyze all Mag 7 stocks for 2024
python3 tasks/run_batch_analysis.py
```

This will:
1. Download transcripts for AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA
2. Analyze each transcript with LLM
3. Store results in PostgreSQL database
4. Generate summary report

## Documentation

- **User Guide** - `docs/USER_GUIDE.md`
- **Database** - `docs/POSTGRES_DATABASE.md`
- **Deployment** - `docs/DEPLOYMENT.md`
- **Scoring System** - `docs/SCORING_SYSTEM.md`
- **Transcript Sources** - `docs/TRANSCRIPT_SOURCES.md`

## Testing

Run tests:

```bash
# Test database
python3 tests/test_postgres_database.py

# Test LLM analysis
python3 tests/test_llm_analysis.py

# Test transcript download
python3 tests/test_transcript_download.py
```

## Deployment

### Streamlit Cloud

1. Push to GitHub
2. Connect repository at https://share.streamlit.io
3. Add secrets in Streamlit Cloud dashboard
4. Deploy

See `docs/DEPLOYMENT.md` for detailed instructions.

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions:
- GitHub Issues: https://github.com/kaljuvee/earnings-calls/issues
- Documentation: See `docs/` directory
