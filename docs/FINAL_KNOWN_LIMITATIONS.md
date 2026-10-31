# Final known limitations

- Yahoo Finance is delayed/external and can fail or rate-limit; live tests are
  excluded from the deterministic suite.
- Streamlit's Pillow constraint may leave transitive Pillow advisories; the
  final Python 3.12 `pip-audit` result must be confirmed in CI before release.
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
