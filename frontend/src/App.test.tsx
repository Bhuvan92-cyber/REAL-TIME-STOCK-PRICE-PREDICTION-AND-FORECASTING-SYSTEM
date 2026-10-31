import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { expect, test, vi } from "vitest";
import App from "./App";

vi.mock("./auth", () => ({
  useAuth: () => ({
    user: null,
    loading: false,
    configured: false,
    signOut: vi.fn(),
    signIn: vi.fn(),
    signUp: vi.fn(),
    resetPassword: vi.fn(),
  }),
}));

function renderApp(path: string) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

test("redirects unauthenticated users to login with their destination", () => {
  renderApp("/watchlists");
  expect(screen.getByText("Authentication is not configured. Add the public Supabase environment variables.")).toBeInTheDocument();
});

test("renders pricing without requiring authentication", async () => {
  renderApp("/pricing");
  expect(await screen.findByRole("heading", { name: "Choose your analytics workspace" })).toBeInTheDocument();
});
