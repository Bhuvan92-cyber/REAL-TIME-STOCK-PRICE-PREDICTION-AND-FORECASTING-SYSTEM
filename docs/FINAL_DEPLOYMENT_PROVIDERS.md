# Final deployment providers

No cloud deployment or paid service was enabled. The recommended architecture
is Cloudflare Pages for the static frontend, Render Free for a demo/testing
FastAPI service, and Supabase Free for authentication and PostgreSQL.

| Provider | Signup | Pricing | Card requirement | Relevant limits |
|---|---|---|---|---|
| Cloudflare Pages | [Dashboard](https://dash.cloudflare.com/sign-up) | [Pages limits](https://developers.cloudflare.com/pages/platform/limits/) | Unverified; confirm during signup | Static assets are free; Functions/Workers quotas and build limits apply |
| Render | [Signup](https://dashboard.render.com/register) | [Free services](https://render.com/docs/free) / [Pricing](https://render.com/pricing) | Unverified; free instances may still be subject to account checks | Free services sleep; limited CPU/RAM; not recommended by Render for production |
| Supabase | [Signup](https://supabase.com/dashboard) | [Official pricing](https://supabase.com/pricing) | Unverified; confirm during signup | Free database/storage/egress quotas and possible project pausing |

The application makes no card-free claim. Docker Compose remains the
independent local deployment option. Billing is disabled by default and no
payment gateway is configured.
