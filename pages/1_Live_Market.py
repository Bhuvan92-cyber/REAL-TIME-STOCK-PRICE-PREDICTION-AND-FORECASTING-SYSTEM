import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
import yfinance as yf

from modules.utils.helpers import load_dataframe
from modules.ingestion.live_data_fetcher import fetch_live_stock_data

try:
    from streamlit_autorefresh import st_autorefresh
    auto_refresh_available = True
except ImportError:
    auto_refresh_available = False

# Auto refresh every 60 seconds (if extension available)
if auto_refresh_available:
    st_autorefresh(interval=60000)

st.header("📊 Live Market View")

# Stock display names
STOCK_OPTIONS = {
    "AAPL": "Apple Inc. (NASDAQ)",
    "TCS": "Tata Consultancy Services (NSE)", 
    "NIFTY50": "NIFTY 50 Index (NSE)"
}

# Stock ticker mappings for yfinance
TICKER_MAP = {
    "AAPL": "AAPL",
    "TCS": "TCS.NS",
    "NIFTY50": "^NSEI"
}

# Selected stock from session
symbol = st.session_state.get("selected_stock", "AAPL")
stock_name = STOCK_OPTIONS.get(symbol, symbol)
ticker = TICKER_MAP.get(symbol, symbol)

# Stock banner
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
    # Fetch live or recent data based on stock
    if symbol == "AAPL":
        # For AAPL, try to fetch live intraday data
        df = fetch_live_stock_data(ticker, interval="1m", period="1d")
    else:
        # For TCS and NIFTY50, fetch 1-hour data
        df = fetch_live_stock_data(ticker, interval="1h", period="5d")
    
    if df.empty:
        st.warning(f"No live data available for {symbol}")
        st.stop()
    
    # Ensure lowercase columns
    df.columns = [c.lower() for c in df.columns]
    
    # Display latest 10 rows
    st.subheader("Latest Market Data")
    st.dataframe(df.tail(10), width="stretch", use_container_width=True)
    
    # Display key metrics
    st.subheader("Market Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    if "close" in df.columns:
        latest_close = df["close"].iloc[-1]
        col1.metric("Current Price", f"${latest_close:.2f}" if symbol == "AAPL" else f"₹{latest_close:.2f}")
        
        if "open" in df.columns:
            opening = df["open"].iloc[0]
            change = latest_close - opening
            col2.metric("Day Change", f"{change:.2f}", f"{(change/opening)*100:.2f}%")
        
        if "high" in df.columns:
            col3.metric("High", f"{df['high'].max():.2f}")
        
        if "low" in df.columns:
            col4.metric("Low", f"{df['low'].min():.2f}")
    
    # Price Trend Chart
    st.subheader("Price Trend")
    if "close" in df.columns:
        st.line_chart(df["close"])
    
    # Volume Chart
    if "volume" in df.columns:
        st.subheader("Trading Volume")
        st.bar_chart(df["volume"])

except Exception as e:
    st.error(f"❌ Error loading live market data for {symbol}")
    st.warning("Make sure you have internet connection and valid stock symbol.")
    with st.expander("Error Details"):
        st.write(str(e))
