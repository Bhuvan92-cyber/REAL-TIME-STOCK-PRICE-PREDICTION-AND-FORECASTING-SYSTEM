import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd

from modules.risk_management import (
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_volatility_risk
)
from modules.ingestion.live_data_fetcher import fetch_live_stock_data

st.header("⚠️ Risk Analysis Dashboard")

STOCK_OPTIONS = {
    "AAPL": "Apple Inc. (NASDAQ)",
    "TCS": "Tata Consultancy Services (NSE)",
    "NIFTY50": "NIFTY 50 Index (NSE)"
}

TICKER_MAP = {
    "AAPL": "AAPL",
    "TCS": "TCS.NS",
    "NIFTY50": "^NSEI"
}

symbol = st.session_state.get("selected_stock", "AAPL")
stock_name = STOCK_OPTIONS.get(symbol, symbol)
ticker = TICKER_MAP.get(symbol, symbol)

st.markdown(
    f"""
    <div style="
        padding: 10px;
        border-radius: 8px;
        background-color: #1f2933;
        color: white;
        font-size: 18px;
        margin-bottom: 15px;
    ">
        📈 <b>Stock Selected:</b> {symbol} — {stock_name}
    </div>
    """,
    unsafe_allow_html=True
)

try:
    # Load historical data
    df = fetch_live_stock_data(ticker, interval="1d", period="2y")
    
    # Normalize columns
    df.columns = [c.lower() for c in df.columns]
    
    if "close" not in df.columns:
        st.error("Dataset must contain 'close' column")
        st.stop()
    
    # Calculate returns
    returns = df["close"].pct_change().dropna()
    
    if len(returns) == 0:
        st.error("Insufficient data for risk analysis")
        st.stop()
    
    # Calculate risk metrics
    sharpe = calculate_sharpe_ratio(returns)
    volatility = calculate_volatility_risk(returns)
    
    # For max drawdown, calculate cumulative returns
    cumulative_returns = (1 + returns).cumprod() - 1
    max_dd = calculate_max_drawdown(cumulative_returns)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        "Sharpe Ratio",
        round(sharpe, 3),
        help="Higher is better. Measures risk-adjusted returns."
    )
    col2.metric(
        "Volatility Risk",
        round(volatility, 3),
        help="Standard deviation of returns. Lower is less risky."
    )
    col3.metric(
        "Max Drawdown",
        round(max_dd, 3),
        help="Maximum loss from peak. Negative values indicate decline."
    )
    
    # Risk assessment
    st.subheader("🔍 Risk Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Volatility Level:**")
        if volatility < 0.01:
            st.success("✅ Low Risk")
        elif volatility < 0.02:
            st.info("⚠️ Moderate Risk")
        else:
            st.warning("🔴 High Risk")
    
    with col2:
        st.write("**Sharpe Ratio:**")
        if sharpe > 1:
            st.success("✅ Good Risk-Adjusted Returns")
        elif sharpe > 0:
            st.info("⚠️ Fair Risk-Adjusted Returns")
        else:
            st.warning("🔴 Poor Risk-Adjusted Returns")
    
    # Daily returns distribution
    st.subheader("📊 Returns Distribution")
    st.area_chart(returns)
    
    # Risk metrics table
    st.subheader("📈 Detailed Risk Metrics")
    metrics_df = pd.DataFrame({
        "Metric": ["Mean Return", "Std Dev", "Sharpe Ratio", "Max Drawdown", "Min Return", "Max Return"],
        "Value": [
            round(returns.mean(), 4),
            round(returns.std(), 4),
            round(sharpe, 4),
            round(max_dd, 4),
            round(returns.min(), 4),
            round(returns.max(), 4)
        ]
    })
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("❌ Risk metrics not available")
    with st.expander("Error Details"):
        st.write(str(e))
