"""
Download Transcripts Page
Search and download earnings call transcripts from FMP API
"""

import streamlit as st
import os
from dotenv import load_dotenv
from utils.fmp_client import FMPClient
import pandas as pd
from faker import Faker

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Download Transcripts",
    page_icon="📥",
    layout="wide"
)

st.title("📥 Download Earnings Call Transcripts")
st.markdown("Search and download earnings call transcripts from Financial Modeling Prep API")

# Initialize FMP client
fmp_api_key = os.getenv("FMP_API_KEY")
if not fmp_api_key:
    st.error("❌ FMP API Key not configured. Please set FMP_API_KEY in .env file")
    st.stop()

fmp_client = FMPClient(fmp_api_key)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # LLM provider selection
    llm_provider = st.selectbox(
        "LLM Provider",
        ["xai", "gemini"],
        help="Select the LLM provider for analysis"
    )
    
    st.markdown("---")
    
    # Generate synthetic data button
    if st.button("🎲 Generate Sample Data"):
        st.info("Sample data generation feature for testing")
        fake = Faker()
        
        sample_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        sample_data = []
        
        for ticker in sample_tickers:
            sample_data.append({
                "Ticker": ticker,
                "Company": fake.company(),
                "Quarter": fake.random_int(1, 4),
                "Year": fake.random_int(2023, 2025),
                "Status": "Available"
            })
        
        st.session_state['sample_data'] = pd.DataFrame(sample_data)
        st.success("✅ Sample data generated!")

# Main content
tab1, tab2, tab3 = st.tabs(["🔍 Search & Download", "📋 Available Transcripts", "📊 Bulk Download"])

with tab1:
    st.header("Search for Transcripts")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        ticker = st.text_input(
            "Ticker Symbol",
            placeholder="e.g., AAPL, MSFT, GOOGL",
            help="Enter the stock ticker symbol"
        ).upper()
    
    with col2:
        quarter = st.selectbox("Quarter", [1, 2, 3, 4], index=2)
    
    with col3:
        year = st.number_input("Year", min_value=2020, max_value=2025, value=2024)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        search_button = st.button("🔍 Search Transcript", type="primary", use_container_width=True)
    
    with col2:
        download_button = st.button("📥 Download & Save", type="secondary", use_container_width=True)
    
    if search_button and ticker:
        with st.spinner(f"Searching for {ticker} Q{quarter} {year} transcript..."):
            # Get company profile first
            profile = fmp_client.get_company_profile(ticker)
            
            if profile:
                st.success(f"✅ Found company: {profile.get('companyName', ticker)}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sector", profile.get('sector', 'N/A'))
                with col2:
                    st.metric("Industry", profile.get('industry', 'N/A'))
                with col3:
                    market_cap = profile.get('mktCap', 0)
                    if market_cap:
                        st.metric("Market Cap", f"${market_cap/1e9:.2f}B")
                
                # Try to get transcript
                transcript = fmp_client.get_transcript(ticker, quarter, year)
                
                if transcript:
                    st.success(f"✅ Transcript found! ({len(transcript)} characters)")
                    
                    # Show preview
                    with st.expander("📄 Preview Transcript"):
                        st.text(transcript[:2000] + "..." if len(transcript) > 2000 else transcript)
                    
                    st.session_state['current_transcript'] = {
                        'ticker': ticker,
                        'quarter': quarter,
                        'year': year,
                        'transcript': transcript,
                        'company_name': profile.get('companyName', ticker)
                    }
                else:
                    st.warning(f"⚠️ No transcript found for {ticker} Q{quarter} {year}")
            else:
                st.error(f"❌ Company not found: {ticker}")
    
    if download_button and ticker:
        if 'current_transcript' in st.session_state:
            with st.spinner(f"Downloading and saving transcript..."):
                saved_path = fmp_client.save_transcript(ticker, quarter, year)
                
                if saved_path:
                    st.success(f"✅ Transcript saved to: {saved_path}")
                    st.balloons()
                else:
                    st.error("❌ Failed to save transcript")
        else:
            st.warning("⚠️ Please search for a transcript first")

with tab2:
    st.header("Available Transcripts")
    
    # List transcripts in the transcripts directory
    transcript_dir = "transcripts"
    
    if os.path.exists(transcript_dir):
        transcript_files = [f for f in os.listdir(transcript_dir) if f.endswith('.md')]
        
        if transcript_files:
            st.info(f"📁 Found {len(transcript_files)} transcripts")
            
            # Parse filenames to create a dataframe
            transcript_data = []
            for filename in transcript_files:
                # Expected format: TICKER_QX_YEAR.md
                parts = filename.replace('.md', '').split('_')
                if len(parts) >= 3:
                    ticker_name = parts[0]
                    quarter_str = parts[1].replace('Q', '')
                    year_str = parts[2]
                    
                    file_path = os.path.join(transcript_dir, filename)
                    file_size = os.path.getsize(file_path)
                    
                    transcript_data.append({
                        'Ticker': ticker_name,
                        'Quarter': f"Q{quarter_str}",
                        'Year': year_str,
                        'Filename': filename,
                        'Size (KB)': f"{file_size/1024:.1f}"
                    })
            
            if transcript_data:
                df = pd.DataFrame(transcript_data)
                st.dataframe(df, use_container_width=True)
                
                # Download selected transcript
                st.subheader("View Transcript")
                selected_file = st.selectbox(
                    "Select a transcript to view",
                    transcript_files
                )
                
                if st.button("👁️ View Selected Transcript"):
                    file_path = os.path.join(transcript_dir, selected_file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    st.markdown("---")
                    st.markdown(content)
            else:
                st.warning("⚠️ No valid transcript files found")
        else:
            st.warning("⚠️ No transcripts downloaded yet")
    else:
        st.error("❌ Transcripts directory not found")

with tab3:
    st.header("Bulk Download")
    st.markdown("Download multiple transcripts at once")
    
    # Bulk download options
    col1, col2 = st.columns(2)
    
    with col1:
        bulk_tickers = st.text_area(
            "Ticker Symbols (one per line)",
            placeholder="AAPL\nMSFT\nGOOGL\nAMZN",
            height=150
        )
    
    with col2:
        bulk_quarter = st.selectbox("Quarter for all", [1, 2, 3, 4], index=2, key="bulk_q")
        bulk_year = st.number_input("Year for all", min_value=2020, max_value=2025, value=2024, key="bulk_y")
        
        st.markdown("---")
        
        bulk_download_button = st.button("📥 Download All", type="primary", use_container_width=True)
    
    if bulk_download_button and bulk_tickers:
        tickers = [t.strip().upper() for t in bulk_tickers.split('\n') if t.strip()]
        
        if tickers:
            st.info(f"Downloading {len(tickers)} transcripts...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            
            for i, ticker in enumerate(tickers):
                status_text.text(f"Processing {ticker}... ({i+1}/{len(tickers)})")
                
                saved_path = fmp_client.save_transcript(ticker, bulk_quarter, bulk_year)
                
                results.append({
                    'Ticker': ticker,
                    'Status': '✅ Success' if saved_path else '❌ Failed',
                    'Path': saved_path if saved_path else 'N/A'
                })
                
                progress_bar.progress((i + 1) / len(tickers))
            
            status_text.text("✅ Bulk download complete!")
            
            # Show results
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            success_count = sum(1 for r in results if r['Status'] == '✅ Success')
            st.success(f"Successfully downloaded {success_count}/{len(tickers)} transcripts")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Downloaded transcripts are saved in both .txt and .md formats in the `transcripts/` directory")
