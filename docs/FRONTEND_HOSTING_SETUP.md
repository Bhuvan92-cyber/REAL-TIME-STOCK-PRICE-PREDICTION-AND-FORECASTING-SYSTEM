# Frontend hosting setup

For Cloudflare Pages:

- Repository root: `frontend`
- Build command: `npm ci && npm run build`
- Output directory: `dist`
- Public variables: `VITE_API_URL`, `VITE_SUPABASE_URL`,
  `VITE_SUPABASE_ANON_KEY`

The `frontend/public/_redirects` file preserves SPA routes on refresh. Set
`VITE_API_URL` to the HTTPS backend origin, not localhost. Only `VITE_`
variables are exposed to the browser; do not add server secrets with that
prefix.
