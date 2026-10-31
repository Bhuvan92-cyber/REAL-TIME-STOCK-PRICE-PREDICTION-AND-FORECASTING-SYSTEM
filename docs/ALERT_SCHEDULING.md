# Alert scheduling

Manual evaluation is available to an authenticated user at
`POST /api/v1/alerts/evaluate`. Scheduled evaluation is protected by the
backend-only `ALERT_SCHEDULER_SECRET` and uses
`POST /api/v1/internal/alerts/evaluate`.

The included GitHub Actions workflow runs every 15 minutes or on demand.
Configure repository secrets `STOCK_API_URL` and `ALERT_SCHEDULER_SECRET`.
GitHub schedule timing is best effort, and provider rate limits still apply.
No continuously running worker or paid scheduler is required.
