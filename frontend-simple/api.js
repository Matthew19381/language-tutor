// API Client for LinguaAI
// No framework, just fetch with JSON handling

const API_BASE = '/api';

// Helper: get auth header (future: JWT)
const getHeaders = () => ({
  'Content-Type': 'application/json',
});

// Helper: check response
async function checkResponse(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// User API
export async function apiCreateUser(data) {
  const res = await fetch(`${API_BASE}/placement/create-user`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return checkResponse(res);
}

export async function apiGetUser(userId) {
  const res = await fetch(`${API_BASE}/users/${userId}`);
  return checkResponse(res);
}

// Placement API
export async function apiStartPlacement(data) {
  const res = await fetch(`${API_BASE}/placement/start`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return checkResponse(res);
}

export async function apiSubmitPlacement(data) {
  const res = await fetch(`${API_BASE}/placement/submit`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return checkResponse(res);
}

// Lessons API
export async function apiGetTodayLesson(userId) {
  const res = await fetch(`${API_BASE}/lessons/today/${userId}`);
  return checkResponse(res);
}

export async function apiCompleteLesson(lessonId, userId) {
  const res = await fetch(`${API_BASE}/lessons/${lessonId}/complete`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ user_id: userId }),
  });
  return checkResponse(res);
}

export async function apiGetLessonAudio(lessonId) {
  const res = await fetch(`${API_BASE}/lessons/audio/${lessonId}`);
  return checkResponse(res);
}

export async function apiGetLessonPDF(lessonId) {
  const res = await fetch(`${API_BASE}/lessons/${lessonId}/export-pdf`);
  if (!res.ok) throw new Error('Failed to generate PDF');
  return res.blob();
}

export async function apiSaveExerciseError(lessonId, data) {
  const res = await fetch(`${API_BASE}/lessons/${lessonId}/exercise-error`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return checkResponse(res);
}

export async function apiGetLessonHistory(userId) {
  const res = await fetch(`${API_BASE}/lessons/history/${userId}`);
  return checkResponse(res);
}

export async function apiGetLesson(lessonId) {
  const res = await fetch(`${API_BASE}/lessons/${lessonId}`);
  return checkResponse(res);
}

export async function apiGenerateNextLesson(userId, language) {
  const res = await fetch(`${API_BASE}/lessons/generate-next/${userId}?language=${encodeURIComponent(language)}`, {
    method: 'POST',
    headers: getHeaders(),
  });
  return checkResponse(res);
}

export async function apiGetConceptFlashcards(lessonId) {
  const res = await fetch(`${API_BASE}/lessons/${lessonId}/concept-flashcards`);
  return checkResponse(res);
}

// Tests API
export async function apiGetDailyTest(userId) {
  const res = await fetch(`${API_BASE}/tests/daily/${userId}`);
  return checkResponse(res);
}

export async function apiSubmitTest(data) {
  const res = await fetch(`${API_BASE}/tests/submit`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return checkResponse(res);
}

export async function apiGetErrorsTest(userId) {
  const res = await fetch(`${API_BASE}/tests/errors/${userId}`);
  return checkResponse(res);
}

export async function apiGetWeeklyTest(userId, week) {
  const url = week ? `${API_BASE}/tests/weekly/${userId}?week=${week}` : `${API_BASE}/tests/weekly/${userId}`;
  const res = await fetch(url);
  return checkResponse(res);
}

export async function apiGetTestHistory(userId) {
  const res = await fetch(`${API_BASE}/tests/history/${userId}`);
  return checkResponse(res);
}

// Flashcards API
export async function apiGetFlashcards(userId, includeAll = false) {
  const url = `${API_BASE}/flashcards/${userId}?all=${includeAll ? 'true' : 'false'}`;
  const res = await fetch(url);
  return checkResponse(res);
}

export async function apiAddFlashcard(userId, data) {
  const res = await fetch(`${API_BASE}/flashcards/${userId}/add`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return checkResponse(res);
}

export async function apiAddFlashcardAI(userId, word, language) {
  const res = await fetch(`${API_BASE}/flashcards/${userId}/add-ai`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ word, language }),
  });
  return checkResponse(res);
}

export async function apiUpdateFlashcard(flashcardId, data) {
  const res = await fetch(`${API_BASE}/flashcards/${flashcardId}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return checkResponse(res);
}

export async function apiDeleteFlashcard(flashcardId) {
  const res = await fetch(`${API_BASE}/flashcards/${flashcardId}`, {
    method: 'DELETE',
  });
  return checkResponse(res);
}

export async function apiGetFlashcardAudio(flashcardId) {
  const res = await fetch(`${API_BASE}/flashcards/${flashcardId}/audio`, {
    method: 'POST',
  });
  return checkResponse(res);
}

export async function apiExportAnkiDeck(userId) {
  const res = await fetch(`${API_BASE}/flashcards/${userId}/export-anki`);
  if (!res.ok) throw new Error('Failed to export Anki deck');
  return res.blob();
}

export async function apiReviewFlashcard(flashcardId, quality) {
  const res = await fetch(`${API_BASE}/flashcards/${flashcardId}/review`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ quality }),
  });
  return checkResponse(res);
}

// Conversation API
export async function apiStartConversation(userId, topic) {
  const res = await fetch(`${API_BASE}/conversation/start/${userId}`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ topic }),
  });
  return checkResponse(res);
}

export async function apiSendMessage(sessionId, message) {
  const res = await fetch(`${API_BASE}/conversation/message`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  return checkResponse(res);
}

export async function apiEndConversation(sessionId, userId) {
  const res = await fetch(`${API_BASE}/conversation/end/${sessionId}?user_id=${userId}`, {
    method: 'POST',
  });
  return checkResponse(res);
}

export async function apiAskQuestion(userId, question) {
  const res = await fetch(`${API_BASE}/conversation/question`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ user_id: userId, question }),
  });
  return checkResponse(res);
}

export async function apiTranslate(text, fromLang, toLang) {
  const res = await fetch(`${API_BASE}/conversation/translate`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ text, from_lang: fromLang, to_lang: toLang }),
  });
  return checkResponse(res);
}

export async function apiGetGrokPrompt(userId) {
  const res = await fetch(`${API_BASE}/conversation/grok-prompt?user_id=${userId}`);
  return checkResponse(res);
}

// Stats API
export async function apiGetStats(userId) {
  const res = await fetch(`${API_BASE}/stats/${userId}`);
  return checkResponse(res);
}

export async function apiAddXP(userId, amount, reason) {
  const res = await fetch(`${API_BASE}/stats/${userId}/xp`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ amount, reason }),
  });
  return checkResponse(res);
}

export async function apiGetLeaderboard(userId) {
  const res = await fetch(`${API_BASE}/stats/${userId}/leaderboard`);
  return checkResponse(res);
}

export async function apiGetDailyTips(userId) {
  const res = await fetch(`${API_BASE}/tips/${userId}`);
  return checkResponse(res);
}

// QuickMode API
export async function apiGetQuickModePlan(userId) {
  const res = await fetch(`${API_BASE}/quickmode/${userId}`);
  return checkResponse(res);
}

export async function apiCompleteQuickModeActivity(userId, activityId) {
  const res = await fetch(`${API_BASE}/quickmode/${userId}/activity/${activityId}/complete`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({}),
  });
  return checkResponse(res);
}

// News API
export async function apiGetNews(userId, limit = 5) {
  const res = await fetch(`${API_BASE}/news/${userId}?limit=${limit}`);
  return checkResponse(res);
}

// Pronunciation API
export async function apiAnalyzePronun(audioFile, targetText, userId) {
  const formData = new FormData();
  formData.append('audio', audioFile);
  formData.append('target_text', targetText);
  formData.append('user_id', userId);

  const res = await fetch(`${API_BASE}/pronunciation/analyze`, {
    method: 'POST',
    body: formData,
  });
  return checkResponse(res);
}

export async function apiGetPronunPhrases(userId) {
  const res = await fetch(`${API_BASE}/pronunciation/phrases/${userId}`);
  return checkResponse(res);
}

// Videos API
export async function apiGetVideos(userId, topic = null) {
  const url = topic ? `${API_BASE}/videos/${userId}?topic=${topic}` : `${API_BASE}/videos/${userId}`;
  const res = await fetch(url);
  return checkResponse(res);
}

export async function apiGetVideoTopics(userId) {
  const res = await fetch(`${API_BASE}/videos/topics/${userId}`);
  return checkResponse(res);
}

// Settings API
export async function apiUpdateUserLanguage(userId, language) {
  const res = await fetch(`${API_BASE}/placement/${userId}/language`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify({ language }),
  });
  return checkResponse(res);
}

export async function apiGetUITranslations(language) {
  const res = await fetch(`${API_BASE}/settings/ui-translations?language=${encodeURIComponent(language)}`);
  return checkResponse(res);
}

export async function apiGetGDriveAuth() {
  const res = await fetch(`${API_BASE}/settings/gdrive/auth`);
  return checkResponse(res);
}

export async function apiGDriveCallback(code) {
  const res = await fetch(`${API_BASE}/settings/gdrive/callback?code=${encodeURIComponent(code)}`);
  return checkResponse(res);
}

export async function apiGDriveStatus() {
  const res = await fetch(`${API_BASE}/settings/gdrive/status`);
  return checkResponse(res);
}

// Audio TTS API
export async function apiGenerateTTS(text, language) {
  const res = await fetch(`${API_BASE}/audio/tts`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ text, language }),
  });
  return checkResponse(res);
}

// YouTube API
export async function apiSearchYouTube(userId, topic = null) {
  const url = topic ? `${API_BASE}/youtube/${userId}?topic=${topic}` : `${API_BASE}/youtube/${userId}`;
  const res = await fetch(url);
  return checkResponse(res);
}
