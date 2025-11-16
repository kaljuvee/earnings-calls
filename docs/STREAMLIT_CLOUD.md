# Streamlit Cloud Deployment Guide

## Overview

This guide explains how to deploy the Earnings Call Analyzer to Streamlit Cloud and ensure data persistence.

## Important: File Persistence in Streamlit Cloud

### What Persists

✅ **Files that persist across sessions:**
- Files in the GitHub repository
- Files written to the app's working directory (`analyses/`, `data/`, `transcripts/`)

### How Streamlit Cloud Works

Streamlit Cloud is **NOT a lambda service** - it runs a persistent container for your app:

1. **Container Lifecycle**: The container stays alive as long as the app is active
2. **File Persistence**: Files written to disk persist within the container
3. **Restarts**: Container may restart due to:
   - App updates (git push)
   - Inactivity (app sleeps after ~7 days of no traffic)
   - Platform maintenance
4. **After Restart**: Files written to disk are lost unless they're in the git repo

### Recommended Approach

For production use with Streamlit Cloud, you have two options:

#### Option 1: External Database (Recommended for Production)

Use a cloud database service:
- **PostgreSQL**: Supabase, Neon, or Railway
- **SQLite Cloud**: Turso or LiteFS
- **MongoDB**: MongoDB Atlas

Benefits:
- ✅ Data persists across restarts
- ✅ Accessible from multiple instances
- ✅ Backup and recovery
- ✅ Scalable

#### Option 2: Local SQLite with Periodic Backup

Keep using local SQLite but implement backups:
- Use GitHub Actions to periodically commit database
- Export to CSV and commit to repo
- Use Streamlit Cloud's secrets to store in S3/GCS

### Current Implementation

The app currently uses **local SQLite** (`data/earnings_analysis.db`):

```python
# In utils/db_util.py
class DatabaseUtil:
    def __init__(self, db_path: str = "data/earnings_analysis.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
```

**What this means:**
- ✅ Works perfectly during active sessions
- ✅ Data persists as long as container runs
- ⚠️ Data lost if container restarts
- ⚠️ Not suitable for long-term production use

## Deployment Steps

### 1. Push to GitHub

```bash
git add -A
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repository: `kaljuvee/earnings-calls`
4. Set main file path: `Home.py`
5. Click "Deploy"

### 3. Configure Secrets

Add these secrets in Streamlit Cloud settings:

```toml
# .streamlit/secrets.toml (add via Streamlit Cloud UI)

API_NINJAS_KEY = "your_api_ninjas_key"
FINNHUB_API_KEY = "your_finnhub_key"
XAI_API_KEY = "your_xai_key"
GOOGLE_API_KEY = "your_google_key"
GROK_MODEL = "grok-3"

# If using external database
DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
```

### 4. Update Database Configuration (Optional)

To use an external database, modify `utils/db_util.py`:

```python
import os
import streamlit as st

class DatabaseUtil:
    def __init__(self, db_path: str = None):
        # Check for external database URL in secrets
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            # Use PostgreSQL or other external DB
            self.db_url = st.secrets['DATABASE_URL']
            self.use_external = True
        else:
            # Use local SQLite
            self.db_path = db_path or "data/earnings_analysis.db"
            self.use_external = False
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self._init_database()
```

## File Storage Locations

### Analyses Directory

```
analyses/
├── AAPL_Q3_2024_20251112_085319.md
├── AAPL_Q3_2024_20251112_085319.json
└── ...
```

**Persistence**: Files persist during container lifetime

### Database Directory

```
data/
└── earnings_analysis.db
```

**Persistence**: Database persists during container lifetime

### Transcripts Directory

```
transcripts/
├── AAPL_Q3_2024.md
├── MSFT_Q2_2024.md
└── ...
```

**Persistence**: Files persist during container lifetime

## Backup Strategy

### Manual Backup

Download data before container restart:

1. Go to **View Results** page
2. Download all analyses as CSV
3. Go to **Correlations** page  
4. Download correlation data

### Automated Backup (Recommended)

Create a backup page:

```python
# pages/5_Backup.py
import streamlit as st
from utils.db_util import DatabaseUtil
import pandas as pd
from datetime import datetime

st.title("💾 Backup & Restore")

db = DatabaseUtil()

# Export database to CSV
if st.button("Export All Data"):
    # Export scores
    scores_df = pd.read_sql_query("SELECT * FROM scores", db.get_connection())
    
    # Export price movements
    movements_df = pd.read_sql_query("SELECT * FROM price_movements", db.get_connection())
    
    # Create download buttons
    st.download_button(
        "Download Scores",
        scores_df.to_csv(index=False),
        f"scores_backup_{datetime.now().strftime('%Y%m%d')}.csv"
    )
    
    st.download_button(
        "Download Price Movements",
        movements_df.to_csv(index=False),
        f"movements_backup_{datetime.now().strftime('%Y%m%d')}.csv"
    )
```

## Monitoring

### Check Container Status

Streamlit Cloud provides:
- **Logs**: View real-time application logs
- **Metrics**: CPU, memory usage
- **Errors**: Runtime errors and exceptions

### Database Size

Monitor database size in your app:

```python
import os

db_path = "data/earnings_analysis.db"
if os.path.exists(db_path):
    size_mb = os.path.getsize(db_path) / 1024 / 1024
    st.sidebar.metric("Database Size", f"{size_mb:.2f} MB")
```

## Migration to External Database

### Step 1: Export Current Data

```python
from utils.db_util import DatabaseUtil
import pandas as pd

db = DatabaseUtil()
conn = db.get_connection()

# Export all tables
scores = pd.read_sql_query("SELECT * FROM scores", conn)
movements = pd.read_sql_query("SELECT * FROM price_movements", conn)
correlations = pd.read_sql_query("SELECT * FROM correlations", conn)

# Save to CSV
scores.to_csv("backup_scores.csv", index=False)
movements.to_csv("backup_movements.csv", index=False)
correlations.to_csv("backup_correlations.csv", index=False)
```

### Step 2: Set Up External Database

For PostgreSQL (Supabase example):

1. Create project at https://supabase.com
2. Get connection string
3. Run schema from `sql/create_tables.sql` (adapted for PostgreSQL)
4. Add `DATABASE_URL` to Streamlit secrets

### Step 3: Import Data

```python
import pandas as pd
from sqlalchemy import create_engine

# Connect to PostgreSQL
engine = create_engine(st.secrets['DATABASE_URL'])

# Import data
scores = pd.read_csv("backup_scores.csv")
scores.to_sql('scores', engine, if_exists='append', index=False)

movements = pd.read_csv("backup_movements.csv")
movements.to_sql('price_movements', engine, if_exists='append', index=False)
```

## Troubleshooting

### Issue: Data Lost After Restart

**Cause**: Container restarted, local files cleared

**Solution**:
1. Implement automated backups
2. Migrate to external database
3. Store critical data in GitHub repo

### Issue: Database Locked

**Cause**: Multiple connections to SQLite

**Solution**:
```python
# Use connection pooling or ensure connections are closed
conn = db.get_connection()
try:
    # Do work
    pass
finally:
    conn.close()
```

### Issue: Out of Memory

**Cause**: Large database or too many files

**Solution**:
1. Implement file cleanup for old analyses
2. Move to external database
3. Upgrade Streamlit Cloud plan

## Best Practices

1. **Regular Backups**: Export data weekly
2. **Monitor Size**: Keep database under 100MB for SQLite
3. **Clean Old Data**: Implement retention policy
4. **Use External DB**: For production deployments
5. **Test Locally**: Always test with `streamlit run Home.py` first
6. **Version Control**: Commit working code before deploying

## Current Status

✅ **Working in Streamlit Cloud**: Yes
✅ **Data Persists During Session**: Yes
⚠️ **Data Persists After Restart**: No (local SQLite)
📝 **Recommended**: Migrate to external database for production

## Resources

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Supabase (PostgreSQL)](https://supabase.com)
- [Turso (SQLite Cloud)](https://turso.tech)
- [Railway (PostgreSQL)](https://railway.app)
