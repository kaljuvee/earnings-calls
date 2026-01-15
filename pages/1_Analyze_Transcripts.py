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

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Analysis Settings")
    
    # LLM Provider selection with all supported providers
    provider_options = {
        "openai": "🔵 OpenAI (GPT-4, GPT-3.5)",
        "anthropic": "🟠 Anthropic (Claude)",
        "xai": "⚫ XAI (Grok)",
        "gemini": "🔴 Google (Gemini)",
        "groq": "🟣 Groq (LLaMA)",
        "together_ai": "🟢 Together AI",
        "openrouter": "🟡 OpenRouter"
    }
    
    llm_provider = st.selectbox(
        "LLM Provider",
        options=list(provider_options.keys()),
        format_func=lambda x: provider_options[x],
        help="Select the LLM provider for analysis"
    )
    
    # API Key input field
    st.markdown("---")
    st.subheader("🔑 API Configuration")
    
    # Map provider to environment variable names
    env_var_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "xai": "XAI_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "together_ai": "TOGETHER_AI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY"
    }
    
    env_var_name = env_var_map.get(llm_provider, "")
    default_api_key = os.getenv(env_var_name, "")
    
    api_key_input = st.text_input(
        f"API Key ({llm_provider.upper()})",
        value=default_api_key,
        type="password",
        help=f"Enter your {llm_provider.upper()} API key. If left empty, will use environment variable {env_var_name}"
    )
    
    # Use provided API key or fall back to environment variable
    api_key = api_key_input if api_key_input else default_api_key
    
    if not api_key:
        st.warning(f"⚠️ No API key provided for {llm_provider.upper()}. Please enter one above or set {env_var_name} environment variable.")
    
    # Model selection based on provider
    st.markdown("---")
    st.subheader("🤖 Model Selection")
    
    model_options = {
        "openai": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "xai": ["grok-3", "grok-2", "grok-1"],
        "gemini": ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"],
        "groq": ["mixtral-8x7b-32768", "llama2-70b-4096", "llama-3-70b-8192"],
        "together_ai": ["meta-llama/Llama-2-70b-chat-hf", "meta-llama/Llama-3-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
        "openrouter": ["openai/gpt-4-turbo", "anthropic/claude-3-opus", "meta-llama/llama-3-70b-instruct"]
    }
    
    available_models = model_options.get(llm_provider, ["default"])
    
    model = st.selectbox(
        "Model",
        available_models,
        help=f"Select the {llm_provider.upper()} model to use"
    )
    
    # Analysis type
    st.markdown("---")
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Standard Analysis", "Agentic Workflow", "Quick Summary"],
        help="Choose the type of analysis to run"
    )
    
    st.markdown("---")
    
    st.header("📊 Analysis Options")
    
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
        # Validate API key
        if not api_key:
            st.error(f"❌ Please provide an API key for {llm_provider.upper()}")
            st.stop()
        
        # Read full transcript
        file_path = os.path.join(transcript_dir, selected_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        # Initialize clients
        try:
            llm_client = LLMClient(provider=llm_provider, model=model, api_key=api_key)
            correlator = DataCorrelator()
        except Exception as e:
            st.error(f"❌ Failed to initialize LLM client: {str(e)}")
            st.stop()
        
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
                    
                    # Predictive signals
                    if include_predictions and results.get('predictive_signals'):
                        st.markdown("---")
                        st.markdown("## 🎯 Predictive Signals")
                        st.markdown(results.get('predictive_signals', ''))
                    
                    # Save results in both JSON and MD formats
                    analyses_dir = "analyses"
                    os.makedirs(analyses_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_filename = f"{ticker}_Q{quarter}_{year}_agentic_{timestamp}"
                    
                    # Prepare full report markdown
                    full_report = results.get('final_report', '')
                    if not full_report:
                        # Combine all sections if final_report not available
                        full_report = results.get('main_analysis', '')
                        if include_predictions and results.get('predictive_signals'):
                            full_report += "\n\n---\n\n## 🎯 Predictive Signals\n\n" + results.get('predictive_signals', '')
                    
                    # Save as Markdown
                    md_file = f"{base_filename}.md"
                    md_path = os.path.join(analyses_dir, md_file)
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(full_report)
                    
                    # Save as JSON with metadata
                    json_file = f"{base_filename}.json"
                    json_path = os.path.join(analyses_dir, json_file)
                    analysis_data = {
                        'ticker': ticker,
                        'quarter': quarter,
                        'year': year,
                        'company_name': ticker,
                        'timestamp': timestamp,
                        'provider': llm_provider,
                        'model': model,
                        'analysis_type': 'Agentic Workflow',
                        'results': results,
                        'full_report_markdown': full_report,
                        'financial_context_included': include_financial_context,
                        'predictions_included': include_predictions
                    }
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(analysis_data, f, indent=2)
                    
                    st.success(f"💾 Results saved to: `{md_path}` and `{json_path}`")
                    
                    # Download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download Markdown",
                            data=full_report,
                            file_name=f"{ticker}_Q{quarter}_{year}_report.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    with col2:
                        st.download_button(
                            label="📥 Download JSON",
                            data=json.dumps(analysis_data, indent=2),
                            file_name=f"{ticker}_Q{quarter}_{year}_report.json",
                            mime="application/json",
                            use_container_width=True
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
                    
                    # Extract score from analysis
                    from utils.score_extractor import extract_score_from_analysis, get_score_label, get_expected_movement_range
                    score, score_justification = extract_score_from_analysis(analysis)
                    
                    # Display analysis
                    st.markdown("## 📊 Analysis")
                    st.markdown(analysis)
                    
                    # Display score
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Score", f"{score}/5")
                    
                    with col2:
                        label = get_score_label(score)
                        st.metric("Label", label)
                    
                    with col3:
                        movement_range = get_expected_movement_range(score)
                        st.metric("Expected Movement", movement_range)
                    
                    # Display justification
                    st.markdown("### Score Justification")
                    st.markdown(score_justification)
                    
                    # Save results
                    analyses_dir = "analyses"
                    os.makedirs(analyses_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_filename = f"{ticker}_Q{quarter}_{year}_standard_{timestamp}"
                    
                    # Save as Markdown
                    md_file = f"{base_filename}.md"
                    md_path = os.path.join(analyses_dir, md_file)
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Analysis for {ticker} Q{quarter} {year}\n\n")
                        f.write(f"**Score:** {score}/5 ({get_score_label(score)})\n\n")
                        f.write(f"**Expected Movement:** {movement_range}\n\n")
                        f.write(f"## Analysis\n\n{analysis}\n\n")
                        f.write(f"## Score Justification\n\n{score_justification}\n")
                    
                    # Save as JSON
                    json_file = f"{base_filename}.json"
                    json_path = os.path.join(analyses_dir, json_file)
                    analysis_data = {
                        'ticker': ticker,
                        'quarter': quarter,
                        'year': year,
                        'timestamp': timestamp,
                        'provider': llm_provider,
                        'model': model,
                        'analysis_type': 'Standard Analysis',
                        'score': score,
                        'label': get_score_label(score),
                        'expected_movement': movement_range,
                        'analysis': analysis,
                        'score_justification': score_justification
                    }
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(analysis_data, f, indent=2)
                    
                    st.success(f"💾 Results saved to: `{md_path}` and `{json_path}`")
                    
                    # Download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download Markdown",
                            data=open(md_path, 'r').read(),
                            file_name=f"{ticker}_Q{quarter}_{year}_report.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    with col2:
                        st.download_button(
                            label="📥 Download JSON",
                            data=json.dumps(analysis_data, indent=2),
                            file_name=f"{ticker}_Q{quarter}_{year}_report.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.exception(e)

with tab2:
    st.header("Batch Analysis")
    st.markdown("Analyze multiple transcripts at once")
    
    # Get list of available transcripts
    transcript_dir = "transcripts"
    transcript_files = []
    
    if os.path.exists(transcript_dir):
        transcript_files = [f for f in os.listdir(transcript_dir) if f.endswith('.md')]
    
    if not transcript_files:
        st.warning("⚠️ No transcripts available. Please download transcripts first.")
    else:
        # Multi-select for transcripts
        selected_transcripts = st.multiselect(
            "Select Transcripts to Analyze",
            transcript_files,
            help="Choose multiple transcripts to analyze in batch"
        )
        
        if st.button("📦 Run Batch Analysis", type="primary", use_container_width=True):
            if not selected_transcripts:
                st.warning("Please select at least one transcript")
            elif not api_key:
                st.error(f"❌ Please provide an API key for {llm_provider.upper()}")
            else:
                # Initialize clients
                try:
                    llm_client = LLMClient(provider=llm_provider, model=model, api_key=api_key)
                    correlator = DataCorrelator()
                except Exception as e:
                    st.error(f"❌ Failed to initialize LLM client: {str(e)}")
                    st.stop()
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_summary = []
                
                for i, selected_file in enumerate(selected_transcripts):
                    status_text.text(f"Processing {selected_file}... ({i+1}/{len(selected_transcripts)})")
                    
                    try:
                        # Parse filename
                        parts = selected_file.replace('.md', '').split('_')
                        if len(parts) >= 3:
                            ticker = parts[0]
                            quarter = int(parts[1].replace('Q', ''))
                            year = int(parts[2])
                            
                            # Read transcript
                            file_path = os.path.join(transcript_dir, selected_file)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                transcript = f.read()
                            
                            # Get financial context if requested
                            financial_context = ""
                            if include_financial_context:
                                financial_context = correlator.generate_financial_context(ticker, quarter, year)
                            
                            # Run analysis
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
                            'Ticker': selected_file,
                            'Quarter': 'N/A',
                            'Year': 'N/A',
                            'Status': f'❌ Failed: {str(e)[:50]}',
                            'File': 'N/A'
                        })
                    
                    progress_bar.progress((i + 1) / len(selected_transcripts))
                
                status_text.text("✅ Batch analysis complete!")
                
                # Display results
                st.subheader("Batch Analysis Results")
                st.dataframe(results_summary, use_container_width=True)

with tab3:
    st.header("View Analysis Results")
    
    results_dir = "analyses"
    
    if os.path.exists(results_dir):
        result_files = [f for f in os.listdir(results_dir) if f.endswith('.md') or f.endswith('.json')]
        
        if not result_files:
            st.info("No analysis results found")
        else:
            st.success(f"Found {len(result_files)} result file(s)")
            
            # Filter by file type
            file_type = st.selectbox("Filter by file type", ["All", "Markdown (.md)", "JSON (.json)"])
            
            if file_type == "Markdown (.md)":
                result_files = [f for f in result_files if f.endswith('.md')]
            elif file_type == "JSON (.json)":
                result_files = [f for f in result_files if f.endswith('.json')]
            
            # Select result to view
            selected_result = st.selectbox("Select a result to view", result_files)
            
            if selected_result:
                result_path = os.path.join(results_dir, selected_result)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(selected_result)
                with col2:
                    # Download button
                    with open(result_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    st.download_button(
                        "📥 Download",
                        content,
                        file_name=selected_result,
                        mime="text/markdown" if selected_result.endswith('.md') else "application/json",
                        use_container_width=True
                    )
                
                # Display content
                if selected_result.endswith('.json'):
                    with open(result_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    st.json(data)
                else:
                    with open(result_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    st.markdown(content)
    else:
        st.warning("⚠️ Results directory not found")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Use the Agentic Workflow for comprehensive multi-step analysis with LangGraph")
st.markdown("""
---

<div style="text-align: center; margin-top: 2rem; color: #888;">
    <p>Built by <a href="https://kaljuvee.github.io" target="_blank"><strong>Julian Kaljuvee</strong></a></p>
    <p><a href="https://github.com/kaljuvee/earnings-calls" target="_blank">📌 GitHub Repository</a></p>
</div>
""", unsafe_allow_html=True)
