import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
import joblib

from modules.prediction.signal_generator import generate_signal
from modules.ingestion.live_data_fetcher import fetch_live_stock_data

st.header("🤖 Price Prediction & Decision Support")

# Stock configuration
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

# Selected Stock
symbol = st.session_state.get("selected_stock", "AAPL")
stock_name = STOCK_OPTIONS.get(symbol, symbol)
ticker = TICKER_MAP.get(symbol, symbol)

# Model path
MODEL_PATH = f"models_saved/{symbol}_random_forest.pkl"

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
    # Load model
    if not os.path.exists(MODEL_PATH):
        st.error(f"❌ Model not found at {MODEL_PATH}")
        st.info("Please train the model first using: `python scripts/train_model.py`")
        st.stop()
    
    model = joblib.load(MODEL_PATH)

    # Load feature-engineered data (priority) or fall back to live data
    csv_path = f"data/processed/{symbol}_feature_engineered.csv"
    
    if os.path.exists(csv_path):
        # Load pre-processed feature-engineered data with all features
        df = pd.read_csv(csv_path)
        st.info("📊 Using pre-processed feature-engineered data")
    else:
        # Fallback: Load live data and apply minimal feature engineering
        try:
            st.info("📡 Fetching live data and applying features...")
            df = fetch_live_stock_data(ticker, interval="1d", period="1y")
            
            # Apply basic feature engineering to match training features
            from modules.feature_engineering import (
                add_trend_features,
                add_technical_indicators,
                add_volatility_features,
                add_lag_features
            )
            
            df.columns = [c.lower() for c in df.columns]
            df = add_trend_features(df)
            df = add_technical_indicators(df)
            df = add_volatility_features(df)
            df = add_lag_features(df, lags=5)
            df.dropna(inplace=True)
            
        except Exception as e:
            st.error(f"❌ Cannot load or process data: {str(e)}")
            st.error("Please run the pipeline first: `python scripts/run_pipeline.py`")
            st.stop()

    # Normalize column names
    df.columns = [c.lower() for c in df.columns]

    if "close" not in df.columns:
        st.error("Dataset must contain 'close' column")
        st.stop()

    # Feature preparation - get numeric features only
    X_latest = df.drop(columns=["close"], errors="ignore").iloc[-1:]
    X_latest = X_latest.select_dtypes(include=["int64", "float64"])
    
    # Get current price
    current_price = df["close"].iloc[-1]
    
    # Check if we have enough features
    expected_features = model.n_features_in_
    actual_features = X_latest.shape[1]
    
    if actual_features != expected_features:
        st.error(f"❌ Feature mismatch!")
        st.error(f"Model expects {expected_features} features, but data has {actual_features}")
        st.info("This usually means the data needs to be processed with: `python scripts/run_pipeline.py`")
        st.stop()
    
    # Make prediction
    predicted_price = model.predict(X_latest.values.reshape(1, -1))[0]

    signal = generate_signal(current_price, predicted_price)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current Price",
        f"${current_price:.2f}" if symbol == "AAPL" else f"₹{current_price:.2f}"
    )
    col2.metric(
        "Predicted Price",
        f"${predicted_price:.2f}" if symbol == "AAPL" else f"₹{predicted_price:.2f}"
    )
    
    # Signal with color coding
    signal_color = "🟢" if signal["signal"] == "BUY" else ("🔴" if signal["signal"] == "SELL" else "🟡")
    col3.metric(signal_color + " Signal", signal["signal"])
    col4.metric("Confidence (%)", f"{signal['confidence (%)']:.2f}%")

    st.success("✅ Prediction generated successfully")
    
    # Show prediction details
    st.subheader("Prediction Details")
    col1, col2 = st.columns(2)
    col1.info(f"**Price Change:** {signal['price_change_pct']*100:.2f}%")
    col2.info(f"**Recommendation:** {signal['signal']}")

except FileNotFoundError as e:
    st.error("❌ Model file not found")
    st.info("Train the model first using: `python scripts/train_model.py`")
    with st.expander("Error Details"):
        st.write(str(e))
except Exception as e:
    st.error("❌ Prediction not available")
    st.info("Make sure the model is trained and feature engineering is complete.")
    with st.expander("Error Details"):
        st.write(str(e))