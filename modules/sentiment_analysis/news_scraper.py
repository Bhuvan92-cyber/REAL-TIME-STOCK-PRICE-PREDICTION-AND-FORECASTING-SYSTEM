import requests
from modules.utils.logger import get_logger
from modules.utils.config_loader import load_config

logger = get_logger(__name__)
CONFIG = load_config()

NEWS_API_KEY = CONFIG.get("e74ccdb303b841dabc7cfc3fb969c23c", "")
NEWS_API_URL = "https://newsapi.org/v2/everything"

def fetch_financial_news(query: str, page_size: int = 10):
    """
    Fetches latest financial news related to a stock/company.
    """
    logger.info(f"Fetching news for query: {query}")

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(NEWS_API_URL, params=params)
    response.raise_for_status()

    articles = response.json().get("articles", [])
    headlines = [article["title"] for article in articles if article.get("title")]

    logger.info(f"Fetched {len(headlines)} news headlines")
    return headlines
