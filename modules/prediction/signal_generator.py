from modules.utils.logger import get_logger

logger = get_logger(__name__)

def generate_signal(
    current_price: float,
    predicted_price: float,
    threshold: float = 0.002
):
    """
    Generates Buy / Sell / Hold signal with confidence score.
    
    threshold: minimum percentage change to trigger action
    """

    logger.info("Generating trading signal")

    price_change_pct = (predicted_price - current_price) / current_price
    confidence = abs(price_change_pct) * 100  # %

    if price_change_pct > threshold:
        signal = "BUY"
    elif price_change_pct < -threshold:
        signal = "SELL"
    else:
        signal = "HOLD"

    logger.info(
        f"Current: {current_price}, Predicted: {predicted_price}, "
        f"Signal: {signal}"
    )

    return {
        "current_price": float(current_price),
        "predicted_price": float(predicted_price),
        "price_change_pct": float(price_change_pct),
        "confidence (%)": round(confidence, 2),
        "signal": signal
    }
