import { Link, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  BookOpen, FlaskConical, MessageSquare, LayoutGrid,
  BarChart3, Flame, Star, Brain, Timer, Newspaper, Mic,
  BookmarkPlus, X, Loader2, Video, AlertTriangle
} from 'lucide-react'
import { getUserId, getStats, addFlashcardAI } from '../api/client'
import { useLanguage } from '../hooks/useLanguage'

function getDailyTabsNav() {
  try {
    const raw = localStorage.getItem('daily_tabs')
    if (!raw) return []
    const parsed = JSON.parse(raw)
    const today = new Date().toISOString().slice(0, 10)
    if (parsed.date !== today) return []
    return parsed.tabs || []
  } catch { return [] }
}

export default function NavBar({ dailyTabs: dailyTabsProp }) {
  const location = useLocation()
  const [userStats, setUserStats] = useState(null)
  const userId = getUserId()
  const { t } = useLanguage()
  const dailyTabs = dailyTabsProp || getDailyTabsNav()
  const dailyProgress = Math.min(100, Math.round((dailyTabs.length / 4) * 100))

  const [flashOpen, setFlashOpen] = useState(false)
  const [flashWord, setFlashWord] = useState('')
  const [flashLoading, setFlashLoading] = useState(false)
  const [flashMsg, setFlashMsg] = useState('')

  const navItems = [
    { to: '/', label: t('nav.home'), icon: LayoutGrid, exact: true },
    { to: '/lesson', label: t('nav.lesson'), icon: BookOpen },
    { to: '/pronunciation', label: t('nav.pronounce'), icon: Mic },
    { to: '/conversation', label: t('nav.speak'), icon: MessageSquare },
    { to: '/flashcards', label: t('nav.flashcards'), icon: Brain },
    { to: '/test', label: t('nav.test'), icon: FlaskConical },
    { to: '/news', label: t('nav.news'), icon: Newspaper },
    { to: '/videos', label: t('nav.videos'), icon: Video },
    { to: '/quickmode', label: t('nav.quickmode'), icon: Timer },
    { to: '/stats', label: t('nav.stats'), icon: BarChart3 },
    { to: '/errors', label: 'Błędy', icon: AlertTriangle },
  ]

  useEffect(() => {
    if (userId) {
      getStats(userId)
        .then(data => setUserStats(data))
        .catch(() => {})
    }
  }, [userId, location.pathname])

  const handleQuickFlash = async () => {
    if (!flashWord.trim() || !userId) return
    setFlashLoading(true)
    setFlashMsg('')
    try {
      const res = await addFlashcardAI(userId, flashWord.trim())
      if (res && res.success === false) {
        setFlashMsg(res.message || 'Już istnieje')
      } else {
        setFlashMsg('Dodano! ✓')
        setFlashWord('')
        setTimeout(() => {
          setFlashMsg('')
          setFlashOpen(false)
        }, 1500)
      }
    } catch (e) {
      setFlashMsg('Błąd: ' + e.message)
    } finally {
      setFlashLoading(false)
    }
  }

  const isActive = (to, exact = false) => {
    if (exact) return location.pathname === to
    return location.pathname.startsWith(to) && to !== '/'
  }

  return (
    <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
      {/* Daily progress bar */}
      <div className="h-1 bg-gray-800 w-full">
        <div
          className="h-1 bg-indigo-500 transition-all duration-500"
          style={{ width: `${dailyProgress}%` }}
          title={`Dzienny postęp: ${dailyProgress}%`}
        />
      </div>
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg gradient-text hidden sm:block">LinguaAI</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            {navItems.map(({ to, label, icon: Icon, exact }) => (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                  isActive(to, exact) || (exact && location.pathname === to)
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden md:block">{label}</span>
              </Link>
            ))}
          </div>

          {/* Right side: stats + flash quick-add */}
          <div className="flex items-center gap-2">
            {userStats && (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 bg-gray-800 rounded-lg px-3 py-1.5">
                  <Flame className="w-4 h-4 text-orange-400" />
                  <span className="text-sm font-semibold text-orange-400">
                    {userStats.user?.streak_days || 0}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 bg-gray-800 rounded-lg px-3 py-1.5">
                  <Star className="w-4 h-4 text-yellow-400" />
                  <span className="text-sm font-semibold text-yellow-400">
                    {userStats.user?.total_xp || 0}
                  </span>
                </div>
                {userStats.user?.cefr_level && (
                  <div className="badge-blue hidden sm:flex">
                    {userStats.user.cefr_level}
                  </div>
                )}
              </div>
            )}

            {!userStats && !userId && (
              <Link to="/placement" className="btn-primary text-sm py-1.5">
                {t('nav.getStarted')}
              </Link>
            )}

            {/* Flash quick-add — always visible on desktop */}
            {userId && (
              <div className="relative flex items-center gap-1.5">
                {/* Desktop: inline input */}
                <div className="hidden md:flex items-center gap-1.5 bg-gray-800 border border-gray-700 rounded-lg px-2 py-1">
                  <BookmarkPlus className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <input
                    className="bg-transparent text-sm text-gray-200 placeholder-gray-500 outline-none w-28"
                    placeholder="Dodaj fiszkę..."
                    value={flashWord}
                    onChange={e => { setFlashWord(e.target.value); setFlashMsg('') }}
                    onKeyDown={e => e.key === 'Enter' && handleQuickFlash()}
                  />
                  {flashLoading && <Loader2 className="w-3 h-3 animate-spin text-indigo-400 shrink-0" />}
                  {flashMsg && <span className={`text-xs shrink-0 ${flashMsg.includes('Błąd') || flashMsg.includes('już istnieje') ? 'text-red-400' : 'text-emerald-400'}`}>{flashMsg.includes('Dodano') ? '✓' : '!'}</span>}
                </div>
                {/* Mobile: toggle button */}
                <button onClick={() => setFlashOpen(o => !o)} className="md:hidden w-9 h-9 rounded-lg bg-indigo-700 hover:bg-indigo-600 flex items-center justify-center" title="Dodaj fiszkę">
                  <BookmarkPlus className="w-4 h-4 text-white" />
                </button>
                {flashOpen && (
                  <div className="absolute right-0 top-11 bg-gray-800 border border-indigo-700/50 rounded-xl shadow-2xl p-3 w-60 z-50 md:hidden">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-indigo-300">Dodaj fiszkę (AI)</span>
                      <button onClick={() => { setFlashOpen(false); setFlashMsg(''); setFlashWord('') }}><X className="w-3.5 h-3.5 text-gray-500" /></button>
                    </div>
                    <input className="input-field text-sm mb-2" placeholder="Słowo..." value={flashWord} onChange={e => setFlashWord(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleQuickFlash()} autoFocus />
                    {flashMsg && <p className={`text-xs mb-2 ${flashMsg.includes('Błąd') || flashMsg.includes('już istnieje') ? 'text-red-400' : 'text-emerald-400'}`}>{flashMsg}</p>}
                    <button className="btn-primary w-full text-xs py-1.5 flex items-center justify-center gap-1" onClick={handleQuickFlash} disabled={flashLoading || !flashWord.trim()}>
                      {flashLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <BookmarkPlus className="w-3 h-3" />}
                      Dodaj z AI
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
