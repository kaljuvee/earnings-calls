"""
Download Transcripts Page
Allows users to download earnings call transcripts from various sources
"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.api_ninjas_client import APINinjasClient
from utils.finnhub_client import FinnhubClient

st.set_page_config(page_title="Download Transcripts", page_icon="📥", layout="wide")

st.title("📥 Download Earnings Call Transcripts")
st.markdown("Search and download earnings call transcripts from multiple sources.")

# Sidebar for API selection
st.sidebar.header("⚙️ Settings")
api_source = st.sidebar.selectbox(
    "Select Transcript Source",
    ["API Ninjas", "Finnhub"],
    help="Choose the API source for downloading transcripts"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About Sources")
if api_source == "API Ninjas":
    st.sidebar.info("""
    **API Ninjas**
    - Free tier: S&P 100 companies
    - Premium: 8,000+ companies
    - Recent transcripts available
    - Requires API key from api-ninjas.com
    """)
elif api_source == "Finnhub":
    st.sidebar.info("""
    **Finnhub**
    - Premium feature
    - Extensive company coverage
    - Historical transcripts
    - Requires premium API key
    """)

# Create tabs
tab1, tab2, tab3 = st.tabs(["📄 Single Download", "📦 Bulk Download", "📂 Browse Transcripts"])

# Tab 1: Single Download
with tab1:
    st.header("Download Single Transcript")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", "AAPL", help="Enter stock ticker (e.g., AAPL, MSFT)")
    
    with col2:
        quarter = st.selectbox("Quarter", [1, 2, 3, 4], index=3, help="Select quarter (Q1-Q4)")
    
    with col3:
        year = st.number_input("Year", min_value=2020, max_value=2025, value=2024, step=1)
    
    st.markdown("---")
    
    col_search, col_download = st.columns(2)
    
    with col_search:
        if st.button("🔍 Search Transcript", use_container_width=True):
            with st.spinner(f"Searching for {ticker} Q{quarter} {year} transcript..."):
                try:
                    if api_source == "API Ninjas":
                        # Check if API key is available
                        api_key = os.getenv('API_NINJAS_KEY')
                        if not api_key or 'placeholder' in api_key.lower():
                            st.error("⚠️ API Ninjas API key not configured. Please add your API key to the .env file.")
                            st.info("Get your free API key at: https://api-ninjas.com/register")
                        else:
                            client = APINinjasClient()
                            transcript = client.get_transcript(ticker.upper(), year, quarter)
                            
                            if transcript:
                                st.success(f"✅ Found transcript for {ticker} Q{quarter} {year}")
                                
                                # Display preview
                                st.subheader("Preview")
                                transcript_text = transcript.get('transcript', '')
                                if isinstance(transcript_text, list):
                                    preview_text = str(transcript_text[:2])[:500]
                                else:
                                    preview_text = str(transcript_text)[:500]
                                
                                st.text_area("Transcript Preview", preview_text, height=200)
                                
                                # Store in session state for download
                                st.session_state['current_transcript'] = transcript
                                st.session_state['current_ticker'] = ticker.upper()
                                st.session_state['current_quarter'] = quarter
                                st.session_state['current_year'] = year
                            else:
                                st.warning(f"❌ No transcript found for {ticker} Q{quarter} {year}")
                                st.info("Try a different quarter/year or check if the company is in the S&P 100 (free tier)")
                    
                    elif api_source == "Finnhub":
                        # Check if API key is available
                        api_key = os.getenv('FINNHUB_API_KEY')
                        if not api_key:
                            st.error("⚠️ Finnhub API key not configured. Please add your API key to the .env file.")
                        else:
                            client = FinnhubClient()
                            transcript = client.find_transcript(ticker.upper(), year, quarter)
                            
                            if transcript:
                                st.success(f"✅ Found transcript for {ticker} Q{quarter} {year}")
                                
                                # Display preview
                                st.subheader("Preview")
                                transcript_text = transcript.get('transcript', '')
                                if isinstance(transcript_text, list):
                                    preview_text = str(transcript_text[:2])[:500]
                                else:
                                    preview_text = str(transcript_text)[:500]
                                
                                st.text_area("Transcript Preview", preview_text, height=200)
                                
                                # Store in session state for download
                                st.session_state['current_transcript'] = transcript
                                st.session_state['current_ticker'] = ticker.upper()
                                st.session_state['current_quarter'] = quarter
                                st.session_state['current_year'] = year
                            else:
                                st.warning(f"❌ No transcript found for {ticker} Q{quarter} {year}")
                                st.info("This may be a premium feature. Check your Finnhub subscription level.")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col_download:
        if st.button("💾 Download & Save", use_container_width=True):
            if 'current_transcript' in st.session_state:
                with st.spinner("Saving transcript..."):
                    try:
                        ticker = st.session_state['current_ticker']
                        quarter = st.session_state['current_quarter']
                        year = st.session_state['current_year']
                        
                        if api_source == "API Ninjas":
                            client = APINinjasClient()
                            filepath = client.save_transcript_to_file(ticker, year, quarter)
                        elif api_source == "Finnhub":
                            client = FinnhubClient()
                            filepath = client.save_transcript_to_file(ticker, year, quarter)
                        
                        if filepath:
                            st.success(f"✅ Transcript saved to: {filepath}")
                            
                            # Offer download
                            with open(filepath, 'r', encoding='utf-8') as f:
                                transcript_content = f.read()
                            
                            st.download_button(
                                label="📥 Download File",
                                data=transcript_content,
                                file_name=f"{ticker}_Q{quarter}_{year}.md",
                                mime="text/markdown"
                            )
                        else:
                            st.error("Failed to save transcript")
                    
                    except Exception as e:
                        st.error(f"Error saving transcript: {str(e)}")
            else:
                st.warning("⚠️ Please search for a transcript first")

# Tab 2: Bulk Download
with tab2:
    st.header("Bulk Download Transcripts")
    st.markdown("Download transcripts for multiple companies at once.")
    
    # Ticker input
    tickers_input = st.text_area(
        "Enter Tickers (one per line)",
        "AAPL\nMSFT\nGOOGL\nAMZN",
        height=150,
        help="Enter one ticker symbol per line"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        bulk_quarter = st.selectbox("Quarter", [1, 2, 3, 4], index=3, key="bulk_quarter")
    with col2:
        bulk_year = st.number_input("Year", min_value=2020, max_value=2025, value=2024, step=1, key="bulk_year")
    
    if st.button("📦 Download All", use_container_width=True):
        tickers = [t.strip().upper() for t in tickers_input.split('\n') if t.strip()]
        
        if not tickers:
            st.warning("Please enter at least one ticker")
        else:
            # Check API key
            if api_source == "API Ninjas":
                api_key = os.getenv('API_NINJAS_KEY')
                if not api_key or 'placeholder' in api_key.lower():
                    st.error("⚠️ API Ninjas API key not configured")
                    st.stop()
                client = APINinjasClient()
            elif api_source == "Finnhub":
                api_key = os.getenv('FINNHUB_API_KEY')
                if not api_key:
                    st.error("⚠️ Finnhub API key not configured")
                    st.stop()
                client = FinnhubClient()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []
            
            for i, ticker in enumerate(tickers):
                status_text.text(f"Processing {ticker}... ({i+1}/{len(tickers)})")
                
                try:
                    filepath = client.save_transcript_to_file(ticker, bulk_year, bulk_quarter)
                    if filepath:
                        results.append({'ticker': ticker, 'status': '✅ Success', 'path': filepath})
                    else:
                        results.append({'ticker': ticker, 'status': '❌ Not Found', 'path': None})
                except Exception as e:
                    results.append({'ticker': ticker, 'status': f'❌ Error: {str(e)}', 'path': None})
                
                progress_bar.progress((i + 1) / len(tickers))
            
            status_text.text("Download complete!")
            
            # Display results
            st.subheader("Download Results")
            for result in results:
                col1, col2, col3 = st.columns([1, 2, 3])
                with col1:
                    st.write(result['ticker'])
                with col2:
                    st.write(result['status'])
                with col3:
                    if result['path']:
                        st.write(result['path'])

# Tab 3: Browse Transcripts
with tab3:
    st.header("Browse Downloaded Transcripts")
    
    # Check if transcripts directory exists
    transcripts_dir = "transcripts"
    if not os.path.exists(transcripts_dir):
        st.info("No transcripts downloaded yet. Use the tabs above to download transcripts.")
    else:
        # List all transcript files
        transcript_files = [f for f in os.listdir(transcripts_dir) if f.endswith('.md')]
        
        if not transcript_files:
            st.info("No transcripts found in the transcripts directory.")
        else:
            st.success(f"Found {len(transcript_files)} transcript(s)")
            
            # Display files in a table
            selected_file = st.selectbox("Select a transcript to view", transcript_files)
            
            if selected_file:
                filepath = os.path.join(transcripts_dir, selected_file)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(selected_file)
                with col2:
                    # Download button
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    st.download_button(
                        "📥 Download",
                        content,
                        file_name=selected_file,
                        mime="text/markdown"
                    )
                
                # Display content
                with open(filepath, 'r', encoding='utf-8') as f:
                    transcript_content = f.read()
                
                # Show preview
                st.markdown("### Preview")
                st.markdown(transcript_content[:2000] + "..." if len(transcript_content) > 2000 else transcript_content)
                
                # Show full content in expander
                with st.expander("View Full Transcript"):
                    st.markdown(transcript_content)

# Footer
st.markdown("---")
st.markdown("""
### 📝 Notes
- **API Ninjas**: Free tier covers S&P 100 companies. Get your API key at [api-ninjas.com](https://api-ninjas.com/register)
- **Finnhub**: Premium feature. Requires paid subscription for transcript access.
- Transcripts are saved to the `transcripts/` directory in markdown format
- You can also manually upload transcript files to the `transcripts/` directory
""")
