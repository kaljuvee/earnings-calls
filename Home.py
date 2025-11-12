"""
Earnings Call Analysis Application
Main Home Page
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Earnings Call Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .company-name {
        font-size: 0.9rem;
        color: #888;
        text-align: center;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">📊 Earnings Call Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Analysis of Earnings Call Transcripts</div>', unsafe_allow_html=True)

# Introduction
st.markdown("""
Welcome to the **Earnings Call Analyzer**, a proof-of-concept application that demonstrates how 
publicly available earnings call transcripts can be analyzed using AI to identify predictive 
signals for market movement.
""")

st.markdown("---")

# Features section
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>🔍 Download Transcripts</h3>
        <p>Search and download earnings call transcripts from API Ninjas (S&P 100 free tier). 
        Access recent earnings calls for major publicly traded companies.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>🤖 AI-Powered Analysis</h3>
        <p>Leverage advanced LLMs (XAI, Gemini) via LangChain to automatically analyze transcripts 
        with structured bull/bear cases, themes, and key insights.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>📈 Financial Correlation</h3>
        <p>Compare analyst estimates with actual results using Yahoo Finance data. 
        Identify beats, misses, and surprise factors that drive market reactions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>🎯 Predictive Signals</h3>
        <p>Generate predictive scores and identify key signals that may indicate 
        future stock performance based on comprehensive analysis.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Getting Started
st.header("🚀 Getting Started")

st.markdown("""
1. **Download Transcripts** - Navigate to the "Download Transcripts" page to search and download earnings call transcripts
2. **Analyze Transcripts** - Use the "Analyze Transcripts" page to run AI-powered analysis on downloaded transcripts
3. **View Correlations** - Check the "Financial Correlation" page to compare with analyst estimates
4. **Review Results** - Explore comprehensive analysis reports on the "View Results" page

Use the sidebar to navigate between pages.
""")

# System Status
st.markdown("---")
st.header("⚙️ System Status")

col1, col2, col3 = st.columns(3)

with col1:
    xai_key = os.getenv("XAI_API_KEY")
    if xai_key:
        st.success("✅ XAI API Key Configured")
    else:
        st.error("❌ XAI API Key Missing")

with col2:
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        st.success("✅ Google API Key Configured")
    else:
        st.error("❌ Google API Key Missing")

with col3:
    api_ninjas_key = os.getenv("API_NINJAS_KEY")
    if api_ninjas_key and 'placeholder' not in api_ninjas_key.lower():
        st.success("✅ API Ninjas Key Configured")
    else:
        st.warning("⚠️ API Ninjas Key Missing")

# Check transcript directory
transcript_dir = "transcripts"
if os.path.exists(transcript_dir):
    transcript_count = len([f for f in os.listdir(transcript_dir) if f.endswith('.md')])
    st.info(f"📁 {transcript_count} transcripts available in the transcripts directory")
else:
    st.warning("📁 Transcripts directory not found")

# Footer
st.markdown("---")
st.markdown('<div class="company-name">Lohusalu Capital Management</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📚 About")
    st.markdown("""
    This application uses:
    - **API Ninjas** for earnings transcripts
    - **Finnhub** for financial data (optional)
    - **Yahoo Finance** for earnings estimates
    - **XAI & Gemini** for AI analysis
    - **LangChain & LangGraph** for agentic workflows
    """)
    
    st.markdown("---")
    
    st.header("🔗 Quick Links")
    st.markdown("""
    - [GitHub Repository](https://github.com/kaljuvee/earnings-calls)
    - [API Ninjas](https://api-ninjas.com/api/earningscalltranscript)
    - [Finnhub](https://finnhub.io/)
    - [Yahoo Finance](https://finance.yahoo.com)
    """)
    
    st.markdown("---")
    
    st.header("⚠️ Disclaimer")
    st.markdown("""
    This is a proof-of-concept application for educational purposes only. 
    Not financial advice.
    """)
