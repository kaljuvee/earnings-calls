# Batch Processing Tasks

This directory contains scripts for batch processing of earnings call transcripts.

## Available Tasks

### `run_batch_analysis.py`

Downloads and analyzes earnings call transcripts for the **Magnificent 7** stocks for 2024.

**Stocks:**
- AAPL (Apple Inc.)
- MSFT (Microsoft Corporation)
- GOOGL (Alphabet Inc.)
- AMZN (Amazon.com Inc.)
- META (Meta Platforms Inc.)
- TSLA (Tesla Inc.)
- NVDA (NVIDIA Corporation)

**Quarters:**
- Q1 2024
- Q2 2024
- Q3 2024

**Total:** 21 transcripts (7 stocks × 3 quarters)

### Usage

```bash
# From project root
python3 tasks/run_batch_analysis.py
```

### What It Does

1. **Downloads transcripts** from API Ninjas for each stock/quarter combination
2. **Analyzes transcripts** using OpenAI GPT-4.1-mini
3. **Extracts scores** (-5 to +5) and justifications
4. **Saves to PostgreSQL** database (transcripts and analyses tables)
5. **Generates log file** in `tasks/logs/` directory
6. **Prints summary** with statistics and results

### Requirements

Environment variables must be set:
- `API_NINJAS_KEY` - For transcript downloads
- `DB_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - For LLM analysis (pre-configured)

### Output

**Console Output:**
```
======================================================================
BATCH ANALYSIS: MAG 7 STOCKS 2024
======================================================================

Stocks: AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA
Quarters: Q1, Q2, Q3 2024
Total: 21 transcripts

[1/21] Processing AAPL Q1 2024
----------------------------------------------------------------------
Downloading AAPL Q1 2024...
✅ Downloaded AAPL Q1 2024 (45234 chars)
Analyzing AAPL Q1 2024...
✅ Analyzed AAPL Q1 2024 - Score: +3/5 (32.5s)
💾 Saved AAPL Q1 2024 to database (transcript_id=1, analysis_id=1)

...

======================================================================
BATCH ANALYSIS SUMMARY
======================================================================

Total processed: 21
Successful: 21
Failed: 0
Total time: 15.2 minutes
Average time per transcript: 43.5 seconds

Average score: +2.4/5
Score range: -1 to +5

📊 Database Statistics:
  transcripts_count: 21
  analyses_count: 21
  price_movements_count: 0
  unique_tickers: 7

✅ Batch analysis complete!
📄 Log file: tasks/logs/batch_analysis_20241115_220000.log
======================================================================
```

**Log File:**
- Saved in `tasks/logs/batch_analysis_YYYYMMDD_HHMMSS.log`
- Contains timestamped entries for all operations
- Includes errors and warnings
- Useful for debugging and auditing

### Error Handling

The script handles common errors:
- **Transcript not available** - Logs warning and continues
- **API rate limits** - 2-second delay between requests
- **Analysis failures** - Logs error and continues
- **Database errors** - Logs error and continues

Failed transcripts are listed in the summary.

### Customization

To analyze different stocks or quarters, edit the script:

```python
# Change stocks
MAG_7_STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    # Add more...
}

# Change quarters
QUARTERS_2024 = [
    (1, 2024),
    (2, 2024),
    (3, 2024),
    (4, 2024),  # Add Q4
]
```

To change the LLM provider or model:

```python
# In BatchAnalyzer.__init__()
self.llm_client = LLMClient(provider='xai', model='grok-3')
```

### Performance

**Typical timing:**
- Download: ~2 seconds per transcript
- Analysis: ~30-45 seconds per transcript
- Database save: <1 second
- **Total:** ~40-50 seconds per transcript

**For 21 transcripts:**
- Estimated time: 15-20 minutes
- API calls: 21 (API Ninjas) + 21 (OpenAI)
- Database inserts: 42 (21 transcripts + 21 analyses)

### Monitoring

Check progress:
```bash
# Watch log file in real-time
tail -f tasks/logs/batch_analysis_*.log

# Check database
python3 -c "from utils.database import Database; db = Database(); print(db.get_database_stats())"
```

### Troubleshooting

**No transcripts found:**
- Check API Ninjas key is valid
- Verify stock ticker is in S&P 100 (free tier)
- Try different quarter/year

**Analysis fails:**
- Check OpenAI API key is configured
- Verify transcript is not empty
- Check LLM client logs

**Database errors:**
- Verify DB_URL is correct
- Check database is initialized (`python3 init_database.py`)
- Verify schema exists (`python3 run_sql_init.py`)

### Future Enhancements

- [ ] Parallel processing for faster execution
- [ ] Resume capability for interrupted runs
- [ ] Price movement data fetching
- [ ] Correlation analysis after batch
- [ ] Email notifications on completion
- [ ] Scheduled runs via cron
