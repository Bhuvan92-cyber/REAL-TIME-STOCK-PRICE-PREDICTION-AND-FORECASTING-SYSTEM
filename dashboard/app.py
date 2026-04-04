import streamlit as st

# -----------------------------
# Global Stock Selection
# -----------------------------
STOCK_OPTIONS = {
    "AAPL": "Apple Inc. (NASDAQ)",
    "TCS": "Tata Consultancy Services (NSE)",
    "NIFTY50": "NIFTY 50 Index (NSE)"
}

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "AAPL"

with st.sidebar:
    st.markdown("### 📌 Select Stock")
    selected = st.selectbox(
        "Stock Symbol",
        options=list(STOCK_OPTIONS.keys()),
        index=list(STOCK_OPTIONS.keys()).index(
            st.session_state.selected_stock
        )
    )
    st.session_state.selected_stock = selected

def load_css():
    with open("dashboard/assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.set_page_config(
    page_title="Real-Time Stock Market Analysis & Prediction",
    layout="wide"
)

st.title("📈 Real-Time Stock Market Analysis & Prediction System")
st.markdown(
    """
    This dashboard provides **real-time market monitoring**,  
    **machine learning–based predictions**,  
    and **risk-aware decision support (Buy / Sell / Hold)**.
    """
)

st.sidebar.success("Select a module from the sidebar ⬅")
