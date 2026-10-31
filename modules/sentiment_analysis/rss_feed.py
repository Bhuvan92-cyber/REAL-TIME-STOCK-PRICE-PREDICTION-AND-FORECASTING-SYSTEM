from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import requests


def fetch_rss_news(url: str, symbol: str, limit: int = 20) -> list[dict]:
    response = requests.get(url, timeout=10, headers={"User-Agent": "stock-analytics/1.0"})
    response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    results = []
    seen = set()
    for item in root.findall(".//item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or link in seen:
            continue
        seen.add(link)
        published = item.findtext("pubDate")
        try:
            timestamp = parsedate_to_datetime(published).astimezone(timezone.utc).isoformat() if published else None
        except (TypeError, ValueError, IndexError):
            timestamp = None
        results.append({"symbol": symbol.upper(), "title": title, "url": link, "published_at": timestamp, "source": url})
    return results


def classify_headline(title: str) -> dict[str, float | str]:
    positive = {"gain", "growth", "profit", "beat", "upgrade", "surge", "record"}
    negative = {"loss", "decline", "fall", "downgrade", "fraud", "cut", "warning"}
    words = {word.strip(".,:;!?").lower() for word in title.split()}
    score = (len(words & positive) - len(words & negative)) / max(len(words & (positive | negative)), 1)
    label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return {"label": label, "score": float(score)}
