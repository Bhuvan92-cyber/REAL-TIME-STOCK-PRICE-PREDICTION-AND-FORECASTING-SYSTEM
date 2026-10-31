# Frontend architecture

The React app uses route-level pages, TanStack Query for server state, and a
small Supabase auth context for session state. `api.ts` is the typed boundary
and attaches the current access token to every request. Pages render actual API
responses and expose loading, empty, stale-provider, and error states.
