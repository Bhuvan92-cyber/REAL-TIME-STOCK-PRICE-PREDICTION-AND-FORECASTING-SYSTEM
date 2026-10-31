# API/frontend integration

The frontend uses `VITE_API_URL` and a Supabase public anon key. `apiRequest`
retrieves the persisted Supabase session and sends its access token as a Bearer
header. Server state is cached by symbol/resource keys; market data refreshes
once per minute. The service-role key is never included in browser code.
