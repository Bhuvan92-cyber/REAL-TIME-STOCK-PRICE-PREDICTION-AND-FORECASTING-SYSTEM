from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    data_dir: Path = ROOT / "data"
    model_dir: Path = ROOT / "models_saved"
    api_title: str = "Stock Analytics API"
    api_version: str = "1.0.0"
    app_env: str = "development"
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_key: str | None = None
    supabase_jwt_secret: str | None = None
    news_rss_url: str = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL&region=US&lang=en-US"
    scheduler_secret: str | None = None
    billing_enabled: bool = False
    billing_webhook_secret: str | None = None
    admin_user_ids: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> "Settings":
        origins = tuple(
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if origin.strip()
        )
        return cls(
            cors_origins=origins or cls.cors_origins,
            app_env=os.getenv("APP_ENV", "development"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_anon_key=os.getenv("SUPABASE_ANON_KEY"),
            supabase_service_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
            supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET"),
            news_rss_url=os.getenv("NEWS_RSS_URL", cls.news_rss_url),
            scheduler_secret=os.getenv("ALERT_SCHEDULER_SECRET"),
            billing_enabled=os.getenv("BILLING_ENABLED", "false").lower() == "true",
            billing_webhook_secret=os.getenv("BILLING_WEBHOOK_SECRET"),
            admin_user_ids=tuple(item.strip() for item in os.getenv("ADMIN_USER_IDS", "").split(",") if item.strip()),
        )


settings = Settings.from_env()
