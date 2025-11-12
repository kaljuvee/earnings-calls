"""
Analyze Transcripts Page
Run LLM-powered analysis on downloaded transcripts
"""

import streamlit as st
import os
from dotenv import load_dotenv
from utils.llm_client import LLMClient
from utils.data_correlator import DataCorrelator
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Analyze Transcripts",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Analyze Earnings Call Transcripts")
st.markdown("AI-powered analysis using LangChain and LangGraph")

# Check API keys
openai_key = os.getenv("OPENAI_API_KEY")
xai_key = os.getenv("XAI_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")

if not openai_key and not xai_key and not google_key:
    st.error("❌ No LLM API keys configured. Please set OPENAI_API_KEY, XAI_API_KEY, or GOOGLE_API_KEY in .env file")
    st.stop()

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Analysis Settings")
    
    # LLM provider selection
    available_providers = []
    if openai_key:
        available_providers.append("openai")
    if xai_key:
        available_providers.append("xai")
    if google_key:
        available_providers.append("gemini")
    
    llm_provider = st.selectbox(
        "LLM Provider",
        available_providers,
        help="Select the LLM provider for analysis"
    )
    
    # Model selection based on provider
    if llm_provider == "openai":
        model = st.selectbox(
            "Model",
            ["gpt-4.1-mini", "gpt-4.1-nano", "gemini-2.5-flash"],
            help="Select the OpenAI model"
        )
    else:
        model = None
    
    # Analysis type
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Standard Analysis", "Agentic Workflow", "Quick Summary"],
        help="Choose the type of analysis to run"
    )
    
    st.markdown("---")
    
    st.header("📊 Analysis Options")
    
    include_sentiment = st.checkbox("Include Sentiment Analysis", value=True)
    include_predictions = st.checkbox("Include Predictive Signals", value=True)
    include_financial_context = st.checkbox("Include Financial Context", value=True)
    
    st.markdown("---")
    
    # Temperature setting
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1,
                           help="Higher values make output more creative, lower values more focused")

# Main content
tab1, tab2, tab3 = st.tabs(["📝 Single Analysis", "🔄 Batch Analysis", "📊 View Results"])

with tab1:
    st.header("Analyze Single Transcript")
    
    # Get list of available transcripts
    transcript_dir = "transcripts"
    transcript_files = []
    
    if os.path.exists(transcript_dir):
        transcript_files = [f for f in os.listdir(transcript_dir) if f.endswith('.md')]
    
    if not transcript_files:
        st.warning("⚠️ No transcripts available. Please download transcripts first.")
        st.stop()
    
    # Select transcript
    selected_file = st.selectbox(
        "Select Transcript",
        transcript_files,
        help="Choose a transcript to analyze"
    )
    
    # Parse filename to extract metadata
    if selected_file:
        parts = selected_file.replace('.md', '').split('_')
        if len(parts) >= 3:
            ticker = parts[0]
            quarter = int(parts[1].replace('Q', ''))
            year = int(parts[2])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ticker", ticker)
            with col2:
                st.metric("Quarter", f"Q{quarter}")
            with col3:
                st.metric("Year", year)
    
    # Preview transcript
    with st.expander("📄 Preview Transcript"):
        file_path = os.path.join(transcript_dir, selected_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        st.markdown(content[:3000] + "..." if len(content) > 3000 else content)
    
    # Analyze button
    col1, col2 = st.columns([1, 3])
    
    with col1:
        analyze_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
    
    if analyze_button:
        # Read full transcript
        file_path = os.path.join(transcript_dir, selected_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        # Initialize clients
        llm_client = LLMClient(provider=llm_provider, model=model if llm_provider == "openai" else None)
        correlator = DataCorrelator()
        
        # Get financial context if requested
        financial_context = ""
        if include_financial_context:
            with st.spinner("Fetching financial context..."):
                financial_context = correlator.generate_financial_context(ticker, quarter, year)
        
        # Run analysis based on type
        if analysis_type == "Agentic Workflow":
            st.info("🤖 Running agentic workflow with LangGraph...")
            
            with st.spinner("Analyzing transcript... This may take a few minutes."):
                try:
                    results = llm_client.run_agentic_analysis(
                        ticker=ticker,
                        quarter=quarter,
                        year=year,
                        transcript=transcript,
                        company_name=ticker,
                        financial_context=financial_context
                    )
                    
                    # Display results
                    st.success("✅ Analysis complete!")
                    
                    # Main analysis
                    st.markdown("## 📊 Main Analysis")
                    st.markdown(results.get('main_analysis', 'No analysis available'))
                    
                    # Sentiment analysis
                    if include_sentiment and results.get('sentiment_analysis'):
                        st.markdown("---")
                        st.markdown("## 😊 Sentiment Analysis")
                        st.markdown(results.get('sentiment_analysis', ''))
                    
                    # Predictive signals
                    if include_predictions and results.get('predictive_signals'):
                        st.markdown("---")
                        st.markdown("## 🎯 Predictive Signals")
                        st.markdown(results.get('predictive_signals', ''))
                    
                    # Save results
                    results_dir = "test-results"
                    os.makedirs(results_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    result_file = f"{ticker}_Q{quarter}_{year}_analysis_{timestamp}.json"
                    result_path = os.path.join(results_dir, result_file)
                    
                    with open(result_path, 'w', encoding='utf-8') as f:
                        json.dump({
                            'ticker': ticker,
                            'quarter': quarter,
                            'year': year,
                            'timestamp': timestamp,
                            'provider': llm_provider,
                            'results': results
                        }, f, indent=2)
                    
                    st.success(f"💾 Results saved to: {result_path}")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Full Report",
                        data=results.get('final_report', ''),
                        file_name=f"{ticker}_Q{quarter}_{year}_report.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.exception(e)
        
        else:  # Standard Analysis
            st.info("📝 Running standard analysis...")
            
            with st.spinner("Analyzing transcript..."):
                try:
                    # Main analysis
                    analysis = llm_client.analyze_transcript(
                        ticker=ticker,
                        quarter=quarter,
                        year=year,
                        transcript=transcript,
                        company_name=ticker,
                        financial_context=financial_context
                    )
                    
                    st.success("✅ Analysis complete!")
                    st.markdown(analysis)
                    
                    # Save results
                    results_dir = "test-results"
                    os.makedirs(results_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    result_file = f"{ticker}_Q{quarter}_{year}_analysis_{timestamp}.md"
                    result_path = os.path.join(results_dir, result_file)
                    
                    with open(result_path, 'w', encoding='utf-8') as f:
                        f.write(analysis)
                    
                    st.success(f"💾 Results saved to: {result_path}")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Analysis",
                        data=analysis,
                        file_name=f"{ticker}_Q{quarter}_{year}_analysis.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.exception(e)

with tab2:
    st.header("Batch Analysis")
    st.markdown("Analyze multiple transcripts at once")
    
    # Get all transcripts
    if transcript_files:
        st.info(f"📁 {len(transcript_files)} transcripts available")
        
        # Select transcripts for batch processing
        selected_transcripts = st.multiselect(
            "Select Transcripts to Analyze",
            transcript_files,
            help="Choose multiple transcripts for batch analysis"
        )
        
        if selected_transcripts:
            st.info(f"Selected {len(selected_transcripts)} transcripts")
            
            batch_button = st.button("🚀 Run Batch Analysis", type="primary")
            
            if batch_button:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                llm_client = LLMClient(provider=llm_provider)
                correlator = DataCorrelator()
                
                results_summary = []
                
                for i, filename in enumerate(selected_transcripts):
                    status_text.text(f"Analyzing {filename}... ({i+1}/{len(selected_transcripts)})")
                    
                    # Parse filename
                    parts = filename.replace('.md', '').split('_')
                    if len(parts) >= 3:
                        ticker = parts[0]
                        quarter = int(parts[1].replace('Q', ''))
                        year = int(parts[2])
                        
                        # Read transcript
                        file_path = os.path.join(transcript_dir, filename)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            transcript = f.read()
                        
                        try:
                            # Run analysis
                            financial_context = ""
                            if include_financial_context:
                                financial_context = correlator.generate_financial_context(ticker, quarter, year)
                            
                            analysis = llm_client.analyze_transcript(
                                ticker=ticker,
                                quarter=quarter,
                                year=year,
                                transcript=transcript,
                                company_name=ticker,
                                financial_context=financial_context
                            )
                            
                            # Save results
                            results_dir = "test-results"
                            os.makedirs(results_dir, exist_ok=True)
                            
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            result_file = f"{ticker}_Q{quarter}_{year}_analysis_{timestamp}.md"
                            result_path = os.path.join(results_dir, result_file)
                            
                            with open(result_path, 'w', encoding='utf-8') as f:
                                f.write(analysis)
                            
                            results_summary.append({
                                'Ticker': ticker,
                                'Quarter': f"Q{quarter}",
                                'Year': year,
                                'Status': '✅ Success',
                                'File': result_file
                            })
                            
                        except Exception as e:
                            results_summary.append({
                                'Ticker': ticker,
                                'Quarter': f"Q{quarter}",
                                'Year': year,
                                'Status': f'❌ Failed: {str(e)[:50]}',
                                'File': 'N/A'
                            })
                    
                    progress_bar.progress((i + 1) / len(selected_transcripts))
                
                status_text.text("✅ Batch analysis complete!")
                
                # Show results summary
                import pandas as pd
                results_df = pd.DataFrame(results_summary)
                st.dataframe(results_df, use_container_width=True)
                
                success_count = sum(1 for r in results_summary if '✅' in r['Status'])
                st.success(f"Successfully analyzed {success_count}/{len(selected_transcripts)} transcripts")
    else:
        st.warning("⚠️ No transcripts available")

with tab3:
    st.header("View Analysis Results")
    
    # List saved results
    results_dir = "test-results"
    
    if os.path.exists(results_dir):
        result_files = [f for f in os.listdir(results_dir) if f.endswith(('.md', '.json'))]
        
        if result_files:
            st.info(f"📁 Found {len(result_files)} analysis results")
            
            selected_result = st.selectbox(
                "Select Result to View",
                sorted(result_files, reverse=True)
            )
            
            if st.button("👁️ View Result"):
                result_path = os.path.join(results_dir, selected_result)
                
                if selected_result.endswith('.json'):
                    with open(result_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    st.json(data)
                else:
                    with open(result_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    st.markdown(content)
        else:
            st.warning("⚠️ No analysis results found")
    else:
        st.warning("⚠️ Results directory not found")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Use the Agentic Workflow for comprehensive multi-step analysis with LangGraph")
