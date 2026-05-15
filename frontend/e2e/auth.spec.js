import { test, expect } from '@playwright/test';

const API = 'http://localhost:8001';

test.describe('Authentication & User Creation', () => {
  test('create user via API', async ({ request }) => {
    const response = await request.post(`${API}/api/placement/create-user`, {
      data: {
        name: 'E2E Test User',
        native_language: 'Polish',
        target_language: 'German',
      },
    });
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.user_id).toBeDefined();
    expect(body.user_id).toBeGreaterThan(0);
    expect(body.name).toBe('E2E Test User');
  });

  test('create user with empty name still creates without 500', async ({ request }) => {
    const response = await request.post(`${API}/api/placement/create-user`, {
      data: { name: '', native_language: '', target_language: '' },
    });
    expect(response.status()).toBeLessThan(500);
  });

  test('get non-existent user stats returns 404', async ({ request }) => {
    const response = await request.get(`${API}/api/stats/999999`);
    expect(response.status()).toBe(404);
  });

  test('get non-existent user lessons returns 404', async ({ request }) => {
    const response = await request.get(`${API}/api/lessons/list/999999`);
    expect(response.status()).toBe(404);
  });
});
