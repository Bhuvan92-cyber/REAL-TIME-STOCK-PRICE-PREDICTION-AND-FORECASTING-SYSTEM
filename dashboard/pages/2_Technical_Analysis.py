import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd

from modules.ingestion.live_data_fetcher import fetch_live_stock_data

st.header("📐 Technical Analysis")

# Stock Names
STOCK_OPTIONS = {
    "AAPL": "Apple Inc. (NASDAQ)",
    "TCS": "Tata Consultancy Services (NSE)",
    "NIFTY50": "NIFTY 50 Index (NSE)"
}

# Ticker Mappings
TICKER_MAP = {
    "AAPL": "AAPL",
    "TCS": "TCS.NS",
    "NIFTY50": "^NSEI"
}

# Selected Stock
symbol = st.session_state.get("selected_stock", "AAPL")
stock_name = STOCK_OPTIONS.get(symbol, symbol)
ticker = TICKER_MAP.get(symbol, symbol)

# Stock Banner
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
    # Load live data for the selected stock
    if symbol == "AAPL":
        df = fetch_live_stock_data(ticker, interval="1h", period="3mo")
    else:
        df = fetch_live_stock_data(ticker, interval="1d", period="2y")

    # Fix column format
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [c.lower() for c in df.columns]
    
    if "close" not in df.columns:
        st.error("Dataset must contain a 'close' column")
        st.stop()

    # Technical Indicators
    df["sma_20"] = df["close"].rolling(window=20).mean()
    df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema_12 - ema_26

    # Display Charts
    st.subheader("Price Trend with Moving Averages")
    st.line_chart(df[["close", "sma_20", "ema_20"]])

    st.subheader("Momentum Indicators (RSI & MACD)")
    st.line_chart(df[["rsi", "macd"]])
    
    # Display technical analysis table
    st.subheader("Latest Technical Indicators")
    latest_indicators = df[["close", "sma_20", "ema_20", "rsi", "macd"]].tail(5)
    st.dataframe(latest_indicators, use_container_width=True)

except Exception as e:
    st.error(f"❌ Failed to load technical analysis data for {symbol}")
    with st.expander("Error Details"):
        st.write(str(e))