# Earnings Call Analysis Application

A Streamlit-based MVP application that analyzes publicly available earnings call transcripts using LLM-powered analysis to identify predictive signals for market movement.

## Features

- **Transcript Download**: Fetch earnings call transcripts from API Ninjas (S&P 100 free tier)
- **LLM Analysis**: Automated analysis using XAI and Gemini via LangChain
- **Financial Correlation**: Compare analyst estimates vs actual results using Yahoo Finance
- **Structured Analysis**: Bull/Bear case analysis, verdict, themes, and key questions
- **Agentic Workflow**: LangGraph-powered multi-step analysis pipeline

## Project Structure

```
earnings-calls/
├── Home.py                 # Main Streamlit application
├── pages/                  # Streamlit pages
│   ├── 0_Download_Transcripts.py
│   ├── 1_Analyze_Transcripts.py
│   ├── 2_Financial_Correlation.py
│   └── 3_View_Results.py
├── utils/                  # Utility modules
│   ├── api_ninjas_client.py  # API Ninjas client
│   ├── finnhub_client.py     # Finnhub client
│   ├── llm_client.py         # LLM integration
│   └── yfinance_client.py    # Yahoo Finance integration
├── prompts/               # LLM prompts
│   └── analysis_prompt.py
├── transcripts/           # Downloaded transcripts
├── tests/                 # Test files
└── test-results/          # Test outputs
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/kaljuvee/earnings-calls.git
cd earnings-calls
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.sample .env
# Edit .env with your API keys
```

4. Run the application:
```bash
streamlit run Home.py
```

## API Keys Required

- **XAI_API_KEY**: For XAI LLM access
- **GROK_MODEL**: (Optional) Grok model to use, defaults to `grok-3`
- **GOOGLE_API_KEY**: For Gemini LLM access
- **API_NINJAS_KEY**: For API Ninjas earnings transcripts (10,000 calls/month free tier)
- **FINNHUB_API_KEY**: (Optional) For Finnhub financial data

## Usage

1. **Download Transcripts**: Search and download earnings call transcripts by ticker
2. **Analyze**: Run LLM-powered analysis on downloaded transcripts
3. **Correlate**: Compare with analyst estimates and recommendations
4. **Review**: View structured analysis with bull/bear cases and predictions

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: XAI (default), Gemini via LangChain
- **Agentic Flow**: LangGraph
- **Financial APIs**: API Ninjas, Yahoo Finance, Finnhub (optional)

## License

MIT
