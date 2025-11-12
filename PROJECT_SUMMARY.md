# Earnings Call Analyzer - Project Summary

## Executive Overview

The **Earnings Call Analyzer** is a comprehensive Streamlit-based MVP application that leverages AI to analyze earnings call transcripts and identify predictive signals for market movement. This proof-of-concept demonstrates how publicly available earnings data can be systematically analyzed to support investment research and decision-making.

---

## Project Objectives

### Primary Goals

1. **Automate Transcript Analysis** - Use AI to extract key insights from earnings call transcripts
2. **Correlate with Financial Data** - Compare analyst estimates with actual results
3. **Identify Predictive Signals** - Generate scores and signals for potential market movement
4. **Provide Actionable Insights** - Present analysis in a structured, easy-to-understand format

### Success Criteria

✅ **Functional MVP** - Complete working application with all core features
✅ **AI-Powered Analysis** - Integration with XAI and Gemini LLMs via LangChain
✅ **Data Correlation** - Yahoo Finance integration for financial data
✅ **User-Friendly Interface** - Intuitive Streamlit UI with multiple pages
✅ **Comprehensive Documentation** - README, User Guide, and Deployment Guide
✅ **Testing Framework** - Automated tests for core functionality

---

## Technical Architecture

### Technology Stack

**Frontend:**
- **Streamlit** - Web application framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation and analysis

**Backend:**
- **Python 3.11** - Core programming language
- **LangChain** - LLM orchestration framework
- **LangGraph** - Agentic workflow management

**AI/ML:**
- **XAI (Grok)** - Primary LLM for analysis
- **Google Gemini** - Alternative LLM option
- **OpenAI-compatible API** - Unified interface

**Data Sources:**
- **Financial Modeling Prep API** - Earnings call transcripts
- **Yahoo Finance (yfinance)** - Financial data and analyst estimates

**Development Tools:**
- **Git** - Version control
- **pytest** - Testing framework
- **python-dotenv** - Environment variable management

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │   Home   │ │ Download │ │ Analyze  │ │Financial │      │
│  │          │ │Transcripts│ │Transcripts│ │Correlation│     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  FMP Client  │  │  LLM Client  │  │YFinance Client│    │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  FMP API     │  │  XAI/Gemini  │  │Yahoo Finance │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
earnings-calls/
├── Home.py                          # Main application entry point
├── pages/                           # Streamlit pages
│   ├── 0_Download_Transcripts.py   # Transcript download interface
│   ├── 1_Analyze_Transcripts.py    # AI analysis interface
│   ├── 2_Financial_Correlation.py  # Financial data correlation
│   └── 3_View_Results.py           # Results browser
├── utils/                           # Core utilities
│   ├── fmp_client.py               # FMP API client
│   ├── yfinance_client.py          # Yahoo Finance client
│   ├── llm_client.py               # LLM integration with LangChain
│   └── data_correlator.py          # Data correlation logic
├── prompts/                         # LLM prompts
│   └── analysis_prompt.py          # Analysis template
├── tests/                           # Test suite
│   ├── test_fmp_client.py          # FMP client tests
│   ├── test_yfinance_client.py     # Yahoo Finance tests
│   └── run_all_tests.py            # Test runner
├── transcripts/                     # Downloaded transcripts
├── test-results/                    # Analysis results
├── requirements.txt                 # Python dependencies
├── .env.sample                      # Environment variable template
├── .gitignore                       # Git ignore rules
├── README.md                        # Project documentation
├── USER_GUIDE.md                    # User documentation
├── DEPLOYMENT.md                    # Deployment guide
└── PROJECT_SUMMARY.md              # This file
```

---

## Core Features

### 1. Transcript Download

**Functionality:**
- Search and download earnings call transcripts by ticker, quarter, and year
- Single transcript download with preview
- Bulk download for multiple tickers
- View all downloaded transcripts in a table
- Generate sample data for testing

**Data Source:**
- Financial Modeling Prep API
- Transcripts saved in both `.txt` and `.md` formats

**Key Files:**
- `pages/0_Download_Transcripts.py`
- `utils/fmp_client.py`

### 2. AI-Powered Analysis

**Functionality:**
- Single transcript analysis with customizable settings
- Batch analysis for multiple transcripts
- Multiple analysis types:
  - Standard Analysis (single-pass)
  - Agentic Workflow (multi-step with LangGraph)
  - Quick Summary
- Configurable options:
  - LLM provider selection (XAI or Gemini)
  - Sentiment analysis
  - Predictive signals
  - Financial context
  - Temperature control

**Analysis Output:**
- Bull Case - Positive arguments and growth metrics
- Bear Case - Concerns and risks
- Verdict - Balanced assessment
- Themes - Categorized by sentiment (positive, negative, neutral, emerging)
- Main Financials - Revenue, margins, key metrics with YoY comparisons
- Guidance - Forward-looking statements and changes
- Key Questions - Strategic questions for management

**Key Files:**
- `pages/1_Analyze_Transcripts.py`
- `utils/llm_client.py`
- `prompts/analysis_prompt.py`

### 3. Financial Correlation

**Functionality:**
- Single ticker analysis with comprehensive financial data
- Comparison dashboard for multiple tickers
- Earnings surprise analysis with historical data
- Interactive visualizations:
  - Candlestick price charts
  - Earnings surprise bar charts
  - Estimate vs actual line charts
  - Recommendation grade distribution

**Data Displayed:**
- Company overview (sector, industry, market cap)
- Analyst estimates (EPS and revenue)
- Analyst recommendations
- Price performance over configurable periods
- Earnings surprise metrics (beat rate, average surprise)

**Key Files:**
- `pages/2_Financial_Correlation.py`
- `utils/yfinance_client.py`
- `utils/data_correlator.py`

### 4. Results Management

**Functionality:**
- Browse all analysis results with filters
- Search across all results for specific keywords
- Compare two analyses side-by-side
- Results dashboard with statistics and charts
- Download results as files
- View JSON and Markdown results with formatting

**Filters:**
- By ticker symbol
- By year
- By file type (Markdown, JSON, All)
- Sort by date or ticker

**Key Files:**
- `pages/3_View_Results.py`

---

## AI Integration

### LangChain Implementation

**Core Components:**

1. **LLM Clients:**
   - `ChatOpenAI` for XAI (Grok) via OpenAI-compatible API
   - `ChatGoogleGenerativeAI` for Gemini
   - Unified interface for both providers

2. **Prompt Engineering:**
   - Structured prompt template in `prompts/analysis_prompt.py`
   - Clear instructions for consistent output format
   - Examples and formatting guidelines

3. **LangGraph Workflow:**
   - Multi-agent pipeline for comprehensive analysis
   - Sequential processing:
     - Main earnings analysis
     - Sentiment analysis
     - Predictive signal generation
     - Final report compilation
   - State management with `TypedDict`

### Analysis Template

The analysis follows a structured template designed to provide comprehensive, actionable insights:

```markdown
# {TICKER} Q{QUARTER} {YEAR} earnings: [One-line summary]

[Opening paragraph with key highlights]

## 🐂 The Bull Case
[Positive arguments, growth metrics, competitive advantages]

## 🐻 The Bear Case
[Concerns, risks, competitive threats]

## ⚖️ Verdict
[Balanced assessment with recommendation]

## Themes, Drivers, and Concerns
🟢 Positive Theme
🟡 Neutral/Mixed Theme
🔴 Negative Theme
⚪ New/Emerging Theme

## Main Financials (Q{QUARTER} {YEAR})
* Revenue: $X.X billion (up/down X% YoY)
* Operating margin: X%
* EPS: $X.XX
* Key metrics with YoY comparisons

## Guidance (Full Year {YEAR})
🟢 Raised guidance
🔴 Lowered guidance
⚪ Maintained guidance

## Main Questions for the Earnings Call
1. Strategic questions
2. Competitive dynamics
3. Financial sustainability
4. Execution risks
```

### Model Selection

**XAI (Grok) - Default:**
- Model: `grok-beta` via OpenAI-compatible API
- Good balance of speed and quality
- Larger context window for long transcripts

**Google Gemini - Alternative:**
- Model: `gemini-2.5-flash`
- Fast inference
- Alternative perspective on analysis

---

## Data Sources and APIs

### Financial Modeling Prep (FMP)

**Purpose:** Earnings call transcript retrieval

**Endpoints Used:**
- `/v3/earning_call_transcript/{ticker}` - Get transcript by ticker, quarter, year
- `/v3/profile/{ticker}` - Get company profile

**Rate Limits:**
- Free tier: 250 API calls/day
- Paid tier: Higher limits available

**Data Format:**
- JSON response with transcript content
- Metadata: date, quarter, year, ticker

### Yahoo Finance (yfinance)

**Purpose:** Financial data and analyst estimates

**Data Retrieved:**
- Company information (sector, industry, market cap)
- Analyst estimates (EPS, revenue)
- Analyst recommendations
- Historical price data
- Earnings calendar
- Earnings history with surprises

**Advantages:**
- Free, no API key required
- Comprehensive financial data
- Historical data available
- Python library with easy interface

### XAI API

**Purpose:** Primary LLM for transcript analysis

**Model:** `grok-beta`

**API Format:** OpenAI-compatible

**Advantages:**
- Large context window
- Good reasoning capabilities
- Fast inference

### Google Gemini API

**Purpose:** Alternative LLM for transcript analysis

**Model:** `gemini-2.5-flash`

**Advantages:**
- Fast inference
- Free tier available
- Good for quick summaries

---

## Testing and Quality Assurance

### Test Suite

**Test Files:**
1. `test_fmp_client.py` - FMP API client tests
2. `test_yfinance_client.py` - Yahoo Finance client tests
3. `run_all_tests.py` - Test runner with summary

**Test Coverage:**
- API connectivity
- Data retrieval
- Error handling
- Data parsing
- File operations

**Running Tests:**
```bash
cd tests
python run_all_tests.py
```

**Test Results:**
- Saved to `test-results/` directory
- JSON format with detailed results
- Summary report with pass/fail counts

### Quality Metrics

**Code Quality:**
- Modular design with separation of concerns
- Clear naming conventions
- Comprehensive docstrings
- Error handling throughout

**User Experience:**
- Intuitive navigation
- Clear instructions and tips
- Progress indicators for long operations
- Error messages with guidance

**Documentation:**
- README with quick start
- USER_GUIDE with detailed instructions
- DEPLOYMENT guide for various platforms
- Inline comments in code

---

## Deployment Options

### 1. Local Development
- Run on localhost for development and testing
- Full control over environment
- Best for: Development, testing, personal use

### 2. Streamlit Cloud
- Free hosting for public repositories
- Automatic deployments on git push
- Built-in secrets management
- Best for: Demos, proof-of-concepts, small teams

### 3. Docker
- Containerized deployment
- Consistent environment across platforms
- Easy scaling and management
- Best for: Production deployments, cloud platforms

### 4. AWS
- EC2 for traditional server deployment
- ECS for container orchestration
- Scalable and reliable
- Best for: Production, high-traffic applications

See `DEPLOYMENT.md` for detailed instructions.

---

## Security Considerations

### API Key Management
- Never commit API keys to git
- Use environment variables
- `.env` file in `.gitignore`
- Separate keys for dev/staging/prod

### Data Privacy
- No user data stored
- Transcripts are public information
- Analysis results stored locally
- No tracking or analytics

### Network Security
- HTTPS recommended for production
- Firewall rules for server deployments
- Rate limiting to prevent abuse

---

## Performance Optimization

### Caching
- Streamlit's `@st.cache_data` for data operations
- `@st.cache_resource` for LLM clients
- API response caching to reduce costs

### Resource Management
- Efficient data structures
- Lazy loading of large datasets
- Progress indicators for long operations

### API Cost Optimization
- Cache transcript downloads
- Reuse analysis results
- Batch operations where possible

---

## Future Enhancements

### Potential Features

1. **Database Integration**
   - PostgreSQL or MongoDB for persistent storage
   - Historical analysis tracking
   - User preferences and saved searches

2. **Advanced Analytics**
   - Trend analysis across multiple quarters
   - Sector comparison and benchmarking
   - Predictive modeling with ML

3. **User Authentication**
   - User accounts and profiles
   - Role-based access control
   - Personal dashboards

4. **Real-time Data**
   - Live earnings call transcription
   - Real-time stock price updates
   - Alert system for significant events

5. **Export and Reporting**
   - PDF report generation
   - Excel export with charts
   - Email notifications

6. **API Development**
   - REST API for programmatic access
   - Webhook support for integrations
   - API documentation with Swagger

7. **Mobile Support**
   - Responsive design improvements
   - Mobile app (React Native or Flutter)
   - Push notifications

8. **Collaboration Features**
   - Shared analyses and comments
   - Team workspaces
   - Annotation and highlighting

---

## Limitations and Disclaimers

### Current Limitations

1. **API Dependencies:**
   - Requires active API keys
   - Subject to rate limits
   - Dependent on external service availability

2. **Data Availability:**
   - Not all companies have transcripts available
   - Historical data may be limited
   - Real-time data not supported

3. **Analysis Quality:**
   - AI analysis is not perfect
   - May miss nuanced information
   - Should be used as a tool, not sole decision-maker

4. **Performance:**
   - Analysis can be slow for long transcripts
   - Batch operations may take time
   - Limited by API rate limits

### Disclaimers

⚠️ **Important:** This application is a proof-of-concept for educational and research purposes only. It does not constitute financial advice. Always conduct your own research and consult with financial professionals before making investment decisions.

- Not financial advice
- No guarantee of accuracy
- Past performance doesn't predict future results
- Use at your own risk

---

## Project Metrics

### Development Statistics

- **Total Files:** 26
- **Lines of Code:** ~4,000+
- **Python Modules:** 10
- **Streamlit Pages:** 5
- **Test Files:** 3
- **Documentation Pages:** 4

### Features Implemented

- ✅ Transcript download (single and bulk)
- ✅ AI-powered analysis (3 types)
- ✅ Financial data correlation
- ✅ Results management and search
- ✅ Interactive visualizations
- ✅ Testing framework
- ✅ Comprehensive documentation

### Time to MVP

- **Planning and Setup:** 1 phase
- **Core Development:** 4 phases
- **Testing and Documentation:** 2 phases
- **Deployment Preparation:** 1 phase
- **Total:** 8 phases

---

## Lessons Learned

### Technical Insights

1. **LangChain Integration:**
   - Powerful but requires careful prompt engineering
   - LangGraph adds complexity but enables sophisticated workflows
   - Model selection significantly impacts results

2. **Streamlit Development:**
   - Rapid prototyping is excellent
   - State management requires attention
   - Caching is crucial for performance

3. **API Integration:**
   - Error handling is critical
   - Rate limiting must be considered
   - Fallback options improve reliability

### Best Practices

1. **Modular Design:**
   - Separation of concerns makes maintenance easier
   - Reusable components save time
   - Clear interfaces between modules

2. **Documentation:**
   - Write documentation as you code
   - Include examples and screenshots
   - Keep documentation up to date

3. **Testing:**
   - Test early and often
   - Automated tests catch regressions
   - Real-world testing reveals edge cases

---

## Acknowledgments

### Technologies Used

- **Streamlit** - Web application framework
- **LangChain** - LLM orchestration
- **LangGraph** - Agentic workflows
- **XAI** - AI analysis
- **Google Gemini** - Alternative AI
- **Financial Modeling Prep** - Transcript data
- **Yahoo Finance** - Financial data
- **Plotly** - Visualizations
- **Pandas** - Data manipulation

### Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [LangChain Documentation](https://python.langchain.com)
- [FMP API Documentation](https://site.financialmodelingprep.com/developer/docs)
- [yfinance Documentation](https://pypi.org/project/yfinance/)

---

## Contact and Support

**Project Repository:** [https://github.com/kaljuvee/earnings-calls](https://github.com/kaljuvee/earnings-calls)

**Organization:** Lohusalu Capital Management

**Email:** dev@lohusalu.com

**Issues and Feature Requests:** [GitHub Issues](https://github.com/kaljuvee/earnings-calls/issues)

---

## Conclusion

The Earnings Call Analyzer successfully demonstrates how AI can be leveraged to automate and enhance earnings call analysis. By combining transcript analysis, financial data correlation, and predictive signals, the application provides a comprehensive toolkit for investment research.

The MVP is fully functional with all core features implemented, comprehensive documentation, and a clear path for future enhancements. The modular architecture and clean codebase make it easy to extend and maintain.

**Key Achievements:**
- ✅ Complete working MVP
- ✅ AI-powered analysis with multiple LLM options
- ✅ Financial data integration
- ✅ User-friendly interface
- ✅ Comprehensive documentation
- ✅ Testing framework
- ✅ Multiple deployment options

**Next Steps:**
1. Deploy to Streamlit Cloud for public access
2. Gather user feedback
3. Implement priority enhancements
4. Expand to additional data sources
5. Develop API for programmatic access

---

*This project was developed as a proof-of-concept to demonstrate the potential of AI-powered financial analysis. It serves as a foundation for more sophisticated investment research tools.*

---

**Version:** 1.0.0  
**Date:** November 12, 2025  
**Status:** MVP Complete

*Lohusalu Capital Management*
