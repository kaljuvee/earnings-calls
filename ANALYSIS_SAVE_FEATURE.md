# Analysis Save Feature

## Overview

All earnings call analyses are now automatically saved in **both JSON and Markdown formats** in the `analyses/` directory.

## File Structure

### Directory
```
analyses/
├── {TICKER}_Q{QUARTER}_{YEAR}_{TIMESTAMP}.md
├── {TICKER}_Q{QUARTER}_{YEAR}_{TIMESTAMP}.json
├── {TICKER}_Q{QUARTER}_{YEAR}_agentic_{TIMESTAMP}.md
└── {TICKER}_Q{QUARTER}_{YEAR}_agentic_{TIMESTAMP}.json
```

### Filename Format

**Standard Analysis:**
- `AAPL_Q3_2024_20251112_085319.md`
- `AAPL_Q3_2024_20251112_085319.json`

**Agentic Workflow:**
- `AAPL_Q3_2024_agentic_20251112_085319.md`
- `AAPL_Q3_2024_agentic_20251112_085319.json`

## Markdown Format (.md)

Contains the full analysis text in markdown format, ready for:
- Direct reading
- Publishing to blogs/websites
- Converting to PDF
- Sharing with stakeholders

**Example:**
```markdown
# $AAPL Q3 2024 earnings: Record revenue...

Apple delivered a robust Q3 FY2025...

## 🐂 𝗧𝗵𝗲 𝗕𝘂𝗹𝗹 𝗖𝗮𝘀𝗲

Strong revenue and earnings growth...
```

## JSON Format (.json)

Contains structured data with metadata for:
- Programmatic access
- Database storage
- API integration
- Analysis comparison

### JSON Schema

```json
{
  "ticker": "AAPL",
  "quarter": 3,
  "year": 2024,
  "company_name": "AAPL",
  "timestamp": "20251112_085319",
  "provider": "openai",
  "model": "gpt-4.1-mini",
  "analysis_type": "Standard Analysis",
  "analysis_markdown": "# Full markdown content...",
  "financial_context_included": false
}
```

### Additional Fields for Agentic Workflow

```json
{
  "analysis_type": "Agentic Workflow",
  "results": {
    "main_analysis": "...",
    "sentiment_analysis": "...",
    "predictive_signals": "..."
  },
  "full_report_markdown": "...",
  "sentiment_included": true,
  "predictions_included": true
}
```

## Features

### Automatic Saving
- ✅ Every analysis is automatically saved
- ✅ Both formats saved simultaneously
- ✅ Unique timestamp prevents overwrites
- ✅ Organized in dedicated `analyses/` folder

### Download Options
After each analysis, users can download:
- **Markdown file** - For documentation and sharing
- **JSON file** - For programmatic use and archival

### Metadata Tracking
Each analysis includes:
- Company ticker and quarter
- Analysis timestamp
- LLM provider and model used
- Analysis type (Standard/Agentic)
- Configuration options used

## Use Cases

### 1. Historical Analysis Tracking
Track how analysis changes over time or with different models:
```bash
analyses/
├── AAPL_Q3_2024_20251112_085319.json  # OpenAI analysis
├── AAPL_Q3_2024_20251112_090145.json  # XAI analysis
└── AAPL_Q3_2024_20251112_091203.json  # Gemini analysis
```

### 2. Batch Processing
Load and compare multiple analyses programmatically:
```python
import json
import glob

# Load all AAPL analyses
analyses = []
for file in glob.glob("analyses/AAPL_*.json"):
    with open(file) as f:
        analyses.append(json.load(f))

# Compare different models
for analysis in analyses:
    print(f"{analysis['provider']}: {len(analysis['analysis_markdown'])} chars")
```

### 3. API Integration
Serve analyses via API:
```python
from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/analysis/<ticker>/<quarter>/<year>')
def get_analysis(ticker, quarter, year):
    # Load latest analysis
    pattern = f"analyses/{ticker}_Q{quarter}_{year}_*.json"
    files = sorted(glob.glob(pattern), reverse=True)
    if files:
        with open(files[0]) as f:
            return jsonify(json.load(f))
    return {"error": "Not found"}, 404
```

### 4. Database Storage
Import analyses into database:
```python
import sqlite3
import json

conn = sqlite3.connect('analyses.db')
cursor = conn.cursor()

for file in glob.glob("analyses/*.json"):
    with open(file) as f:
        data = json.load(f)
        cursor.execute("""
            INSERT INTO analyses 
            (ticker, quarter, year, provider, model, analysis, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['ticker'],
            data['quarter'],
            data['year'],
            data['provider'],
            data['model'],
            data['analysis_markdown'],
            data['timestamp']
        ))

conn.commit()
```

## Configuration

### .gitignore
The `analyses/` directory is added to `.gitignore` to prevent committing large analysis files:
```
# Analysis output files
analyses/
```

### Directory Creation
The directory is automatically created when the first analysis is saved.

## Benefits

1. **Dual Format Support**: Both human-readable (MD) and machine-readable (JSON)
2. **Complete Metadata**: Track provider, model, settings for each analysis
3. **Easy Comparison**: Compare analyses from different models or time periods
4. **Programmatic Access**: JSON format enables automation and integration
5. **Historical Record**: Permanent record of all analyses with timestamps
6. **Flexible Usage**: Use MD for reports, JSON for data processing

## Testing

Run the test script to verify functionality:
```bash
python3 test_analysis_save.py
```

Expected output:
```
✓ Markdown saved: analyses/AAPL_Q3_2024_20251112_085319.md
✓ JSON saved: analyses/AAPL_Q3_2024_20251112_085319.json
✓ Markdown file verified
✓ JSON file verified
✅ ALL TESTS PASSED
```
