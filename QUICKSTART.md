# ⚡ Quick Start Guide

## System Overview

This is a **Real-Time Stock Prediction System** that predicts stock prices for **3 stocks**:
- **AAPL** (Apple) - NASDAQ
- **TCS** (Tata Consultancy Services) - NSE  
- **NIFTY50** (NIFTY 50 Index) - NSE

The system uses:
- **Random Forest** for regression-based predictions
- **CNN-LSTM** for deep learning sequence predictions
- **Ensemble voting** to combine both models
- **Technical indicators** (RSI, MACD, Bollinger Bands, etc.)
- **Risk metrics** (Sharpe Ratio, Max Drawdown, Volatility)

---

## 🚀 Installation

### Step 1: Prerequisites
- **Python 3.9+** (Check: `python --version`)
- **pip** package manager
- Internet connection (for downloading data)

### Step 2: Install Project

```bash
# Clone or navigate to project directory
cd Real-Time-Stock-Market-Analysis-And-Prediction-System

# Install project in editable mode with all dependencies
pip install -e .

# Verify installation
python -c "import modules; print('✅ Installation successful')"
```

### Step 3: Verify Installation

Run the comprehensive test suite:

```bash
python tests/test_system.py
```

Expected output:
```
✅ PASSED: 15+
❌ FAILED: 0
🎉 All tests passed! Ready to run the pipeline.
```

---

## 📊 Complete Workflow

### **Phase 1: Data Preparation & Model Training (One-time)**

```bash
# Step 1: Run the full pipeline (Data ingestion → Feature engineering)
# This will process AAPL, TCS, and NIFTY50 data
python scripts/run_pipeline.py

# This generates:
# - data/processed/AAPL_feature_engineered.csv
# - data/processed/TCS_feature_engineered.csv
# - data/processed/NIFTY50_feature_engineered.csv
```

**Expected output:**
```
2025-03-06 | INFO | Starting full pipeline execution
============================================================
Processing AAPL
============================================================
✅ Fetched Yahoo Finance data for AAPL for period 5y
✅ Data cleaning completed
...
✅ Feature engineering completed for AAPL
Shape: (1250, 35), Columns: ['close', 'sma_20', 'ema_20', 'rsi', 'macd', ...]
```

```bash
# Step 2: Train both Random Forest and CNN-LSTM models
# This will create models for all 3 stocks
python scripts/train_model.py

# This generates:
# - models_saved/AAPL_random_forest.pkl
# - models_saved/AAPL_cnn_lstm_model.pt
# - models_saved/AAPL_lstm_scaler.pkl
# - Similarly for TCS and NIFTY50
```

**Expected output:**
```
============================================================
Training models for AAPL
============================================================
✅ Loaded data shape: (1250, 35)
Training Random Forest Regressor
✅ Random Forest Metrics: {'mae': 2.34, 'rmse': 3.45, 'r2': 0.92}
Starting CNN-LSTM training
CNN-LSTM Epoch [1/10] - Loss: 0.052341
...
CNN-LSTM Epoch [10/10] - Loss: 0.001234
```

### **Phase 2: Launch Interactive Dashboard**

```bash
# Start the Streamlit dashboard
# The dashboard will open at http://localhost:8501
streamlit run dashboard/app.py
```

**Dashboard Features:**
- 📊 **Live Market** - Real-time price data and charts
- 📐 **Technical Analysis** - 20+ technical indicators
- 🤖 **Predictions** - ML-based price forecasts with trading signals (BUY/SELL/HOLD)
- ⚠️ **Risk Analysis** - Sharpe ratio, volatility, max drawdown
- 📈 **Model Performance** - Evaluation metrics and backtesting results

**Stock Selection:**
- Use the sidebar dropdown to select: **AAPL**, **TCS**, or **NIFTY50**
- All 5 dashboard pages will update for the selected stock

### **Phase 3: (Optional) Real-Time Prediction Engine**

```bash
# Start continuous real-time predictions for a specific stock
# Usage: python scripts/realtime_runner.py [STOCK_SYMBOL]

python scripts/realtime_runner.py AAPL
# or
python scripts/realtime_runner.py TCS
# or
python scripts/realtime_runner.py NIFTY50
```

**What it does:**
- Loads trained models continuously
- Makes predictions every 30 seconds
- Generates BUY/SELL/HOLD signals
- Saves predictions to `data/raw/realtime/{STOCK}_live_stream.csv`
- Logs all results to `logs/system.log`

**Stop:** Press `Ctrl+C`

---

## 📁 Important Directories & Files

```
project/
├── scripts/
│   ├── run_pipeline.py          # Data → Features (all 3 stocks)
│   ├── train_model.py           # Train all models (all 3 stocks)
│   ├── realtime_runner.py       # Real-time predictions
│   └── __init__.py
│
├── dashboard/
│   ├── app.py                   # Main dashboard entry
│   ├── pages/
│   │   ├── 1_Live_Market.py     # Real-time market data
│   │   ├── 2_Technical_Analysis.py  # Indicators (RSI, MACD, etc)
│   │   ├── 3_Predictions.py     # ML predictions & signals
│   │   ├── 4_Risk_Analysis.py   # Risk metrics
│   │   └── 5_Model_Performance.py   # Backtest results
│   └── assets/styles.css
│
├── modules/
│   ├── ingestion/               # Data loading (Yahoo, Live)
│   ├── preprocessing/           # Cleaning, normalization
│   ├── feature_engineering/     # Technical features, lag features
│   ├── models/                  # ML models (RF, CNN-LSTM)
│   ├── training/                # Model training pipelines
│   ├── evaluation/              # Metrics (MSE, MAE, etc)
│   ├── prediction/              # Signal generation
│   ├── risk_management/         # Risk calculations
│   └── utils/                   # Logging, config, helpers
│
├── data/
│   ├── raw/
│   │   ├── historical/          # Downloaded historical data
│   │   └── realtime/            # Live stream data
│   └── processed/               # Feature-engineered data
│
├── models_saved/
│   ├── AAPL_random_forest.pkl
│   ├── AAPL_cnn_lstm_model.pt
│   ├── TCS_random_forest.pkl
│   ├── TCS_cnn_lstm_model.pt
│   └── (similar for NIFTY50)
│
├── config.yaml                  # Configuration (API keys, settings)
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
└── tests/
    └── test_system.py           # Comprehensive test suite
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
supported_stocks:
  - symbol: "AAPL"
    name: "Apple Inc."
    ...
  - symbol: "TCS"
    ...
  - symbol: "NIFTY50"
    ...

models:
  random_forest:
    n_estimators: 200       # Number of trees
    max_depth: null         # Unlimited depth
  cnn_lstm:
    hidden_size: 64
    epochs: 10
    learning_rate: 0.001

realtime:
  update_interval_seconds: 30  # Prediction frequency
```

---

## 🔍 Monitoring & Logs

**All logs are saved to:** `logs/system.log`

View logs in real-time:
```bash
# On Windows (PowerShell)
Get-Content logs\system.log -Tail 20 -Wait

# On Mac/Linux
tail -f logs/system.log
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" error
```bash
# Solution: Reinstall the package
pip install --force-reinstall -e .
```

### Issue: "No such file or directory" for data
```bash
# Solution: Run the pipeline first
python scripts/run_pipeline.py
```

### Issue: "Model not found" when making predictions
```bash
# Solution: Train the models
python scripts/train_model.py
```

### Issue: Streamlit app won't load
```bash
# Solution: Install streamlit-autorefresh
pip install streamlit-autorefresh==0.0.2
pip install streamlit==1.52.1
```

### Issue: Yahoo Finance returns no data
```python
# Check internet connection
# Some stocks might need ticker adjustment:
# - US stocks: symbol (e.g., "AAPL")
# - Indian stocks: add ".NS" or ".BO" (e.g., "TCS.NS")
# - Indices: use symbol with "^" (e.g., "^NSEI")
```

---

## 📊 Expected Results

### Data Pipeline
- Downloads 5 years of historical data
- Generates 35+ features per stock
- Handles missing values automatically
- Normalizes data for ML models

### Model Training
- Random Forest: R² score ~0.85-0.92
- CNN-LSTM: RMSE < 5% of price range
- Training time: 2-5 minutes per stock

### Predictions
- Daily price forecasts
- Trading signals (BUY/SELL/HOLD)
- Confidence scores
- Risk metrics (Sharpe, Volatility, Drawdown)

### Dashboard
- 5 responsive pages
- Real-time data refresh
- Interactive charts
- Multi-stock support

---

## 🤝 Support

For issues or questions:
1. Check the `logs/system.log` file
2. Run `python tests/test_system.py` to diagnose problems
3. Review error messages in the terminal
4. Check `README.md` for detailed documentation

---

## 📝 Next Steps

1. ✅ Install dependencies
2. ✅ Run tests to verify setup
3. ✅ Execute `run_pipeline.py` (data prep)
4. ✅ Execute `train_model.py` (train models)
5. ✅ Launch dashboard with `streamlit run dashboard/app.py`
6. ✅ (Optional) Start real-time engine with `realtime_runner.py`

**Happy analyzing! 📈**
