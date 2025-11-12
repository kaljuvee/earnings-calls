"""
View Results Page
Browse and explore analysis results
"""

import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="View Results",
    page_icon="📊",
    layout="wide"
)

st.title("📊 View Analysis Results")
st.markdown("Browse and explore earnings call analysis results")

# Sidebar
with st.sidebar:
    st.header("🔍 Filters")
    
    # Filter by ticker
    filter_ticker = st.text_input(
        "Filter by Ticker",
        placeholder="e.g., AAPL",
        help="Filter results by ticker symbol"
    ).upper()
    
    # Filter by year
    filter_year = st.selectbox(
        "Filter by Year",
        ["All", "2025", "2024", "2023", "2022"],
        index=0
    )
    
    # Filter by file type
    filter_type = st.selectbox(
        "File Type",
        ["All", "Markdown (.md)", "JSON (.json)"],
        index=0
    )
    
    st.markdown("---")
    
    # Sort options
    sort_by = st.selectbox(
        "Sort By",
        ["Most Recent", "Oldest First", "Ticker (A-Z)", "Ticker (Z-A)"],
        index=0
    )

# Main content
tab1, tab2, tab3 = st.tabs(["📁 Browse Results", "📊 Results Dashboard", "🔍 Search & Compare"])

with tab1:
    st.header("Browse Analysis Results")
    
    results_dir = "test-results"
    
    if not os.path.exists(results_dir):
        st.warning("⚠️ Results directory not found. Run some analyses first!")
        st.stop()
    
    # Get all result files
    all_files = os.listdir(results_dir)
    
    # Apply filters
    filtered_files = []
    
    for filename in all_files:
        # Filter by type
        if filter_type == "Markdown (.md)" and not filename.endswith('.md'):
            continue
        if filter_type == "JSON (.json)" and not filename.endswith('.json'):
            continue
        
        # Filter by ticker
        if filter_ticker and not filename.upper().startswith(filter_ticker):
            continue
        
        # Filter by year
        if filter_year != "All" and filter_year not in filename:
            continue
        
        filtered_files.append(filename)
    
    if not filtered_files:
        st.info("No results found matching the filters")
        st.stop()
    
    # Sort files
    if sort_by == "Most Recent":
        filtered_files.sort(reverse=True)
    elif sort_by == "Oldest First":
        filtered_files.sort()
    elif sort_by == "Ticker (A-Z)":
        filtered_files.sort()
    elif sort_by == "Ticker (Z-A)":
        filtered_files.sort(reverse=True)
    
    st.info(f"📁 Found {len(filtered_files)} results")
    
    # Create a table of results
    results_data = []
    
    for filename in filtered_files:
        file_path = os.path.join(results_dir, filename)
        file_size = os.path.getsize(file_path)
        file_mtime = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        # Parse filename to extract metadata
        parts = filename.replace('.md', '').replace('.json', '').split('_')
        
        ticker = parts[0] if len(parts) > 0 else 'Unknown'
        quarter = parts[1] if len(parts) > 1 else 'N/A'
        year = parts[2] if len(parts) > 2 else 'N/A'
        
        results_data.append({
            'Ticker': ticker,
            'Quarter': quarter,
            'Year': year,
            'Filename': filename,
            'Type': 'Markdown' if filename.endswith('.md') else 'JSON',
            'Size (KB)': f"{file_size/1024:.1f}",
            'Modified': file_date
        })
    
    # Display table
    df = pd.DataFrame(results_data)
    st.dataframe(df, use_container_width=True)
    
    # Select and view result
    st.markdown("---")
    st.subheader("View Result")
    
    selected_file = st.selectbox(
        "Select a result to view",
        filtered_files,
        key="view_result"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        view_button = st.button("👁️ View", type="primary", use_container_width=True)
    
    with col2:
        if selected_file:
            file_path = os.path.join(results_dir, selected_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            st.download_button(
                label="📥 Download",
                data=content,
                file_name=selected_file,
                mime="text/markdown" if selected_file.endswith('.md') else "application/json",
                use_container_width=True
            )
    
    if view_button and selected_file:
        st.markdown("---")
        
        file_path = os.path.join(results_dir, selected_file)
        
        if selected_file.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Display JSON with nice formatting
            st.subheader(f"📄 {selected_file}")
            
            # Show metadata if available
            if 'ticker' in data:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Ticker", data.get('ticker', 'N/A'))
                
                with col2:
                    st.metric("Quarter", f"Q{data.get('quarter', 'N/A')}")
                
                with col3:
                    st.metric("Year", data.get('year', 'N/A'))
                
                with col4:
                    st.metric("Provider", data.get('provider', 'N/A'))
            
            st.markdown("---")
            
            # Display results
            if 'results' in data:
                results = data['results']
                
                if 'main_analysis' in results:
                    st.markdown("## 📊 Main Analysis")
                    st.markdown(results['main_analysis'])
                
                if 'sentiment_analysis' in results:
                    st.markdown("---")
                    st.markdown("## 😊 Sentiment Analysis")
                    st.markdown(results['sentiment_analysis'])
                
                if 'predictive_signals' in results:
                    st.markdown("---")
                    st.markdown("## 🎯 Predictive Signals")
                    st.markdown(results['predictive_signals'])
            else:
                st.json(data)
        
        else:  # Markdown file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            st.subheader(f"📄 {selected_file}")
            st.markdown("---")
            st.markdown(content)

with tab2:
    st.header("Results Dashboard")
    st.markdown("Overview of all analysis results")
    
    if not os.path.exists(results_dir):
        st.warning("⚠️ No results directory found")
        st.stop()
    
    all_files = os.listdir(results_dir)
    
    if not all_files:
        st.info("No results available yet")
        st.stop()
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Results", len(all_files))
    
    with col2:
        md_count = sum(1 for f in all_files if f.endswith('.md'))
        st.metric("Markdown Files", md_count)
    
    with col3:
        json_count = sum(1 for f in all_files if f.endswith('.json'))
        st.metric("JSON Files", json_count)
    
    with col4:
        total_size = sum(os.path.getsize(os.path.join(results_dir, f)) for f in all_files)
        st.metric("Total Size", f"{total_size/1024/1024:.2f} MB")
    
    st.markdown("---")
    
    # Parse all files to get statistics
    ticker_counts = {}
    year_counts = {}
    
    for filename in all_files:
        parts = filename.replace('.md', '').replace('.json', '').split('_')
        
        if len(parts) > 0:
            ticker = parts[0]
            ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
        
        if len(parts) > 2:
            year = parts[2]
            year_counts[year] = year_counts.get(year, 0) + 1
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if ticker_counts:
            st.subheader("Results by Ticker")
            
            ticker_df = pd.DataFrame(
                list(ticker_counts.items()),
                columns=['Ticker', 'Count']
            ).sort_values('Count', ascending=False)
            
            st.bar_chart(ticker_df.set_index('Ticker'))
    
    with col2:
        if year_counts:
            st.subheader("Results by Year")
            
            year_df = pd.DataFrame(
                list(year_counts.items()),
                columns=['Year', 'Count']
            ).sort_values('Year')
            
            st.bar_chart(year_df.set_index('Year'))
    
    # Recent results
    st.markdown("---")
    st.subheader("Recent Results")
    
    # Get 10 most recent files
    files_with_time = []
    for filename in all_files:
        file_path = os.path.join(results_dir, filename)
        mtime = os.path.getmtime(file_path)
        files_with_time.append((filename, mtime))
    
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    recent_files = [f[0] for f in files_with_time[:10]]
    
    recent_data = []
    for filename in recent_files:
        file_path = os.path.join(results_dir, filename)
        file_mtime = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        parts = filename.replace('.md', '').replace('.json', '').split('_')
        ticker = parts[0] if len(parts) > 0 else 'Unknown'
        
        recent_data.append({
            'Ticker': ticker,
            'Filename': filename,
            'Modified': file_date
        })
    
    recent_df = pd.DataFrame(recent_data)
    st.dataframe(recent_df, use_container_width=True)

with tab3:
    st.header("Search & Compare")
    st.markdown("Search through results and compare analyses")
    
    # Search functionality
    search_query = st.text_input(
        "🔍 Search in results",
        placeholder="Enter keywords to search...",
        help="Search through all analysis results"
    )
    
    if search_query:
        st.info(f"Searching for: '{search_query}'")
        
        search_results = []
        
        for filename in os.listdir(results_dir):
            file_path = os.path.join(results_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if search_query.lower() in content.lower():
                    # Count occurrences
                    count = content.lower().count(search_query.lower())
                    
                    # Get context (first occurrence)
                    idx = content.lower().find(search_query.lower())
                    context_start = max(0, idx - 100)
                    context_end = min(len(content), idx + 100)
                    context = content[context_start:context_end]
                    
                    search_results.append({
                        'Filename': filename,
                        'Occurrences': count,
                        'Context': context
                    })
            except:
                pass
        
        if search_results:
            st.success(f"✅ Found {len(search_results)} results")
            
            for result in search_results:
                with st.expander(f"📄 {result['Filename']} ({result['Occurrences']} occurrences)"):
                    st.text(result['Context'])
                    
                    if st.button(f"View Full File", key=f"view_{result['Filename']}"):
                        file_path = os.path.join(results_dir, result['Filename'])
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        st.markdown("---")
                        st.markdown(content)
        else:
            st.warning("No results found")
    
    # Compare functionality
    st.markdown("---")
    st.subheader("Compare Analyses")
    
    all_files = os.listdir(results_dir) if os.path.exists(results_dir) else []
    
    if len(all_files) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            file1 = st.selectbox("Select first result", all_files, key="compare1")
        
        with col2:
            file2 = st.selectbox("Select second result", all_files, key="compare2")
        
        if st.button("🔄 Compare"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"📄 {file1}")
                file_path1 = os.path.join(results_dir, file1)
                
                with open(file_path1, 'r', encoding='utf-8') as f:
                    content1 = f.read()
                
                if file1.endswith('.json'):
                    data1 = json.loads(content1)
                    if 'results' in data1 and 'main_analysis' in data1['results']:
                        st.markdown(data1['results']['main_analysis'][:2000] + "...")
                    else:
                        st.json(data1)
                else:
                    st.markdown(content1[:2000] + "...")
            
            with col2:
                st.subheader(f"📄 {file2}")
                file_path2 = os.path.join(results_dir, file2)
                
                with open(file_path2, 'r', encoding='utf-8') as f:
                    content2 = f.read()
                
                if file2.endswith('.json'):
                    data2 = json.loads(content2)
                    if 'results' in data2 and 'main_analysis' in data2['results']:
                        st.markdown(data2['results']['main_analysis'][:2000] + "...")
                    else:
                        st.json(data2)
                else:
                    st.markdown(content2[:2000] + "...")
    else:
        st.info("Need at least 2 results to compare")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Use the search functionality to find specific themes or keywords across all analyses")
