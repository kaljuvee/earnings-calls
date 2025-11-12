# Earnings Call Transcript Sources

This document explains the available transcript sources and how to configure them.

## Available Sources

### 1. API Ninjas (Recommended for Free Tier)

**Website:** https://api-ninjas.com/

**Features:**
- ✅ **Free Tier Available**: S&P 100 companies
- ✅ **Premium Tier**: 8,000+ companies
- ✅ **Recent Data**: Updated regularly
- ✅ **Easy Setup**: Simple API key registration

**Coverage:**
- Free tier: S&P 100 companies (major US companies)
- Premium: 8,000+ companies globally
- Historical transcripts available

**Setup:**
1. Sign up at https://api-ninjas.com/register
2. Get your free API key from the dashboard
3. Add to `.env` file:
   ```
   API_NINJAS_KEY=your_api_key_here
   ```

**Pricing:**
- Free: 10,000 requests/month
- Premium: Starting at $10/month for unlimited requests

### 2. Finnhub

**Website:** https://finnhub.io/

**Features:**
- ⚠️ **Premium Feature**: Requires paid subscription
- ✅ **Extensive Coverage**: Large company database
- ✅ **Historical Data**: Deep historical transcripts
- ✅ **High Quality**: Well-structured data

**Coverage:**
- Thousands of companies globally
- Historical transcripts going back several years
- Regular updates

**Setup:**
1. Sign up at https://finnhub.io/
2. Upgrade to a premium plan that includes transcript access
3. Get your API key from the dashboard
4. Add to `.env` file:
   ```
   FINNHUB_API_KEY=your_api_key_here
   ```

**Pricing:**
- Free tier: Basic stock data only (no transcripts)
- Premium: Starting at $59/month (includes transcripts)

### 3. Financial Modeling Prep (FMP) - Deprecated

**Status:** ⚠️ **No longer supported for free tier**

The FMP earnings call transcript endpoint was deprecated on August 31, 2025, and is no longer available for free tier users. Premium plans may still have access, but we recommend using API Ninjas or Finnhub instead.

## Comparison Table

| Feature | API Ninjas (Free) | API Ninjas (Premium) | Finnhub (Premium) |
|---------|-------------------|---------------------|-------------------|
| **Price** | Free | $10/month | $59/month |
| **Companies** | S&P 100 | 8,000+ | Thousands |
| **Historical Data** | ✅ Yes | ✅ Yes | ✅ Yes |
| **API Calls/Month** | 10,000 | Unlimited | Depends on plan |
| **Setup Difficulty** | Easy | Easy | Easy |
| **Best For** | Testing, S&P 100 | Production | Enterprise |

## Recommended Setup

### For Development/Testing
Use **API Ninjas Free Tier**:
- Covers major S&P 100 companies (AAPL, MSFT, GOOGL, etc.)
- 10,000 requests/month is sufficient for testing
- No credit card required

### For Production
Use **API Ninjas Premium** or **Finnhub Premium**:
- API Ninjas: Better value for money ($10/month)
- Finnhub: More comprehensive data but more expensive

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# API Ninjas (get from https://api-ninjas.com/register)
API_NINJAS_KEY=your_api_ninjas_key_here

# Finnhub (get from https://finnhub.io/)
FINNHUB_API_KEY=your_finnhub_key_here
```

### Switching Between Sources

In the Streamlit app:
1. Navigate to **Download Transcripts** page
2. Use the **sidebar** to select your preferred source
3. The app will automatically use the selected API

## Testing Your Setup

### Test API Ninjas

```bash
cd earnings-calls
python3 -c "
from utils.api_ninjas_client import APINinjasClient
client = APINinjasClient()
companies = client.list_available_companies()
print(f'Available companies: {len(companies)}')
"
```

### Test Finnhub

```bash
cd earnings-calls
python3 -c "
from utils.finnhub_client import FinnhubClient
client = FinnhubClient()
transcripts = client.get_transcripts_list('AAPL')
print(f'AAPL transcripts: {len(transcripts)}')
"
```

## Troubleshooting

### "API key not configured" Error

**Solution:** Make sure your `.env` file contains the API key:
```bash
# Check if .env file exists
cat .env

# If missing, create it from sample
cp .env.sample .env

# Edit and add your API key
nano .env
```

### "You don't have access to this resource" Error

**Finnhub:** This means the transcript endpoint requires a premium subscription.
- Upgrade your Finnhub plan, or
- Switch to API Ninjas in the sidebar

**API Ninjas:** This may mean:
- Invalid API key
- Company not in your tier (try S&P 100 companies on free tier)
- Rate limit exceeded

### No Transcripts Found

**Possible causes:**
1. Company not covered by the API
2. Quarter/year not available
3. Ticker symbol incorrect

**Solutions:**
- Try different quarters/years
- Verify ticker symbol is correct
- Check if company is in S&P 100 (for API Ninjas free tier)
- Try the other API source

## Manual Upload Alternative

If APIs don't work or you have transcripts from other sources:

1. Save transcript as markdown file
2. Name it: `TICKER_QX_YEAR.md` (e.g., `AAPL_Q4_2024.md`)
3. Place in `transcripts/` directory
4. The app will automatically detect and analyze it

## Support

For API-specific issues:
- **API Ninjas:** https://api-ninjas.com/support
- **Finnhub:** https://finnhub.io/support

For app issues:
- Check GitHub Issues: https://github.com/kaljuvee/earnings-calls/issues
- Review documentation: README.md and USER_GUIDE.md
