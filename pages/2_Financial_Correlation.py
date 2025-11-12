"""
Financial Correlation Page
Compare analyst estimates with actual results
"""

import streamlit as st
import os
from dotenv import load_dotenv
from utils.yfinance_client import YFinanceClient
from utils.data_correlator import DataCorrelator
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Financial Correlation",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Financial Data Correlation")
st.markdown("Compare analyst estimates with actual earnings results")

# Initialize clients
yf_client = YFinanceClient()
correlator = DataCorrelator()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Time period for price data
    price_period = st.selectbox(
        "Price Data Period",
        ["1mo", "3mo", "6mo", "1y", "2y"],
        index=2
    )
    
    st.markdown("---")
    
    st.header("📊 Display Options")
    
    show_estimates = st.checkbox("Show Analyst Estimates", value=True)
    show_recommendations = st.checkbox("Show Recommendations", value=True)
    show_price_chart = st.checkbox("Show Price Chart", value=True)
    show_surprise_metrics = st.checkbox("Show Surprise Metrics", value=True)

# Main content
tab1, tab2, tab3 = st.tabs(["🔍 Single Ticker Analysis", "📊 Comparison Dashboard", "📈 Surprise Analysis"])

with tab1:
    st.header("Analyze Single Ticker")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        ticker = st.text_input(
            "Ticker Symbol",
            placeholder="e.g., AAPL",
            help="Enter stock ticker symbol"
        ).upper()
    
    with col2:
        quarter = st.selectbox("Quarter", [1, 2, 3, 4], index=2, key="single_q")
    
    with col3:
        year = st.number_input("Year", min_value=2020, max_value=2025, value=2024, key="single_y")
    
    analyze_button = st.button("🔍 Analyze", type="primary")
    
    if analyze_button and ticker:
        with st.spinner(f"Fetching data for {ticker}..."):
            # Get company info
            company_info = yf_client.get_company_info(ticker)
            
            if company_info:
                st.success(f"✅ Found: {company_info.get('longName', ticker)}")
                
                # Company overview
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Sector", company_info.get('sector', 'N/A'))
                
                with col2:
                    st.metric("Industry", company_info.get('industry', 'N/A'))
                
                with col3:
                    market_cap = company_info.get('marketCap', 0)
                    if market_cap:
                        st.metric("Market Cap", f"${market_cap/1e9:.2f}B")
                    else:
                        st.metric("Market Cap", "N/A")
                
                with col4:
                    current_price = company_info.get('currentPrice', 0)
                    if current_price:
                        st.metric("Current Price", f"${current_price:.2f}")
                    else:
                        st.metric("Current Price", "N/A")
                
                st.markdown("---")
                
                # Analyst Estimates
                if show_estimates:
                    st.subheader("📊 Analyst Estimates")
                    
                    estimates = yf_client.get_analyst_estimates(ticker)
                    
                    if estimates:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if estimates.get('earnings_estimate'):
                                st.markdown("**Earnings Estimates**")
                                earnings_df = pd.DataFrame(estimates['earnings_estimate'])
                                if not earnings_df.empty:
                                    st.dataframe(earnings_df, use_container_width=True)
                                else:
                                    st.info("No earnings estimates available")
                        
                        with col2:
                            if estimates.get('revenue_estimate'):
                                st.markdown("**Revenue Estimates**")
                                revenue_df = pd.DataFrame(estimates['revenue_estimate'])
                                if not revenue_df.empty:
                                    st.dataframe(revenue_df, use_container_width=True)
                                else:
                                    st.info("No revenue estimates available")
                    else:
                        st.info("No analyst estimates available")
                    
                    st.markdown("---")
                
                # Analyst Recommendations
                if show_recommendations:
                    st.subheader("⭐ Analyst Recommendations")
                    
                    recommendations = yf_client.get_analyst_recommendations(ticker)
                    
                    if recommendations is not None and not recommendations.empty:
                        # Show recent recommendations
                        st.dataframe(recommendations.head(10), use_container_width=True)
                        
                        # Recommendation summary
                        rec_summary = correlator.get_recommendation_summary(ticker)
                        
                        if rec_summary:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Recommendations", rec_summary.get('total_recommendations', 0))
                            
                            with col2:
                                st.metric("Firms Covering", rec_summary.get('firms_covering', 0))
                            
                            with col3:
                                st.metric("Most Recent", rec_summary.get('most_recent_date', 'N/A')[:10])
                            
                            # Grade distribution chart
                            if rec_summary.get('grade_distribution'):
                                grade_df = pd.DataFrame(
                                    list(rec_summary['grade_distribution'].items()),
                                    columns=['Grade', 'Count']
                                )
                                
                                fig = px.bar(
                                    grade_df,
                                    x='Grade',
                                    y='Count',
                                    title='Recommendation Grade Distribution',
                                    color='Count',
                                    color_continuous_scale='Blues'
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No analyst recommendations available")
                    
                    st.markdown("---")
                
                # Price Chart
                if show_price_chart:
                    st.subheader("📈 Price Performance")
                    
                    price_data = yf_client.get_price_data(ticker, period=price_period)
                    
                    if price_data is not None and not price_data.empty:
                        # Create candlestick chart
                        fig = go.Figure(data=[go.Candlestick(
                            x=price_data.index,
                            open=price_data['Open'],
                            high=price_data['High'],
                            low=price_data['Low'],
                            close=price_data['Close']
                        )])
                        
                        fig.update_layout(
                            title=f'{ticker} Price Chart ({price_period})',
                            yaxis_title='Price ($)',
                            xaxis_title='Date',
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Price statistics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Current", f"${price_data['Close'].iloc[-1]:.2f}")
                        
                        with col2:
                            period_return = ((price_data['Close'].iloc[-1] / price_data['Close'].iloc[0]) - 1) * 100
                            st.metric("Period Return", f"{period_return:.2f}%")
                        
                        with col3:
                            st.metric("High", f"${price_data['High'].max():.2f}")
                        
                        with col4:
                            st.metric("Low", f"${price_data['Low'].min():.2f}")
                    else:
                        st.info("No price data available")
                    
                    st.markdown("---")
                
                # Surprise Metrics
                if show_surprise_metrics:
                    st.subheader("🎯 Earnings Surprise Metrics")
                    
                    surprise_metrics = correlator.calculate_surprise_metrics(ticker)
                    
                    if surprise_metrics:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Avg Surprise", f"{surprise_metrics.get('average_surprise', 0):.2f}%")
                        
                        with col2:
                            beat_rate = (surprise_metrics.get('beat_count', 0) / 
                                       surprise_metrics.get('total_quarters', 1)) * 100
                            st.metric("Beat Rate", f"{beat_rate:.1f}%")
                        
                        with col3:
                            st.metric("Max Surprise", f"{surprise_metrics.get('max_surprise', 0):.2f}%")
                        
                        with col4:
                            st.metric("Min Surprise", f"{surprise_metrics.get('min_surprise', 0):.2f}%")
                        
                        # Beat/Miss/Meet breakdown
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Beats", surprise_metrics.get('beat_count', 0), 
                                    delta="Positive", delta_color="normal")
                        
                        with col2:
                            st.metric("Meets", surprise_metrics.get('meet_count', 0),
                                    delta="Neutral", delta_color="off")
                        
                        with col3:
                            st.metric("Misses", surprise_metrics.get('miss_count', 0),
                                    delta="Negative", delta_color="inverse")
                    else:
                        st.info("No surprise metrics available")
                
                # Generate full correlation report
                st.markdown("---")
                
                if st.button("📄 Generate Full Correlation Report"):
                    with st.spinner("Generating report..."):
                        report = correlator.generate_correlation_report(ticker, quarter, year, "")
                        
                        st.markdown(report)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Report",
                            data=report,
                            file_name=f"{ticker}_Q{quarter}_{year}_correlation_report.md",
                            mime="text/markdown"
                        )
            else:
                st.error(f"❌ Could not fetch data for {ticker}")

with tab2:
    st.header("Comparison Dashboard")
    st.markdown("Compare multiple tickers side by side")
    
    # Multi-ticker input
    tickers_input = st.text_input(
        "Enter Tickers (comma-separated)",
        placeholder="e.g., AAPL, MSFT, GOOGL",
        help="Enter multiple tickers separated by commas"
    )
    
    if tickers_input:
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        
        if st.button("📊 Compare Tickers"):
            comparison_data = []
            
            progress_bar = st.progress(0)
            
            for i, ticker in enumerate(tickers):
                try:
                    info = yf_client.get_company_info(ticker)
                    surprise_metrics = correlator.calculate_surprise_metrics(ticker)
                    
                    if info:
                        comparison_data.append({
                            'Ticker': ticker,
                            'Company': info.get('longName', ticker)[:30],
                            'Sector': info.get('sector', 'N/A'),
                            'Market Cap ($B)': f"{info.get('marketCap', 0)/1e9:.2f}",
                            'Current Price': f"${info.get('currentPrice', 0):.2f}",
                            'Avg Surprise %': f"{surprise_metrics.get('average_surprise', 0):.2f}" if surprise_metrics else 'N/A',
                            'Beat Rate %': f"{(surprise_metrics.get('beat_count', 0) / surprise_metrics.get('total_quarters', 1) * 100):.1f}" if surprise_metrics else 'N/A'
                        })
                except:
                    pass
                
                progress_bar.progress((i + 1) / len(tickers))
            
            if comparison_data:
                df = pd.DataFrame(comparison_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("⚠️ No data available for comparison")

with tab3:
    st.header("Earnings Surprise Analysis")
    st.markdown("Analyze historical earnings surprises and their impact")
    
    ticker_surprise = st.text_input(
        "Ticker Symbol",
        placeholder="e.g., AAPL",
        key="surprise_ticker"
    ).upper()
    
    if st.button("📊 Analyze Surprises") and ticker_surprise:
        with st.spinner("Analyzing earnings surprises..."):
            comparison = yf_client.compare_estimates_vs_actual(ticker_surprise)
            
            if comparison and comparison.get('eps_surprise_percent'):
                # Create surprise chart
                surprise_df = pd.DataFrame({
                    'Date': comparison['dates'],
                    'EPS Estimate': comparison['eps_estimate'],
                    'EPS Actual': comparison['eps_actual'],
                    'Surprise %': comparison['eps_surprise_percent']
                })
                
                # Surprise percentage chart
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=surprise_df['Date'],
                    y=surprise_df['Surprise %'],
                    marker_color=['green' if x > 0 else 'red' for x in surprise_df['Surprise %']],
                    name='Surprise %'
                ))
                
                fig.update_layout(
                    title=f'{ticker_surprise} Earnings Surprise History',
                    xaxis_title='Date',
                    yaxis_title='Surprise %',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Estimate vs Actual chart
                fig2 = go.Figure()
                
                fig2.add_trace(go.Scatter(
                    x=surprise_df['Date'],
                    y=surprise_df['EPS Estimate'],
                    mode='lines+markers',
                    name='Estimate',
                    line=dict(color='blue', dash='dash')
                ))
                
                fig2.add_trace(go.Scatter(
                    x=surprise_df['Date'],
                    y=surprise_df['EPS Actual'],
                    mode='lines+markers',
                    name='Actual',
                    line=dict(color='green')
                ))
                
                fig2.update_layout(
                    title=f'{ticker_surprise} EPS: Estimate vs Actual',
                    xaxis_title='Date',
                    yaxis_title='EPS ($)',
                    height=400
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
                # Data table
                st.subheader("Detailed Surprise Data")
                st.dataframe(surprise_df, use_container_width=True)
            else:
                st.warning("⚠️ No surprise data available for this ticker")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Use the comparison dashboard to analyze multiple companies in the same sector")
