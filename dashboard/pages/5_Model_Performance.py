import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
import numpy as np

from modules.risk_management.sharpe_ratio import calculate_sharpe_ratio
from modules.risk_management.max_drawdown import calculate_max_drawdown


st.header("📈 Model Performance & Risk Metrics")

# Stock display names
STOCK_OPTIONS = {
    "AAPL": "Apple Inc. (NASDAQ)",
    "TCS": "Tata Consultancy Services (NSE)",
    "NIFTY50": "NIFTY 50 Index (NSE)"
}

symbol = st.session_state.get("selected_stock", "AAPL")
stock_name = STOCK_OPTIONS.get(symbol, symbol)

# Stock-specific data path
DATA_PATH = f"data/processed/{symbol}_train_test_split.csv"

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

    if not os.path.exists(DATA_PATH):
        st.error(f"❌ Performance data not found for {symbol}")
        st.info(f"Training data file: {DATA_PATH}")
        st.info("Please run the training pipeline first: `python scripts/train_model.py`")
        st.stop()

    df = pd.read_csv(DATA_PATH)

    if "y_test" not in df.columns or "y_pred" not in df.columns:
        st.error("Dataset must contain columns: y_test and y_pred")
        st.stop()

    y_true = df["y_test"].values
    y_pred = df["y_pred"].values

    # -------- Error Calculation --------

    error = y_pred - y_true
    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error**2))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    # -------- Risk Metrics --------

    returns = error / (y_true + 1e-8)  # Add small value to avoid division by zero

    sharpe = calculate_sharpe_ratio(returns)
    max_dd = calculate_max_drawdown(returns)

    # -------- Direction Accuracy --------

    actual_dir = np.sign(np.diff(y_true))
    pred_dir = np.sign(np.diff(y_pred))

    dir_accuracy = np.mean(actual_dir == pred_dir) * 100

    # -------- R² Score --------

    ss_res = np.sum((y_true - y_pred)**2)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    r2_score = 1 - (ss_res / ss_tot)

    # -------- Metrics Display --------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Directional Accuracy (%)", f"{dir_accuracy:.2f}")
    col2.metric("R² Score", f"{r2_score:.3f}")
    col3.metric("RMSE", f"{rmse:.3f}")
    col4.metric("MAPE (%)", f"{mape:.2f}")

    # Additional metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Mean Absolute Error", f"{mae:.3f}")
    col2.metric("Sharpe Ratio", f"{sharpe:.3f}")
    col3.metric("Max Drawdown", f"{max_dd:.3f}")

    # -------- Chart Data --------

    chart_df = pd.DataFrame({
        "Actual": y_true,
        "Predicted": y_pred,
        "Difference": error
    })

    # -------- Actual vs Predicted Chart --------

    st.subheader("Prediction vs Actual Prices")
    st.line_chart(chart_df[["Actual", "Predicted"]])

    # -------- Difference Chart --------

    st.subheader("Prediction Error Distribution")
    st.area_chart(chart_df["Difference"])

    # -------- Performance Summary --------
    
    st.subheader("📊 Performance Summary")
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.write("**Accuracy Metrics:**")
        st.write(f"- R² Score: {r2_score:.4f}")
        st.write(f"- MAE: {mae:.4f}")
        st.write(f"- RMSE: {rmse:.4f}")
        st.write(f"- MAPE: {mape:.2f}%")
    
    with summary_col2:
        st.write("**Risk Metrics:**")
        st.write(f"- Directional Accuracy: {dir_accuracy:.2f}%")
        st.write(f"- Sharpe Ratio: {sharpe:.4f}")
        st.write(f"- Max Drawdown: {max_dd:.4f}")
        st.write(f"- Predictions Made: {len(y_true)}")

except FileNotFoundError as e:
    st.error(f"❌ Performance data file not found: {DATA_PATH}")
    st.info("Training data needs to be generated first.")
    st.info("Run: `python scripts/train_model.py`")
    with st.expander("Error Details"):
        st.write(str(e))

except Exception as e:
    st.error("❌ Error loading model performance data")
    st.info("Make sure the model training completed successfully.")
    with st.expander("Error Details"):
        st.write(str(e))

    st.error("Unexpected error while loading model performance.")
    st.write(str(e))