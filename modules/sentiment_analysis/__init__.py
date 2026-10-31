from .news_scraper import fetch_financial_news

__all__ = ["fetch_financial_news", "analyze_sentiment", "FinBERTSentiment"]


def analyze_sentiment(*args, **kwargs):
    from .sentiment_analyzer import analyze_sentiment as implementation

    return implementation(*args, **kwargs)


def FinBERTSentiment(*args, **kwargs):
    from .finbert_model import FinBERTSentiment as implementation

    return implementation(*args, **kwargs)
