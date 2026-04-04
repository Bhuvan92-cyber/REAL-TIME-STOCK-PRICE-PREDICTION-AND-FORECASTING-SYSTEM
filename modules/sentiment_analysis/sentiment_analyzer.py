from textblob import TextBlob
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def analyze_sentiment(texts):
    """
    Analyzes sentiment polarity using TextBlob.
    Returns average sentiment score.
    """

    logger.info("Analyzing sentiment using TextBlob")

    if not texts:
        return 0.0

    polarity_scores = [TextBlob(text).sentiment.polarity for text in texts]
    avg_sentiment = sum(polarity_scores) / len(polarity_scores)

    logger.info(f"Average sentiment score: {avg_sentiment}")
    return avg_sentiment
