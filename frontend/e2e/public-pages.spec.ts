import { test, expect } from "@playwright/test";

test("public pricing page renders without authentication", async ({ page }) => {
  await page.goto("/pricing");
  await expect(page.getByRole("heading", { name: "Choose your analytics workspace" })).toBeVisible();
  await expect(page.getByText(/Billing is currently disabled/)).toBeVisible();
});

test("protected pages redirect to login when Supabase is unavailable", async ({ page }) => {
  await page.goto("/watchlists");
  await expect(page).toHaveURL(/\/login\?next=%2Fwatchlists/);
  await expect(page.getByText(/Authentication is not configured/)).toBeVisible();
});
