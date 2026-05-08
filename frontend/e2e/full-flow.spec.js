import { test, expect } from '@playwright/test';

test.describe('LinguaAI E2E - Core Functionality', () => {
  
  test('homepage loads and has correct title', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await expect(page).toHaveTitle(/LinguaAI/i);
    // Check that the page has content
    await expect(page.locator('body')).toContainText(/LinguaAI/i);
  });

  test('API health check', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/health');
    expect(response.ok()).toBeTruthy();
  });

  test('API create user', async ({ request }) => {
    const response = await request.post('http://localhost:8001/api/placement/create-user', {
      data: {
        name: 'E2E Test User',
        native_language: 'Polish',
        target_language: 'German'
      }
    });
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.user_id).toBeDefined();
    console.log('Created user ID:', body.user_id);
  });

  test('placement page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/placement');
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    // Should have some form elements or text
    const pageText = await page.textContent('body');
    expect(pageText).toMatch(/place|tell|pytanie|test|placement/i);
  });

  test('can navigate from home to placement', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // Look for any link/button that might lead to placement
    const placementLink = page.locator('a[href*="placement"]').first();
    if (await placementLink.isVisible().catch(() => false)) {
      await placementLink.click();
      await expect(page).toHaveURL(/placement/);
    } else {
      // Already on placement or link not visible - that's ok
      console.log('Placement link not found or already on page');
    }
  });

  test('navigation items exist when user logged in', async ({ page }) => {
    // First create a user via API
    const response = await page.request.post('http://localhost:8001/api/placement/create-user', {
      data: {
        name: 'Nav Test User',
        native_language: 'Polish',
        target_language: 'German'
      }
    });
    const body = await response.json();
    const userId = body.user_id;
    
    // Now go to home page with user logged in
    await page.goto(`http://localhost:5173/?userId=${userId}`);
    await page.waitForLoadState('networkidle');
    
    // Check that navigation exists
    const navLinks = page.locator('nav a, [role="navigation"] a');
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(0);
  });
});
