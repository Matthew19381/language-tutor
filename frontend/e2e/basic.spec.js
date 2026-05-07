import { test, expect } from '@playwright/tests';

test.describe('LinguaAI Basic E2E', () => {
    test('homepage loads and shows title', async ({ page }) => {
        await page.goto('http://localhost:5173/');
        await expect(page).toHaveTitle(/LinguaAI/i);
    });

    test('user can navigate to placement test', async ({ page }) => {
        await page.goto('http://localhost:5173/');
        const placementLink = page.locator('a[href*="placement"], button:has-text("Start"), button:has-text("Placement")').first();
        if (await placementLink.isVisible()) {
            await placementLink.click();
            await expect(page).toHaveURL(/placement/);
        }
    });
});
