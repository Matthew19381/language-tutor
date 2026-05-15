import { test, expect } from '@playwright/test';

const API = 'http://localhost:8001';

test.describe('Security — Ownership & Authorization', () => {
  let userA, userB;

  test.beforeAll(async ({ request }) => {
    const resA = await request.post(`${API}/api/placement/create-user`, {
      data: { name: 'Security User A', native_language: 'Polish', target_language: 'German' },
    });
    userA = await resA.json();

    const resB = await request.post(`${API}/api/placement/create-user`, {
      data: { name: 'Security User B', native_language: 'Polish', target_language: 'German' },
    });
    userB = await resB.json();
  });

  test('user B cannot complete user A lesson', async ({ request }) => {
    const lessonRes = await request.post(`${API}/api/lessons/generate?user_id=${userA.user_id}`);
    if (!lessonRes.ok()) return;

    const lesson = await lessonRes.json();
    const lessonId = lesson.id || lesson.lesson_id;
    if (!lessonId) return;

    const completeRes = await request.post(`${API}/api/lessons/${lessonId}/complete`, {
      data: { user_id: userB.user_id },
    });
    expect(completeRes.status()).toBe(403);
  });

  test('user B cannot generate concept flashcards for user A lesson', async ({ request }) => {
    const lessonRes = await request.post(`${API}/api/lessons/generate?user_id=${userA.user_id}`);
    if (!lessonRes.ok()) return;

    const lesson = await lessonRes.json();
    const lessonId = lesson.id || lesson.lesson_id;
    if (!lessonId) return;

    const fcRes = await request.post(
      `${API}/api/lessons/${lessonId}/concept-flashcards?user_id=${userB.user_id}`
    );
    expect(fcRes.status()).toBe(403);
  });

  test('evaluate-production requires ownership', async ({ request }) => {
    const lessonRes = await request.post(`${API}/api/lessons/generate?user_id=${userA.user_id}`);
    if (!lessonRes.ok()) return;

    const lesson = await lessonRes.json();
    const lessonId = lesson.id || lesson.lesson_id;
    if (!lessonId) return;

    const evalRes = await request.post(
      `${API}/api/lessons/${lessonId}/evaluate-production`,
      {
        data: {
          user_id: userB.user_id,
          user_answer: 'Test answer',
          instruction: 'Test instruction',
          language: 'German',
        },
      }
    );
    expect(evalRes.status()).toBe(403);
  });

  test('missing user_id in path returns 404', async ({ request }) => {
    const response = await request.get(`${API}/api/stats/0`);
    expect(response.status()).toBe(404);
  });

  test('lesson list requires valid user', async ({ request }) => {
    const response = await request.get(`${API}/api/lessons/list/999999`);
    expect(response.status()).toBe(404);
  });
});
