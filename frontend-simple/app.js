// LinguaAI Simple Frontend (Vanilla JS)
// No frameworks, no Vite, no build step

const API_BASE = '/api';
let userId = null;
let userLang = 'German';
let currentLesson = null;

// Router (hash-based)
async function router() {
  const hash = window.location.hash.slice(2) || '/';
  const content = document.getElementById('content');
  content.innerHTML = '<div class="loading"><div class="spinner"></div><p>Ładowanie...</p></div>';

  try {
    if (hash === '/') await renderHome(content);
    else if (hash.startsWith('/lesson')) await renderLesson(content);
    else if (hash === '/flashcards') await renderFlashcards(content);
    else if (hash === '/test') await renderTest(content);
    else if (hash === '/stats') await renderStats(content);
    else content.innerHTML = '<p class="text-center">Strona nie znaleziona</p>';
  } catch (err) {
    content.innerHTML = `<div class="msg msg-error">Błąd: ${err.message}</div>`;
  }
}

// API helpers
async function api(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API error');
  }
  return res.json();
}

function getUserId() {
  if (!userId) {
    const uid = localStorage.getItem('userId');
    if (uid) userId = parseInt(uid);
  }
  return userId;
}

// Home page
async function renderHome(container) {
  const savedUser = localStorage.getItem('userId');
  if (savedUser) {
    userId = parseInt(savedUser);
    window.location.hash = '/lesson';
    return;
  }

  container.innerHTML = `
    <div class="card text-center" style="max-width: 600px; margin: 2rem auto;">
      <h2>Witaj w LinguaAI</h2>
      <p class="mb-4">System nauki języków obcych z AI</p>

      <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
        <div>
          <label>Twoje języki</label>
          <select id="nativeLanguage">
            <option value="Polish">Polski</option>
            <option value="English">English</option>
            <option value="German">Deutsch</option>
            <option value="Spanish">Español</option>
            <option value="French">Français</option>
            <option value="Italian">Italiano</option>
          </select>
        </div>
        <div>
          <label>Chcę się uczyć</label>
          <select id="targetLanguage">
            <option value="German">Niemiecki</option>
            <option value="English">Angielski</option>
            <option value="Spanish">Hiszpański</option>
            <option value="French">Francuski</option>
            <option value="Italian">Włoski</option>
            <option value="Russian">Rosyjski</option>
            <option value="Chinese">Chiński</option>
          </select>
        </div>
      </div>

      <div class="mb-4">
        <label>Twoje imię</label>
        <input type="text" id="userName" placeholder="Wpisz imię">
      </div>

      <button class="btn" onclick="createUser()">Rozpocznij naukę</button>
    </div>
  `;
}

async function createUser() {
  const name = document.getElementById('userName').value.trim();
  const nativeLanguage = document.getElementById('nativeLanguage').value;
  const targetLanguage = document.getElementById('targetLanguage').value;

  if (!name) return alert('Podaj imię');

  try {
    const data = await api('/placement/create-user', {
      method: 'POST',
      body: JSON.stringify({ name, native_language: nativeLanguage, target_language: targetLanguage }),
    });
    userId = data.user_id;
    localStorage.setItem('userId', userId);
    window.location.hash = '/lesson';
  } catch (err) {
    alert('Błąd: ' + err.message);
  }
}

// Lesson page
async function renderLesson(container) {
  if (!getUserId()) { window.location.hash = '/'; return; }

  container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Generowanie lekcji...</p></div>';

  try {
    const data = await api(`/lessons/today/${userId}`);
    currentLesson = data;

    const content = data.content || {};
    const lessonHtml = `
      <div class="card">
        <div class="flex justify-between items-center mb-4">
          <h2>${data.title || 'Lekcja dzisiaj'}</h2>
          <span class="badge">Dzień ${data.day_number}</span>
        </div>

        <div class="grid grid-2 mb-4">
          <div><strong>Temat:</strong> ${data.topic || 'Ogólny'}</div>
          <div><strong>Poziom:</strong> ${data.cefr_level || 'A1'}</div>
        </div>

        ${content.explanation ? `
          <div class="card">
            <h3>📘 Gramatyka</h3>
            <div class="prose">${markdownToHtml(content.explanation)}</div>
          </div>
        ` : ''}

        ${content.vocabulary ? `
          <div class="card">
            <h3>📗 Słownictwo</h3>
            ${content.vocabulary.map((item, i) => `
              <div style="margin-bottom: 0.75rem; padding-bottom: 0.75rem; border-bottom: 1px solid #333;">
                <div class="flex items-center justify-between">
                  <strong>${item.word}</strong>
                  <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" onclick="playAudio('${item.word}')">🔊</button>
                </div>
                <p>${item.meaning}</p>
                ${item.example ? `<p><em>"${item.example}"</em></p>` : ''}
              </div>
            `).join('')}
          </div>
        ` : ''}

        ${content.dialogue ? `
          <div class="card">
            <h3>💬 Dialog</h3>
            <div class="prose">${markdownToHtml(content.dialogue)}</div>
          </div>
        ` : ''}

        <div class="flex gap-1">
          <button class="btn" onclick="completeLesson(${data.lesson_id})">✓ Zakończ lekcję (+25 XP)</button>
        </div>
      </div>
    `;

    container.innerHTML = lessonHtml;
  } catch (err) {
    container.innerHTML = `<div class="msg msg-error">${err.message}</div>`;
  }
}

async function completeLesson(lessonId) {
  try {
    await api(`/lessons/${lessonId}/complete`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
    alert('Lekcja ukończona! +25 XP');
    window.location.reload();
  } catch (err) {
    alert('Błąd: ' + err.message);
  }
}

async function playAudio(text) {
  try {
    const res = await fetch('/api/audio/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language: userLang }),
    });
    const data = await res.json();
    const audio = new Audio(data.url);
    audio.play();
  } catch (err) {
    console.error('Audio error:', err);
  }
}

// Flashcards page (placeholder)
async function renderFlashcards(container) {
  container.innerHTML = `
    <div class="card">
      <h2>Fiszki</h2>
      <p>Funkcja w budowie. Wróć później.</p>
    </div>
  `;
}

// Test page (placeholder)
async function renderTest(container) {
  container.innerHTML = `
    <div class="card">
      <h2>Test</h2>
      <p>Testy dostępne po ukończeniu testu poziomującego.</p>
    </div>
  `;
}

// Stats page
async function renderStats(container) {
  if (!getUserId()) { window.location.hash = '/'; return; }

  container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Ładowanie statystyk...</p></div>';

  try {
    const data = await api(`/stats/${userId}`);
    const stats = data;

    container.innerHTML = `
      <div class="card">
        <h2>Statystyki</h2>

        <div class="grid grid-2 mb-4">
          <div class="card text-center">
            <p class="text-3xl font-bold">${stats.level_info?.level || 1}</p>
            <p>Poziom</p>
            <p class="text-sm text-gray-400">${stats.level_info?.xp_to_next || 0} XP do następnego</p>
          </div>
          <div class="card text-center">
            <p class="text-3xl font-bold">${stats.lessons?.completed || 0}</p>
            <p>Ukończone lekcje</p>
          </div>
        </div>

        <h3>Osiągnięcia</h3>
        <ul>
          ${(stats.achievements || []).map(a => `
            <li>${a.icon} <strong>${a.title}</strong> — ${a.description}</li>
          `).join('')}
        </ul>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="msg msg-error">${err.message}</div>`;
  }
}

// Simple markdown parser (basic)
function markdownToHtml(text) {
  if (!text) return '';
  return text
    .replace(/\n\n/g, '</p><p>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^\* (.*$)/gm, '<li>$1</li>')
    .replace(/\n/g, '<br>');
}

// Router listener
window.addEventListener('hashchange', router);
window.addEventListener('load', router);
