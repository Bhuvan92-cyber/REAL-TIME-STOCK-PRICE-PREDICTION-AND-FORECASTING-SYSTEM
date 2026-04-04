#!/usr/bin/env python
"""
Comprehensive test suite for the Real-Time Stock Prediction System
Tests all major components before running the full pipeline
"""

import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.utils.logger import get_logger

logger = get_logger(__name__)

def test_imports():
    """Test that all major modules can be imported"""
    logger.info("Testing imports...")
    tests_passed = 0
    tests_failed = 0
    
    test_modules = [
        ("Data Ingestion", "modules.ingestion.yahoo_fetcher"),
        ("Preprocessing", "modules.preprocessing"),
        ("Feature Engineering", "modules.feature_engineering"),
        ("Models - Random Forest", "modules.models.regression.random_forest"),
        ("Models - CNN-LSTM", "modules.models.deep_learning.cnn_lstm_model"),
        ("Training", "modules.training.trainer"),
        ("Evaluation", "modules.evaluation.regression_metrics"),
        ("Prediction", "modules.prediction.signal_generator"),
        ("Risk Management", "modules.risk_management"),
    ]
    
    for test_name, module_name in test_modules:
        try:
            __import__(module_name)
            logger.info(f"  ✅ {test_name}")
            tests_passed += 1
        except Exception as e:
            logger.error(f"  ❌ {test_name}: {str(e)}")
            tests_failed += 1
    
    return tests_passed, tests_failed


def test_data_loading():
    """Test that data can be loaded from yfinance"""
    logger.info("\nTesting data loading...")
    tests_passed = 0
    tests_failed = 0
    
    from modules.ingestion.yahoo_fetcher import fetch_historical
    
    stocks = ["AAPL", "TCS.NS", "^NSEI"]
    
    for stock in stocks:
        try:
            df = fetch_historical(stock, period="1mo")
            if not df.empty and len(df) > 0:
                logger.info(f"  ✅ {stock}: {len(df)} rows loaded")
                tests_passed += 1
            else:
                logger.warning(f"  ⚠️  {stock}: Empty dataframe")
                tests_failed += 1
        except Exception as e:
            logger.error(f"  ❌ {stock}: {str(e)}")
            tests_failed += 1
    
    return tests_passed, tests_failed


def test_preprocessing():
    """Test preprocessing functions"""
    logger.info("\nTesting preprocessing...")
    tests_passed = 0
    tests_failed = 0
    
    import pandas as pd
    from modules.preprocessing import clean_data, handle_missing_values, normalize_data
    
    # Create sample data
    df = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=10),
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'open': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
        'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
        'volume': [1000000] * 10
    })
    
    try:
        df_clean = clean_data(df)
        logger.info(f"  ✅ Data cleaning: {df_clean.shape}")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ Data cleaning: {str(e)}")
        tests_failed += 1
    
    try:
        df_filled = handle_missing_values(df_clean)
        logger.info(f"  ✅ Missing values handling: {df_filled.shape}")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ Missing values handling: {str(e)}")
        tests_failed += 1
    
    try:
        df_normalized = normalize_data(df_filled, save_scaler=False)
        logger.info(f"  ✅ Normalization: {df_normalized.shape}")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ Normalization: {str(e)}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_feature_engineering():
    """Test feature engineering functions"""
    logger.info("\nTesting feature engineering...")
    tests_passed = 0
    tests_failed = 0
    
    import pandas as pd
    from modules.feature_engineering import (
        add_technical_indicators,
        add_trend_features,
        add_volatility_features,
        add_lag_features
    )
    
    # Create sample data
    df = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109] * 10,
    })
    
    try:
        df = add_trend_features(df)
        logger.info(f"  ✅ Trend features: {list(df.columns[-3:])}")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ Trend features: {str(e)}")
        tests_failed += 1
    
    try:
        df = add_technical_indicators(df)
        logger.info(f"  ✅ Technical indicators added")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ Technical indicators: {str(e)}")
        tests_failed += 1
    
    try:
        df = add_volatility_features(df)
        logger.info(f"  ✅ Volatility features added")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ Volatility features: {str(e)}")
        tests_failed += 1
    
    try:
        df = add_lag_features(df, lags=3)
        logger.info(f"  ✅ Lag features added")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ Lag features: {str(e)}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_models():
    """Test model instantiation"""
    logger.info("\nTesting models...")
    tests_passed = 0
    tests_failed = 0
    
    try:
        from modules.models.regression.random_forest import RandomForestModel
        model = RandomForestModel()
        logger.info(f"  ✅ Random Forest model instantiated")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ Random Forest: {str(e)}")
        tests_failed += 1
    
    try:
        from modules.models.deep_learning.cnn_lstm_model import CNNLSTMModel
        model = CNNLSTMModel()
        logger.info(f"  ✅ CNN-LSTM model instantiated")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ CNN-LSTM: {str(e)}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_config():
    """Test configuration loading"""
    logger.info("\nTesting configuration...")
    tests_passed = 0
    tests_failed = 0
    
    try:
        from modules.utils.config_loader import load_config
        config = load_config("config.yaml")
        logger.info(f"  ✅ Config loaded: {list(config.keys())[:3]}")
        tests_passed += 1
    except Exception as e:
        logger.error(f"  ❌ Config loading: {str(e)}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("STARTING COMPREHENSIVE TEST SUITE")
    logger.info("="*60)
    
    total_passed = 0
    total_failed = 0
    
    # Run all tests
    passed, failed = test_imports()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_config()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_data_loading()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_preprocessing()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_feature_engineering()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_models()
    total_passed += passed
    total_failed += failed
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    logger.info(f"✅ PASSED: {total_passed}")
    logger.info(f"❌ FAILED: {total_failed}")
    logger.info(f"📊 TOTAL:  {total_passed + total_failed}")
    logger.info("="*60)
    
    if total_failed == 0:
        logger.info("🎉 All tests passed! Ready to run the pipeline.")
        return 0
    else:
        logger.error(f"⚠️  {total_failed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
