# Real-Time Stock Market Analysis & Prediction

A Python and Streamlit research application for exploring market data, technical indicators, next-session price estimates, and basic risk metrics for selected US and Indian market instruments.

The repository contains a multi-page dashboard, a reusable data/ML pipeline, trained Random Forest artifacts, and a PyTorch CNN-LSTM training path. It is an educational project—not a brokerage terminal or investment recommendation system.

## What is implemented

- **Market data:** Yahoo Finance through yfinance; the configured instruments are AAPL, TCS (mapped to TCS.NS), and NIFTY 50 (mapped to ^NSEI).
- **Feature engineering:** trend/return, lag, volatility, and technical-indicator features.
- **Prediction:** per-symbol Random Forest artifacts are loaded by the dashboard; the training scripts also include a CNN-LSTM path.
- **Analysis:** live-market view, technical analysis, prediction/signal view, risk metrics, and model-performance view.
- **Risk calculations:** Sharpe ratio, maximum drawdown, and volatility metrics.
- **Reproducibility:** configuration in config.yaml, dependency files, and pytest-based tests.

## Run the dashboard

### Requirements

- Python 3.10 is the repository's configured runtime (runtime.txt).
- Git and pip.
- Network access for Yahoo Finance-backed market views.

### Install

~~~bash
git clone https://github.com/Bhuvan92-cyber/REAL-TIME-STOCK-PRICE-PREDICTION-AND-FORECASTING-SYSTEM.git
cd REAL-TIME-STOCK-PRICE-PREDICTION-AND-FORECASTING-SYSTEM

python -m venv .venv
~~~

Activate the environment:

~~~powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
~~~

~~~bash
# macOS / Linux
source .venv/bin/activate
~~~

Install the dashboard/runtime dependencies:

~~~bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

Launch from the repository root:

~~~bash
streamlit run app.py
~~~

Open http://localhost:8501. The root app.py uses the root pages/ directory for Streamlit's multipage navigation. Run the command from the repository root so relative asset and data paths resolve correctly.

The dashboard's prediction page expects the checked-in per-symbol Random Forest artifacts under models_saved/. If an artifact is missing or incompatible, retrain the models using the optional workflow below.

## Train the models and rebuild data

The full training and test environment includes PyTorch and additional scientific dependencies. Use the development requirements rather than installing a second, conflicting NumPy version manually.

~~~bash
python -m pip install -r requirements-dev.txt
python scripts/run_pipeline.py
python scripts/train_model.py
~~~

The pipeline fetches historical market data for configured instruments, cleans and transforms it, engineers features, writes processed datasets, and trains Random Forest models. The training script also runs the CNN-LSTM training path and saves model/scaler artifacts. These steps require working Yahoo Finance access and can be affected by upstream rate limits or market-data availability.

Configuration:
- config.yaml — symbols, ticker mappings, model parameters, feature settings, paths, and refresh interval.
- requirements.txt — dashboard/runtime dependencies.
- requirements-dev.txt — runtime plus deep-learning, statistical-model, and development/test dependencies.

## Architecture

~~~mermaid
flowchart TD
    YF["Yahoo Finance / yfinance"] --> ING["Ingestion"]
    ING --> CLEAN["Cleaning and missing-value handling"]
    CLEAN --> FE["Feature engineering<br/>trend, technical, lag, volatility"]
    FE --> DATA["Processed datasets"]
    DATA --> RF["Random Forest training"]
    DATA --> CNN["CNN-LSTM training path"]
    RF --> ART["Per-symbol model artifacts"]
    CNN --> ART2["CNN-LSTM checkpoints and scalers"]
    YF --> LIVE["Dashboard live-data fetch"]
    ART --> PRED["Prediction and rule-based signal view"]
    LIVE --> PAGES["Streamlit pages"]
    FE --> PAGES
    ART2 --> PAGES
    PAGES --> UI["Live market · Technical analysis<br/>Predictions · Risk · Performance"]
~~~

The dashboard is a presentation layer over live market fetches and local artifacts. The historical training pipeline is separate from dashboard rendering; opening the dashboard does not retrain models.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for module responsibilities and data-flow notes.

## Dashboard pages

| Page | Purpose |
| --- | --- |
| Live Market | Latest available OHLCV data and price charts |
| Technical Analysis | Moving averages, RSI, MACD, Bollinger Bands, and related indicators |
| Predictions | Loads the selected symbol's Random Forest artifact and displays a price estimate and signal |
| Risk Analysis | Sharpe ratio, maximum drawdown, and volatility |
| Model Performance | Evaluation visualizations based on saved train/test outputs |

## Tests

Install the development dependencies first:

~~~bash
python -m pip install -r requirements-dev.txt
~~~

Run the network-independent tests:

~~~bash
pytest -q -m "not integration"
~~~

The Yahoo Finance ingestion test is marked as an integration test because it needs external network access:

~~~bash
pytest -q -m integration
~~~

A broader diagnostic script is also available:

~~~bash
python tests/test_system.py
~~~

That diagnostic script includes live Yahoo Finance requests. It is not the same as the fast, offline-focused pytest command.

A GitHub Actions workflow runs the network-independent pytest suite on pushes and pull requests.

## Repository map

~~~text
.
├── app.py                    # Streamlit entry point
├── pages/                    # Multipage dashboard
├── dashboard/assets/         # Shared styles and dashboard assets
├── modules/
│   ├── ingestion/             # Yahoo Finance / Alpha Vantage adapters
│   ├── preprocessing/         # Cleaning, imputation, scaling
│   ├── feature_engineering/   # Technical, trend, lag, volatility features
│   ├── models/                # Random Forest and deep-learning models
│   ├── training/              # Training routines
│   ├── prediction/            # Inference and signal helpers
│   ├── evaluation/            # Regression and financial metrics
│   └── risk_management/       # Risk calculations
├── scripts/                   # Pipeline, training, real-time runner
├── data/                      # Raw/processed datasets
├── models_saved/              # Model and scaler artifacts
├── tests/                     # Unit and integration tests
├── docs/                      # Architecture and screenshot guidance
├── config.yaml
├── requirements.txt
└── requirements-dev.txt
~~~

## Screenshots

This repository does not currently contain verified screenshots captured from a running application. See [docs/SCREENSHOTS.md](docs/SCREENSHOTS.md) for the exact pages and filenames to capture. Do not treat the architecture diagram above as a UI screenshot.

## Limitations and responsible use

- Yahoo Finance availability, data freshness, symbol coverage, and rate limits are controlled by the upstream provider.
- Price estimates and BUY/SELL/HOLD labels are experimental outputs, not audited investment signals.
- Historical model metrics are not evidence of future performance. Re-evaluate models on a strictly held-out, time-ordered period before using results in any decision.
- The repository does not place trades, connect to brokerage accounts, or provide financial advice.

## License

MIT. See [LICENSE](LICENSE).
