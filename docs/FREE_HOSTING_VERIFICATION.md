# Free hosting verification

Verification date: **2026-10-31**.

Official documentation confirms the following capabilities:

- [Cloudflare Pages Functions pricing](https://developers.cloudflare.com/pages/functions/pricing/)
  documents a Free plan and a 100,000 daily Workers/Functions request quota;
  static asset requests are free and unlimited.
- [Render free services](https://render.com/docs/free) documents free Python
  web services, Docker workloads, health checks, and sleep/cold-start
  limitations. Render explicitly warns that free instances are not for
  production applications.
- [Render pricing](https://render.com/pricing) documents the available service
  categories and free/static deployment options.
- [Supabase pricing](https://supabase.com/pricing) documents the Free plan
  and project pause/resource limitations.

The official pages reviewed do **not** provide a universal, explicit
no-credit-card guarantee for every account, region, or abuse-prevention
check. Therefore this repository does not claim that signup is card-free.
Confirm the current signup screen before deployment. No paid service or card
is required for local development.

Recommended no-cost architecture:

1. Cloudflare Pages for the static frontend.
2. Render Free web service for a testing/demo FastAPI backend, accepting sleep
   and cold-start behavior.
3. Supabase Free for authentication and PostgreSQL.

Do not use the free Render database for durable user data; this application
uses Supabase for persistence.
