# Final known limitations

- Yahoo Finance is delayed/external and can fail or rate-limit; live tests are
  excluded from the deterministic suite.
- The optional legacy Streamlit dependency set may retain transitive Pillow
  advisories until Streamlit supports Pillow 13; it is excluded from the
  production API dependency audit.
- Free hosting card requirements are unverified and provider sleep/quotas
  apply.
- No payment provider, brokerage, real-money trading, or paid market-data
  integration is enabled.
- Playwright tests currently cover public routing only; authenticated journeys
  require isolated Supabase test credentials and deterministic API fixtures.
- Docker and Python 3.12 runtime execution require CI or unavailable local
  services.
- Public cloud deployment and URL smoke tests require authorized provider
  accounts; no deployment was performed.
