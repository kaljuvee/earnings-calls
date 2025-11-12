"""
Score-Price Movement Correlations Page
Shows correlation between analysis scores and actual stock price movements
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.db_util import DatabaseUtil
import os

st.set_page_config(page_title="Correlations", page_icon="📈", layout="wide")

st.title("📈 Score-Price Movement Correlations")
st.markdown("Analyze the correlation between earnings analysis scores and actual stock price movements.")

# Initialize database
db = DatabaseUtil()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Get all tickers
all_tickers = db.get_all_tickers()

if not all_tickers:
    st.warning("⚠️ No analysis scores found in database. Please run some analyses first.")
    st.info("💡 Go to **Analyze Transcripts** page to generate analyses with scores.")
    st.stop()

# Ticker filter
ticker_filter = st.sidebar.selectbox(
    "Ticker",
    ["All"] + all_tickers,
    help="Filter by specific ticker or view all"
)

# Period filter
period_filter = st.sidebar.selectbox(
    "Time Period",
    [1, 3, 5, 10],
    format_func=lambda x: f"{x} Day{'s' if x > 1 else ''}",
    help="Number of days after earnings to measure price movement"
)

st.sidebar.markdown("---")

# Load data
ticker_param = None if ticker_filter == "All" else ticker_filter
df = db.get_score_price_correlation(ticker_param)

if df.empty:
    st.warning(f"⚠️ No data found for {ticker_filter if ticker_filter != 'All' else 'any ticker'}.")
    st.stop()

# Select movement column based on period
movement_col = f'movement_{period_filter}d_pct'

# Filter out rows with missing price data
df_clean = df[df[movement_col].notna()].copy()

if df_clean.empty:
    st.warning(f"⚠️ No price movement data available for {period_filter} day period.")
    st.info("💡 Price movements need to be fetched and stored in the database.")
    st.stop()

# Main metrics
st.header("📊 Overall Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Analyses", len(df_clean))

with col2:
    correlation, sample_size = db.calculate_correlation(ticker_param, period_filter)
    st.metric("Correlation", f"{correlation:.3f}")

with col3:
    avg_score = df_clean['score'].mean()
    st.metric("Avg Score", f"{avg_score:.2f}")

with col4:
    avg_movement = df_clean[movement_col].mean()
    st.metric(f"Avg {period_filter}D Move", f"{avg_movement:.2f}%")

st.markdown("---")

# Scatter plot
st.header("📈 Score vs Price Movement")

fig = px.scatter(
    df_clean,
    x='score',
    y=movement_col,
    color='ticker' if ticker_filter == "All" else None,
    hover_data=['ticker', 'quarter', 'year', 'earnings_date', 'provider'],
    labels={
        'score': 'Analysis Score',
        movement_col: f'{period_filter}-Day Price Movement (%)',
        'ticker': 'Ticker'
    },
    title=f"Analysis Score vs {period_filter}-Day Price Movement",
    trendline="ols"
)

fig.update_layout(
    height=500,
    xaxis=dict(range=[-5.5, 5.5], dtick=1),
    showlegend=True if ticker_filter == "All" else False
)

st.plotly_chart(fig, use_container_width=True)

# Correlation by score bucket
st.header("📊 Performance by Score Range")

# Create score buckets
df_clean['score_bucket'] = pd.cut(
    df_clean['score'],
    bins=[-6, -3, -1, 1, 3, 6],
    labels=['Very Bearish (-5 to -3)', 'Bearish (-2 to -1)', 'Neutral (0 to 1)', 'Bullish (2 to 3)', 'Very Bullish (4 to 5)']
)

bucket_stats = df_clean.groupby('score_bucket', observed=True).agg({
    movement_col: ['mean', 'std', 'count'],
    'score': 'mean'
}).round(2)

bucket_stats.columns = ['Avg Movement (%)', 'Std Dev (%)', 'Count', 'Avg Score']
bucket_stats = bucket_stats.reset_index()

# Bar chart
fig_bar = px.bar(
    bucket_stats,
    x='score_bucket',
    y='Avg Movement (%)',
    error_y='Std Dev (%)',
    text='Count',
    labels={'score_bucket': 'Score Range'},
    title=f"Average {period_filter}-Day Price Movement by Score Range",
    color='Avg Movement (%)',
    color_continuous_scale='RdYlGn'
)

fig_bar.update_traces(texttemplate='n=%{text}', textposition='outside')
fig_bar.update_layout(height=400)

st.plotly_chart(fig_bar, use_container_width=True)

# Detailed table
st.header("📋 Detailed Analysis Data")

# Prepare display dataframe
display_df = df_clean[[
    'ticker', 'quarter', 'year', 'earnings_date', 'score', 
    movement_col, 'provider', 'model', 'score_justification'
]].copy()

display_df.columns = [
    'Ticker', 'Quarter', 'Year', 'Earnings Date', 'Score',
    f'{period_filter}D Movement (%)', 'Provider', 'Model', 'Justification'
]

# Sort by earnings date descending
display_df = display_df.sort_values('Earnings Date', ascending=False)

# Color code scores
def color_score(val):
    if val >= 3:
        return 'background-color: #90EE90'  # Light green
    elif val >= 1:
        return 'background-color: #FFFFCC'  # Light yellow
    elif val >= -1:
        return 'background-color: #FFE4B5'  # Light orange
    else:
        return 'background-color: #FFB6C1'  # Light red

def color_movement(val):
    if val >= 5:
        return 'background-color: #90EE90'
    elif val >= 2:
        return 'background-color: #FFFFCC'
    elif val >= -2:
        return 'background-color: #FFE4B5'
    else:
        return 'background-color: #FFB6C1'

# Apply styling
styled_df = display_df.style.applymap(
    color_score, subset=['Score']
).applymap(
    color_movement, subset=[f'{period_filter}D Movement (%)']
).format({
    f'{period_filter}D Movement (%)': '{:.2f}%',
    'Score': '{:.0f}'
})

st.dataframe(styled_df, use_container_width=True, height=400)

# Download button
csv = display_df.to_csv(index=False)
st.download_button(
    label="📥 Download Data as CSV",
    data=csv,
    file_name=f"score_correlation_{ticker_filter}_{period_filter}d.csv",
    mime="text/csv"
)

# Accuracy metrics
st.header("🎯 Prediction Accuracy")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Direction Accuracy")
    
    # Calculate direction accuracy
    df_clean['score_direction'] = df_clean['score'].apply(lambda x: 'Up' if x > 0 else ('Down' if x < 0 else 'Neutral'))
    df_clean['actual_direction'] = df_clean[movement_col].apply(lambda x: 'Up' if x > 0 else ('Down' if x < 0 else 'Neutral'))
    df_clean['correct_direction'] = df_clean['score_direction'] == df_clean['actual_direction']
    
    accuracy = (df_clean['correct_direction'].sum() / len(df_clean) * 100)
    
    st.metric("Direction Accuracy", f"{accuracy:.1f}%")
    
    # Confusion matrix
    confusion = pd.crosstab(
        df_clean['score_direction'],
        df_clean['actual_direction'],
        rownames=['Predicted'],
        colnames=['Actual']
    )
    
    st.dataframe(confusion, use_container_width=True)

with col2:
    st.subheader("Magnitude Accuracy")
    
    # Calculate mean absolute error
    df_clean['expected_movement'] = df_clean['score'] * 2  # Rough estimate: score * 2%
    df_clean['error'] = abs(df_clean[movement_col] - df_clean['expected_movement'])
    
    mae = df_clean['error'].mean()
    st.metric("Mean Absolute Error", f"{mae:.2f}%")
    
    # Error distribution
    st.write("**Error Distribution:**")
    error_stats = df_clean['error'].describe().round(2)
    st.dataframe(error_stats, use_container_width=True)

# Insights
st.markdown("---")
st.header("💡 Insights")

if correlation > 0.5:
    st.success(f"✅ **Strong positive correlation** ({correlation:.3f}) between scores and price movements. The analysis scores are good predictors of price direction.")
elif correlation > 0.3:
    st.info(f"📊 **Moderate positive correlation** ({correlation:.3f}) between scores and price movements. Scores show some predictive power.")
elif correlation > 0:
    st.warning(f"⚠️ **Weak positive correlation** ({correlation:.3f}) between scores and price movements. Limited predictive power.")
else:
    st.error(f"❌ **Negative or no correlation** ({correlation:.3f}) between scores and price movements. Scores may need recalibration.")

if accuracy > 70:
    st.success(f"✅ **High direction accuracy** ({accuracy:.1f}%). The model correctly predicts price direction most of the time.")
elif accuracy > 50:
    st.info(f"📊 **Moderate direction accuracy** ({accuracy:.1f}%). Better than random but room for improvement.")
else:
    st.warning(f"⚠️ **Low direction accuracy** ({accuracy:.1f}%). Model needs improvement or more data.")
