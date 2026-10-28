# Architecture and data flow

## System boundary

This project has two distinct execution paths:

1. **Offline/periodic model pipeline:** fetch historical prices, prepare features, train models, and persist datasets/artifacts.
2. **Interactive dashboard:** fetch the latest available market data, load local model artifacts where required, and render analysis pages.

Opening the dashboard does not automatically run the training pipeline.

## Data and training path

~~~mermaid
flowchart TD
    SOURCE["Yahoo Finance (yfinance)"] --> FETCH["modules/ingestion"]
    FETCH --> CLEAN["modules/preprocessing"]
    CLEAN --> FEATURES["modules/feature_engineering"]
    FEATURES --> CSV["data/processed/{symbol}_feature_engineered.csv"]
    CSV --> RF["RandomForestModel"]
    CSV --> SEQ["prepare_lstm_data"]
    RF --> RF_OUT["models_saved/{symbol}_random_forest.pkl"]
    SEQ --> CNN["CNNLSTMModel / PyTorch"]
    CNN --> CNN_OUT["CNN-LSTM checkpoint and scaler"]
    RF --> METRICS["modules/evaluation"]
    METRICS --> LOGS["logs / evaluation outputs"]
~~~

The historical pipeline uses the ticker mapping in config.yaml. The configured universe is AAPL, TCS.NS, and ^NSEI.

## Dashboard path

~~~mermaid
flowchart TD
    USER["Browser"] --> STREAMLIT["app.py + pages/"]
    STREAMLIT --> MARKET["Live Market page"]
    STREAMLIT --> TECH["Technical Analysis page"]
    STREAMLIT --> PRED["Predictions page"]
    STREAMLIT --> RISK["Risk Analysis page"]
    STREAMLIT --> PERF["Model Performance page"]
    MARKET --> YF["Yahoo Finance live fetch"]
    TECH --> YF
    PRED --> YF
    PRED --> RF["models_saved/{symbol}_random_forest.pkl"]
    RISK --> YF
    PERF --> FILES["data/processed/*_train_test_split.csv"]
~~~

## Main module responsibilities

| Module | Responsibility |
| --- | --- |
| modules/ingestion | Historical and latest available market-data retrieval |
| modules/preprocessing | Data cleaning, missing-value handling, normalization |
| modules/feature_engineering | Technical indicators, returns/trends, lag and volatility features |
| modules/models | Regression and deep-learning model definitions |
| modules/training | Time-ordered train/test split and model fitting |
| modules/prediction | Model inference helpers and rule-based signal generation |
| modules/evaluation | MAE, RMSE, R², and related evaluation metrics |
| modules/risk_management | Sharpe ratio, drawdown, and volatility calculations |
| pages/ | Streamlit user-facing pages |

## Reproducibility notes

- Run Streamlit from the repository root so relative paths resolve.
- Keep the training and inference feature order consistent. A scaler/model artifact is only valid for the feature schema used when it was trained.
- Rebuild processed files and model artifacts after changing feature engineering or the target definition.
- Record the data window and evaluation period when quoting any performance metric.
- Treat upstream market data as external input; tests that call Yahoo Finance are integration tests.
