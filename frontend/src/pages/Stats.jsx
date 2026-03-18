import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  BarChart3, Flame, Star, Trophy, BookOpen,
  FlaskConical, Brain, TrendingUp, Target, Calendar,
  Download, Globe, Lightbulb, CheckCircle
} from 'lucide-react'
import axios from 'axios'
import { getUserId, getStats, getDailyTips, updateUserLanguage, getLanguageProfiles, getStudyPlan } from '../api/client'
import { NotificationSettings } from '../components/NotificationManager'
import { PageLoader } from '../components/LoadingSpinner'
import { useLanguage } from '../hooks/useLanguage'

export default function Stats() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tips, setTips] = useState([])
  const [tipsLoading, setTipsLoading] = useState(false)
  const [studyPlan, setStudyPlan] = useState(null)
  const [csvLoading, setCsvLoading] = useState(false)
  const [changingLanguage, setChangingLanguage] = useState(false)
  const [languageMsg, setLanguageMsg] = useState('')
  const [languageProfiles, setLanguageProfiles] = useState(null)
  const navigate = useNavigate()
  const userId = getUserId()
  const { lang, setLang, t, targetLanguage } = useLanguage()

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
    getStats(userId)
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false))
    getLanguageProfiles(userId)
      .then(setLanguageProfiles)
      .catch(() => {})
    getStudyPlan(userId).then(setStudyPlan).catch(() => {})
  }, [userId])

  useEffect(() => {
    if (!userId) return
    const today = new Date().toISOString().slice(0, 10)
    const cachedDate = localStorage.getItem('tips_date')
    const cachedData = localStorage.getItem('tips_data')
    if (cachedDate === today && cachedData) {
      try {
        setTips(JSON.parse(cachedData))
        return
      } catch {}
    }
    setTipsLoading(true)
    getDailyTips(userId)
      .then(data => {
        const tips = data.tips || []
        setTips(tips)
        localStorage.setItem('tips_date', today)
        localStorage.setItem('tips_data', JSON.stringify(tips))
      })
      .catch(() => {})
      .finally(() => setTipsLoading(false))
  }, [userId])

  const handleDownloadCSV = async () => {
    if (!userId) return
    setCsvLoading(true)
    try {
      const response = await axios.get(`/api/stats/${userId}/export-csv`, { responseType: 'blob' })
      const url = URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }))
      const link = document.createElement('a')
      link.href = url
      link.download = `progress_${userId}.csv`
      link.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      console.error('CSV download failed:', e)
    } finally {
      setCsvLoading(false)
    }
  }

  const LANGUAGES = ['German', 'English', 'Spanish', 'Russian', 'Chinese']

  const LANG_FLAGS = {
    German: '🇩🇪',
    English: '🇬🇧',
    Spanish: '🇪🇸',
    Russian: '🇷🇺',
    Chinese: '🇨🇳',
  }

  const handleChangeLanguage = async (newLanguage) => {
    if (!userId || newLanguage === stats?.user?.target_language) return
    setChangingLanguage(true)
    try {
      const result = await updateUserLanguage(userId, newLanguage)
      localStorage.removeItem('tips_date')
      localStorage.removeItem('tips_data')
      if (result.needs_placement) {
        navigate(`/placement?language=${encodeURIComponent(newLanguage)}&userId=${userId}`)
      } else {
        setLanguageMsg(`Zmieniono na ${newLanguage}. Odśwież stronę.`)
        setTimeout(() => window.location.reload(), 1500)
      }
    } catch (e) {
      setLanguageMsg('Błąd: ' + e.message)
    } finally {
      setChangingLanguage(false)
    }
  }

  const handleRegenerateLesson = async () => {
    if (!userId) return
    try {
      await fetch(`/api/lessons/next/${userId}`, { method: 'POST' })
      window.location.href = '/lesson'
    } catch (e) {
      alert('Błąd: ' + e.message)
    }
  }

  if (loading) return <PageLoader text={t('stats.loading')} />
  if (!stats) return null

  const { user, level_info, lessons, tests, flashcards, error_categories, error_examples, achievements } = stats

  const CATEGORY_LABELS = {
    grammar: 'Gramatyka',
    vocabulary: 'Słownictwo',
    word_order: 'Szyk zdania',
    articles: 'Rodzajniki',
    verb_conjugation: 'Koniugacja',
    prepositions: 'Przyimki',
    spelling: 'Pisownia',
    pronunciation: 'Wymowa',
    case: 'Przypadki',
    comprehension: 'Rozumienie',
    syntax: 'Składnia',
    pronunciation_spelling: 'Wymowa/Pisownia',
    fluency: 'Płynność',
    register: 'Rejestr',
    application: 'Zastosowanie',
    unknown: 'Inne',
  }

  const CATEGORY_ADVICE = {
    grammar: 'Popracuj nad zasadami gramatycznymi — deklinacje, koniugacje, czasy gramatyczne.',
    vocabulary: 'Rozszerz słownictwo — ucz się nowych słów w kontekście zdań.',
    word_order: 'Ćwicz szyk zdania — zwróć uwagę na kolejność słów w zdaniach podrzędnych.',
    articles: 'Ucz się rodzajników i rodzaju gramatycznego rzeczowników na pamięć.',
    verb_conjugation: 'Ćwicz odmianę czasowników — szczególnie nieregularne i modalne.',
    prepositions: 'Zapamiętuj przyimki z ich przypadkami — lista typowych połączeń.',
    spelling: 'Ćwicz pisownię — zwróć uwagę na podwójne litery i wyjątki ortograficzne.',
    pronunciation: 'Słuchaj native speakerów i powtarzaj na głos — ćwicz trudne dźwięki.',
    case: 'Ćwicz przypadki gramatyczne — szczególnie Akkusativ i Dativ z przyimkami.',
    comprehension: 'Ćwicz rozumienie ze słuchu i z czytania — więcej ekspozycji na język.',
    syntax: 'Popracuj nad budową zdań złożonych i spójnikami.',
    pronunciation_spelling: 'Ćwicz wymowę i pisownię — słuchaj native speakerów i powtarzaj.',
    fluency: 'Mów więcej i nie bój się błędów — liczy się płynność rozmowy.',
    register: 'Ćwicz różne rejestry języka — formalny i nieformalny styl.',
    application: 'Ćwicz zastosowanie wiedzy w praktycznych sytuacjach.',
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <BarChart3 className="w-7 h-7 text-blue-400" />
        <div>
          <h1 className="text-2xl font-bold">{t('stats.title')}</h1>
          <p className="text-gray-400">{user?.name} · {user?.target_language} · {user?.cefr_level}</p>
        </div>
      </div>

      {/* XP & Level */}
      <div className="card mb-6 bg-gradient-to-r from-indigo-900/40 to-purple-900/40 border-indigo-700/30">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center">
            <span className="text-xl font-bold">{level_info?.level}</span>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold">{level_info?.level_name}</h2>
            <p className="text-gray-400 text-sm">
              {t('stats.level')} {level_info?.level}/{level_info?.max_level || 50} ·{' '}
              {level_info?.xp} / {level_info?.next_level_xp} XP
            </p>
            <div className="progress-bar mt-2">
              <div
                className="progress-fill bg-gradient-to-r from-indigo-500 to-purple-500"
                style={{ width: `${level_info?.progress_percent || 0}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Today's Activity Completion — Wskaźnik ukończenia */}
      <div className="card mb-6">
        <h2 className="section-title flex items-center gap-2 mb-3">
          <CheckCircle className="w-5 h-5 text-emerald-400" />
          Wskaźnik ukończenia — dziś
        </h2>
        <TodayCompletion stats={stats} />
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatBox
          icon={<Flame className="w-6 h-6 text-orange-400" />}
          label={t('stats.streak')}
          value={`${user?.streak_days || 0} ${t('stats.days')}`}
          color="orange"
        />
        <StatBox
          icon={<Star className="w-6 h-6 text-yellow-400" />}
          label={t('stats.totalXP')}
          value={user?.total_xp || 0}
          color="yellow"
        />
        <StatBox
          icon={<BookOpen className="w-6 h-6 text-blue-400" />}
          label={t('stats.lessons')}
          value={`${lessons?.completed || 0}/${lessons?.total || 0}`}
          color="blue"
        />
        <StatBox
          icon={<Trophy className="w-6 h-6 text-emerald-400" />}
          label={t('stats.avgScore')}
          value={`${tests?.average_score || 0}%`}
          color="emerald"
        />
      </div>

      {/* Test Score History List */}
      {tests?.history?.length > 0 && (
        <div className="card mb-6">
          <h2 className="section-title flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            {t('stats.testHistory')}
          </h2>
          <div className="space-y-2 mb-3">
            {tests.history.map((item, i) => {
              const pct = Math.round(item.score)
              const color = pct >= 80 ? 'text-emerald-400' : pct >= 60 ? 'text-yellow-400' : 'text-red-400'
              return (
                <div key={i} className="flex items-center justify-between py-1.5 border-b border-gray-800 last:border-0">
                  <span className="text-gray-400 text-sm">{item.date}</span>
                  <span className={`text-2xl font-bold ${color}`}>{pct}%</span>
                </div>
              )
            })}
          </div>
          <div className="flex gap-4 text-xs text-gray-500">
            <span>{t('stats.best')} <span className="text-emerald-400">{tests.best_score}%</span></span>
            <span>{t('stats.average')} <span className="text-yellow-400">{tests.average_score}%</span></span>
            <span>{t('stats.testsTaken')} <span className="text-blue-400">{tests.total_taken}</span></span>
          </div>
        </div>
      )}

      {/* Lesson Completion */}
      {lessons?.history?.length > 0 && (
        <div className="card mb-6">
          <h2 className="section-title flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            {t('stats.recentLessons')}
          </h2>
          <div className="space-y-2">
            {lessons.history.map((lesson, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                  lesson.completed ? 'bg-emerald-700 text-emerald-100' : 'bg-gray-700 text-gray-400'
                }`}>
                  {lesson.day}
                </div>
                <div className="flex-1">
                  <p className={`text-sm ${lesson.completed ? 'text-gray-300' : 'text-gray-500'}`}>
                    {(lesson.title || '').replace(/^Day\s+\d+[:\s]*/i, '').replace(/^Dzień\s+\d+[:\s]*/i, '') || lesson.title}
                  </p>
                </div>
                <span className="text-xs text-gray-600">{lesson.date}</span>
                {lesson.completed && (
                  <div className="w-4 h-4 text-emerald-400">✓</div>
                )}
              </div>
            ))}
          </div>
          {lessons.completion_rate !== undefined && (
            <div className="mt-3 pt-3 border-t border-gray-800">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">{t('stats.completionRate')}</span>
                <span className="text-emerald-400">{lessons.completion_rate}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill bg-emerald-500"
                  style={{ width: `${lessons.completion_rate}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Lesson Plan / Study Plan */}
      {studyPlan?.plan && (
        <LessonPlanCard plan={studyPlan.plan} currentLesson={studyPlan.current_lesson} />
      )}

      {/* Error Categories */}
      {error_categories && Object.keys(error_categories).length > 0 && (
        <ErrorCategoriesCard
          error_categories={error_categories}
          error_examples={error_examples}
          CATEGORY_LABELS={CATEGORY_LABELS}
          CATEGORY_ADVICE={CATEGORY_ADVICE}
          t={t}
        />
      )}

      {/* Achievements */}
      {achievements && (
        <div className="card mb-6">
          <h2 className="section-title flex items-center gap-2 mb-1">
            <Trophy className="w-5 h-5 text-yellow-400" />
            {t('stats.achievements')}
          </h2>
          <p className="text-gray-500 text-xs mb-4">
            {achievements.earned}/{achievements.total} {t('stats.unlocked')}
          </p>
          <div className="progress-bar mb-4">
            <div
              className="progress-fill bg-yellow-500"
              style={{ width: `${achievements.total ? (achievements.earned / achievements.total) * 100 : 0}%` }}
            />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            {achievements.achievements?.map((ach) => {
              const titleKey = `ach.${ach.type}.title`
              const descKey = `ach.${ach.type}.desc`
              const displayTitle = t(titleKey) !== titleKey ? t(titleKey) : ach.title
              const displayDesc = t(descKey) !== descKey ? t(descKey) : ach.description
              return (
                <div
                  key={ach.type}
                  className={`rounded-lg p-3 text-center transition-all ${
                    ach.earned
                      ? 'bg-yellow-900/20 border border-yellow-700/40'
                      : 'bg-gray-800/50 opacity-40'
                  }`}
                  title={displayDesc}
                >
                  <div className="text-2xl mb-1">{ach.icon}</div>
                  <p className={`text-xs font-medium ${ach.earned ? 'text-yellow-300' : 'text-gray-500'}`}>
                    {displayTitle}
                  </p>
                  {ach.earned && ach.unlocked_at && (
                    <p className="text-[10px] text-gray-600 mt-0.5">
                      {new Date(ach.unlocked_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Daily Tips */}
      <div className="card mb-6">
        <h2 className="section-title flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          {t('stats.tips')}
        </h2>
        {tipsLoading ? (
          <p className="text-gray-400 text-sm">{t('stats.loadingTips')}</p>
        ) : tips.length === 0 ? (
          <p className="text-gray-400 text-sm">{t('stats.noTips')}</p>
        ) : (
          <div className="space-y-4">
            {tips.map((tip, i) => (
              <div key={i} className="bg-gray-800/60 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                    tip.type === 'grammar' ? 'bg-blue-900/50 text-blue-300' :
                    tip.type === 'vocabulary' ? 'bg-emerald-900/50 text-emerald-300' :
                    tip.type === 'culture' ? 'bg-purple-900/50 text-purple-300' :
                    'bg-yellow-900/50 text-yellow-300'
                  }`}>{
                    tip.type === 'grammar' ? 'Gramatyka' :
                    tip.type === 'vocabulary' ? 'Słownictwo' :
                    tip.type === 'culture' ? 'Kultura' :
                    tip.type === 'memory_tip' ? 'Zapamiętywanie' :
                    tip.type || 'Wskazówka'
                  }</span>
                  <p className="font-semibold text-gray-100 text-sm">{tip.title}</p>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">{tip.content}</p>
                {tip.source && (
                  <p className="text-gray-500 text-xs mt-2 italic">— {tip.source}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Settings */}
      <div className="card mb-6">
        <h2 className="section-title flex items-center gap-2">
          <Globe className="w-5 h-5 text-indigo-400" />
          {t('stats.settings')}
        </h2>

        {/* UI Language Toggle */}
        <div className="flex items-center justify-between mb-4">
          <span className="text-gray-300 text-sm">{t('stats.uiLanguage')}</span>
          <div className="flex gap-2">
            <button
              onClick={() => setLang('pl')}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                lang === 'pl' ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              {t('stats.polishMode')}
            </button>
            <button
              onClick={() => setLang('hardcore')}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                lang === 'hardcore' ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              Hardcore ({targetLanguage})
            </button>
          </div>
        </div>

        {/* Target Language Change */}
        <div className="mb-4 mt-4">
          <span className="text-gray-300 text-sm block mb-1">Zmień język nauki</span>
          <span className="text-gray-500 text-xs mb-3 block">Progres dla każdego języka jest zachowywany oddzielnie</span>
          <div className="grid grid-cols-5 gap-2">
            {LANGUAGES.map(lng => {
              const profile = languageProfiles?.languages?.find(p => p.language === lng)
              const isActive = user?.target_language === lng
              const cefr = profile?.cefr_level
              const started = profile?.started
              return (
                <button
                  key={lng}
                  onClick={() => handleChangeLanguage(lng)}
                  disabled={changingLanguage || isActive}
                  className={`flex flex-col items-center gap-1 p-2 rounded-lg border text-center transition-all ${
                    isActive
                      ? 'bg-indigo-700/40 border-indigo-500 text-white'
                      : started
                      ? 'bg-gray-800 border-gray-600 text-gray-300 hover:border-indigo-500'
                      : 'bg-gray-900/50 border-gray-800 text-gray-500 hover:border-gray-600'
                  } disabled:cursor-default`}
                >
                  <span className="text-xl">{LANG_FLAGS[lng]}</span>
                  <span className="text-xs font-medium leading-tight">{lng}</span>
                  {cefr ? (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                      isActive ? 'bg-indigo-500 text-white' : 'bg-gray-700 text-gray-300'
                    }`}>{cefr}</span>
                  ) : (
                    <span className="text-[10px] text-gray-600">—</span>
                  )}
                  {profile?.lessons_completed > 0 && (
                    <span className="text-[10px] text-gray-500">{profile.lessons_completed} lekcji</span>
                  )}
                </button>
              )
            })}
          </div>
          {changingLanguage && <p className="text-xs text-indigo-400 mt-2">Zmienianie języka...</p>}
          {languageMsg && <p className="text-sm text-indigo-300 mt-2">{languageMsg}</p>}
        </div>

        <button
          onClick={handleRegenerateLesson}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800 hover:bg-red-900/30 hover:border-red-700/30 border border-transparent text-gray-300 hover:text-red-300 text-sm transition-colors mt-2"
        >
          Wygeneruj następną lekcję
        </button>

        {/* CSV Export */}
        <button
          onClick={handleDownloadCSV}
          disabled={csvLoading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors disabled:opacity-50 mt-2"
        >
          <Download className="w-4 h-4" />
          {csvLoading ? '...' : t('stats.downloadCSV')}
        </button>
      </div>

      {/* Notification Settings */}
      <NotificationSettings />

      {/* Member since */}
      <p className="text-center text-gray-600 text-sm mt-6">
        {t('stats.memberSince')} {user?.member_since}
      </p>
    </div>
  )
}

function ErrorCategoriesCard({ error_categories, error_examples, CATEGORY_LABELS, CATEGORY_ADVICE, t }) {
  const [expanded, setExpanded] = useState({})
  const total = Object.values(error_categories).reduce((a, b) => a + b, 0)

  return (
    <div className="card mb-6">
      <div className="flex items-center justify-between mb-1">
        <h2 className="section-title flex items-center gap-2">
          <Target className="w-5 h-5 text-red-400" />
          {t('stats.errorAnalysis')}
        </h2>
        <Link to="/errors" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
          Przegląd wszystkich błędów →
        </Link>
      </div>
      <p className="text-gray-400 text-sm mb-4">{t('stats.errorAreas')}</p>
      <div className="space-y-2">
        {Object.entries(error_categories)
          .sort((a, b) => b[1] - a[1])
          .map(([category, count]) => {
            const pct = Math.round((count / total) * 100)
            const examples = error_examples?.[category] || []
            const isOpen = expanded[category]
            const hasDetails = examples.length > 0 || !!CATEGORY_ADVICE[category]
            return (
              <div key={category} className="rounded-lg overflow-hidden">
                <button
                  className="w-full text-left"
                  onClick={() => hasDetails && setExpanded(e => ({ ...e, [category]: !e[category] }))}
                >
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300 flex items-center gap-1">
                      {CATEGORY_LABELS[category] || category}
                      {hasDetails && (
                        <span className="text-gray-600 text-xs ml-1">{isOpen ? '▲' : '▼'}</span>
                      )}
                    </span>
                    <span className="text-gray-500">{count} {t('stats.errors')} ({pct}%)</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill bg-red-500" style={{ width: `${pct}%` }} />
                  </div>
                </button>
                {isOpen && hasDetails && (
                  <div className="mt-2 pl-2 space-y-1">
                    {examples.map((ex, ei) => (
                      <div key={ei} className="text-xs text-gray-500 flex gap-2">
                        <span className="text-red-400 shrink-0">✗</span>
                        <span className="truncate">{ex.question}</span>
                        {ex.correct && <span className="text-emerald-500 shrink-0">→ {ex.correct}</span>}
                      </div>
                    ))}
                    {CATEGORY_ADVICE[category] && (
                      <p className="text-xs text-indigo-400 mt-1 italic">💡 {CATEGORY_ADVICE[category]}</p>
                    )}
                  </div>
                )}
              </div>
            )
          })}
      </div>
    </div>
  )
}

function StatBox({ icon, label, value, color }) {
  return (
    <div className="card text-center">
      <div className="flex justify-center mb-2">{icon}</div>
      <div className={`text-xl font-bold text-${color}-400`}>{value}</div>
      <div className="text-xs text-gray-500 mt-0.5">{label}</div>
    </div>
  )
}

function TodayCompletion({ stats }) {
  // Read daily tabs from localStorage
  const getDailyTabs = () => {
    try {
      const raw = localStorage.getItem('daily_tabs')
      if (!raw) return []
      const parsed = JSON.parse(raw)
      const today = new Date().toISOString().slice(0, 10)
      if (parsed.date !== today) return []
      return parsed.tabs || []
    } catch { return [] }
  }
  const tabs = getDailyTabs()

  // Check if lesson completed today
  const lessonDoneToday = stats?.lessons?.history?.some(
    l => l.completed && l.date === new Date().toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' })
  ) || tabs.includes('lesson')

  // Check if test done today
  const testDoneToday = stats?.tests?.history?.some(
    t => t.date === new Date().toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' })
  ) || tabs.includes('test')

  const activities = [
    { key: 'lesson', label: 'Lekcja', icon: '📚', done: lessonDoneToday },
    { key: 'test', label: 'Test', icon: '📝', done: testDoneToday },
    { key: 'conversation', label: 'Rozmowa', icon: '💬', done: tabs.includes('conversation') },
    { key: 'news', label: 'Newsy/Wymowa', icon: '📰', done: tabs.includes('news') || tabs.includes('pronunciation') || tabs.includes('videos') },
  ]

  const doneCount = activities.filter(a => a.done).length
  const pct = Math.round((doneCount / activities.length) * 100)

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <span className="text-gray-400 text-sm">{doneCount}/{activities.length} aktywności ukończonych</span>
        <span className={`text-sm font-bold ${pct === 100 ? 'text-emerald-400' : pct >= 50 ? 'text-yellow-400' : 'text-gray-400'}`}>{pct}%</span>
      </div>
      <div className="progress-bar mb-4">
        <div className={`progress-fill ${pct === 100 ? 'bg-emerald-500' : 'bg-indigo-500'}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {activities.map(act => (
          <div key={act.key} className={`flex flex-col items-center gap-1 p-2 rounded-lg border text-center ${
            act.done
              ? 'bg-emerald-900/20 border-emerald-700/40'
              : 'bg-gray-800/50 border-gray-700/40'
          }`}>
            <span className="text-xl">{act.icon}</span>
            <span className={`text-xs font-medium ${act.done ? 'text-emerald-400' : 'text-gray-500'}`}>{act.label}</span>
            <span className={`text-xs ${act.done ? 'text-emerald-400' : 'text-gray-600'}`}>{act.done ? '✓' : '—'}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function LessonPlanCard({ plan, currentLesson }) {
  const [expanded, setExpanded] = useState(false)
  const weeks = plan?.weeks || []

  return (
    <div className="card mb-6">
      <button
        className="w-full flex items-center justify-between"
        onClick={() => setExpanded(e => !e)}
      >
        <h2 className="section-title flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-blue-400" />
          Plan nauki
        </h2>
        <span className="text-gray-500 text-sm">{expanded ? '▲' : '▼'}</span>
      </button>
      {expanded && (
        <div className="mt-4 space-y-4">
          {weeks.length > 0 ? (
            weeks.map((week, wi) => (
              <div key={wi}>
                <h3 className="text-sm font-semibold text-indigo-300 mb-2">
                  Tydzień {week.week || wi + 1}: {week.theme || week.focus || ''}
                </h3>
                <div className="space-y-1">
                  {(week.days || week.lessons || []).map((day, di) => (
                    <div key={di} className="flex items-start gap-2 text-sm py-1 border-b border-gray-800 last:border-0">
                      <span className="text-gray-600 shrink-0 w-16 text-xs">
                        {day.day ? `Dzień ${day.day}` : `Lekcja ${di + 1}`}
                      </span>
                      <span className="text-gray-300 flex-1">{day.topic || day.title || day.content || JSON.stringify(day)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <pre className="text-gray-400 text-xs whitespace-pre-wrap">{JSON.stringify(plan, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  )
}
