import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120 seconds for AI generation calls
})

// Request interceptor
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

// ===== User / Placement =====

export const createUser = (data) =>
  api.post('/placement/create-user', data)

export const getUser = (userId) =>
  api.get(`/placement/user/${userId}`)

export const startPlacementTest = (data = {}) =>
  api.post('/placement/start', data)

export const submitPlacementTest = (data) =>
  api.post('/placement/submit', data)

export const updateUserLanguage = (userId, targetLanguage) =>
  api.patch(`/placement/${userId}/language`, { target_language: targetLanguage })

export const getLanguageProfiles = (userId) =>
  api.get(`/placement/${userId}/languages`)

// ===== Lessons =====

export const getTodayLesson = (userId) =>
  api.get(`/lessons/today/${userId}`)

export const getLesson = (lessonId) =>
  api.get(`/lessons/${lessonId}`)

export const completeLesson = (lessonId, userId) =>
  api.post(`/lessons/${lessonId}/complete`, { user_id: userId })

export const evaluateProduction = (lessonId, data) =>
  api.post(`/lessons/${lessonId}/evaluate-production`, data)

export const generateTTS = (text, language) =>
  api.post(`/audio/tts`, { text, language })

export const getLessonAudio = (lessonId) =>
  api.get(`/lessons/audio/${lessonId}`)

export const listLessons = (userId) =>
  api.get(`/lessons/list/${userId}`)

export const getLessonHistory = (userId) =>
  api.get(`/lessons/history/${userId}`)

export const generateNextLesson = (userId) =>
  api.post(`/lessons/next/${userId}`)

export const generateConceptFlashcards = (lessonId) =>
  api.post(`/lessons/${lessonId}/concept-flashcards`)

export const recordExerciseError = (lessonId, data) =>
  api.post(`/lessons/${lessonId}/exercise-error`, data)

// ===== Tests =====

export const getDailyTest = (userId) =>
  api.get(`/tests/daily/${userId}`)

export const submitTest = (data) =>
  api.post('/tests/submit', data)

export const getWeeklyTest = (userId, week) =>
  api.get(`/tests/weekly/${userId}`, { params: { week } })

export const getTestHistory = (userId) =>
  api.get(`/tests/history/${userId}`)

export const getTestResult = (resultId) =>
  api.get(`/tests/result/${resultId}`)

// ===== Flashcards =====

export const getFlashcards = (userId) =>
  api.get(`/flashcards/${userId}`)

export const getDueFlashcards = (userId) =>
  api.get(`/flashcards/${userId}/due`)

export const reviewFlashcard = (flashcardId, rating) =>
  api.post(`/flashcards/${flashcardId}/review`, { rating })

export const exportAnki = (userId) =>
  axios.post(`/api/flashcards/${userId}/export-anki`, {}, { responseType: 'blob' })

export const addFlashcard = (userId, data) =>
  api.post(`/flashcards/${userId}/add`, data)

export const addFlashcardAI = (userId, word) =>
  api.post(`/flashcards/${userId}/add-ai`, { word })

// ===== Conversation =====

export const startConversation = (userId, topic) =>
  api.post(`/conversation/start/${userId}`, { topic })

export const sendMessage = (sessionId, userMessage) =>
  api.post('/conversation/message', { session_id: sessionId, user_message: userMessage })

export const analyzeConversation = (sessionId, userId) =>
  api.post('/conversation/analyze', { session_id: sessionId, user_id: userId })

export const analyzePastedConversation = (userId, pastedText) =>
  api.post('/conversation/analyze-text', { user_id: userId, pasted_text: pastedText })

export const getGrokPrompt = (userId) =>
  api.get(`/conversation/grok-prompt`, { params: { user_id: userId } })

export const askQuestion = (question, userId) =>
  api.post('/conversation/question', { question, user_id: userId })

// ===== Stats =====

export const getStats = (userId) =>
  api.get(`/stats/${userId}`)

export const addXP = (userId, amount, reason) =>
  api.post(`/stats/${userId}/xp`, { amount, reason })

export const getDailyTips = (userId) =>
  api.get(`/tips/${userId}`)

// ===== PDF Export =====

export const exportLessonPDF = (lessonId) =>
  axios.get(`/api/lessons/${lessonId}/export-pdf`, { responseType: 'blob' })

// ===== Quick Mode =====

export const getQuickMode = (userId) =>
  api.get(`/quickmode/${userId}`)

// ===== News =====

export const getNews = (userId, limit = 5) =>
  api.get(`/news/${userId}`, { params: { limit } })

// ===== Pronunciation =====

export const getPronunciationPhrases = (userId) =>
  api.get(`/pronunciation/phrases/${userId}`)

export const analyzePronunciation = (formData) =>
  axios.post('/api/pronunciation/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000,
  })

// ===== YouTube =====

export const searchYouTube = (userId, query = '') =>
  api.get(`/youtube/search`, { params: { user_id: userId, query } })

// ===== Achievements =====

export const getAchievements = (userId) =>
  api.get(`/stats/${userId}`).then(d => d.achievements)

// ===== localStorage helpers =====

export const getUserId = () => {
  const id = localStorage.getItem('userId')
  return id ? parseInt(id) : null
}

export const setUserId = (id) => {
  localStorage.setItem('userId', String(id))
}

export const clearUser = () => {
  localStorage.removeItem('userId')
  localStorage.removeItem('userName')
  localStorage.removeItem('userLanguage')
}

// ===== CSV Export =====

export const exportProgressCSV = (userId) =>
  axios.get(`/api/stats/${userId}/export-csv`, { responseType: 'blob' })

// ===== Obsidian Export =====

export const exportObsidian = (lessonId, dayOffset = 0, upload = false) =>
  axios.get(`/api/lessons/${lessonId}/export-obsidian`, {
    params: { day_offset: dayOffset, upload },
    responseType: upload ? 'json' : 'blob',
  })

// ===== Study Plan =====

export const getStudyPlan = (userId) =>
  api.get(`/lessons/study-plan/${userId}`)
