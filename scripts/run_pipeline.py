import pandas as pd
from modules.ingestion.yahoo_fetcher import fetch_historical
from modules.preprocessing import (
    clean_data,
    handle_missing_values,
    normalize_data
)
from modules.feature_engineering import (
    add_technical_indicators,
    add_trend_features,
    add_volatility_features,
    add_lag_features
)
from modules.models.regression.random_forest import RandomForestModel
from modules.training.trainer import train_regression_model
from modules.evaluation.regression_metrics import regression_evaluation
from modules.utils.helpers import save_dataframe
from modules.utils.logger import get_logger
from modules.utils.config_loader import load_config

logger = get_logger(__name__)

def main():
    logger.info("Starting full pipeline execution")

    # 1. Data Ingestion - Fetch all 3 stocks
    config = load_config()
    stocks_config = {stock['symbol']: stock.get('ticker', stock['symbol']) 
                     for stock in config['supported_stocks']}
    
    for symbol in stocks_config:
        ticker = stocks_config[symbol]
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {symbol}")
        logger.info(f"{'='*60}\n")
        
        try:
            df = fetch_historical(ticker, period="5y")
            
            if df.empty:
                logger.warning(f"No data for {symbol}, skipping")
                continue
            
            df.reset_index(inplace=True)
            df.rename(columns=str.lower, inplace=True)

            # 2. Preprocessing
            df = clean_data(df)
            df = handle_missing_values(df)

            # 3. Feature Engineering (ORDER MATTERS!)
            # Add trend features FIRST (creates returns column)
            df = add_trend_features(df)
            
            # Then add technical indicators
            df = add_technical_indicators(df)
            
            # Then add volatility features (depends on returns)
            df = add_volatility_features(df)
            
            # Add lag features
            df = add_lag_features(df, lags=5)

            # Drop NaN values created by technical indicators
            df.dropna(inplace=True)

            # Remove datetime columns (ML models require numeric input only)
            df = df.select_dtypes(exclude=["datetime64[ns]", "datetime64"])

            # Save feature-engineered data
            save_dataframe(df, f"data/processed/{symbol}_feature_engineered.csv")
            logger.info(f"\nFeature engineering completed for {symbol}")
            logger.info(f"Shape: {df.shape}, Columns: {list(df.columns)}")

            # 4. Normalization
            df_normalized = normalize_data(df, scaler_path=f"models_saved/{symbol}_scaler.pkl")

            # 5. Model Training
            model = RandomForestModel()
            preds, y_test = train_regression_model(model, df_normalized)

            # Save model
            model.save(path=f"models_saved/{symbol}_random_forest.pkl")

            # 6. Evaluation
            metrics = regression_evaluation(y_test, preds)
            logger.info(f"Evaluation Metrics for {symbol}: {metrics}")
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {str(e)}")
            continue

    logger.info("\n" + "="*60)
    logger.info("Pipeline execution completed for all stocks")
    logger.info("="*60)

if __name__ == "__main__":
    main()

