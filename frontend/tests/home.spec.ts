import { expect, test } from "@playwright/test";

test("renders the evidence workspace", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveTitle("BIS Sahayak");
  await expect(page.getByRole("heading", { name: "Make the next BIS decision clearer." })).toBeVisible();
  await expect(page.getByLabel("What do you need to understand?")).toBeVisible();
});

test("suggestions populate the question field and navigation changes context", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Which BIS standard may apply to my product?" }).click();
  await expect(page.getByLabel("What do you need to understand?")).toHaveValue(
    "Which BIS standard may apply to my product?",
  );
  await page.getByRole("button", { name: /Certification guide/ }).click();
  await expect(page.getByText("Smart Standard Finder")).toBeVisible();
});
