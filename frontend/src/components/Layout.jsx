import { useState, useEffect, useCallback } from 'react'
import { Outlet } from 'react-router-dom'
import NavBar from './NavBar'
import NotificationManager from './NotificationManager'
import { getUserId, getStats } from '../api/client'
import { useLanguage } from '../hooks/useLanguage'
import { useNavigate, useLocation } from 'react-router-dom'
import { Timer } from 'lucide-react'

// Only these paths are auto-marked on visit (lesson + test require explicit completion)
const AUTO_VISIT_PATHS = ['/flashcards', '/conversation', '/quickmode', '/news', '/pronunciation']

function getTodayStr() {
  return new Date().toISOString().slice(0, 10)
}

function getDailyTabs() {
  try {
    const raw = localStorage.getItem('daily_tabs')
    if (!raw) return { date: getTodayStr(), tabs: [] }
    const parsed = JSON.parse(raw)
    if (parsed.date !== getTodayStr()) return { date: getTodayStr(), tabs: [] }
    return parsed
  } catch { return { date: getTodayStr(), tabs: [] } }
}

export default function Layout() {
  const [toasts, setToasts] = useState([])
  const userId = getUserId()
  const { t } = useLanguage()
  const navigate = useNavigate()
  const location = useLocation()
  const [timerDisplay, setTimerDisplay] = useState(null)

  // Daily progress state
  const [dailyTabs, setDailyTabs] = useState(() => getDailyTabs().tabs)

  useEffect(() => {
    const updateTimer = () => {
      const startTime = localStorage.getItem('quickmode_start')
      const duration = parseInt(localStorage.getItem('quickmode_duration') || '15') * 60
      if (!startTime) { setTimerDisplay(null); return }
      const elapsed = Math.floor((Date.now() - parseInt(startTime)) / 1000)
      const remaining = duration - elapsed
      if (remaining <= 0) {
        localStorage.removeItem('quickmode_start')
        setTimerDisplay(null)
      } else {
        const m = Math.floor(remaining / 60)
        const s = remaining % 60
        setTimerDisplay(`${m}:${s.toString().padStart(2, '0')}`)
      }
    }
    updateTimer()
    const interval = setInterval(updateTimer, 1000)
    return () => clearInterval(interval)
  }, [])

  // Poll for new achievements every time the layout mounts (route changes)
  const checkNewAchievements = useCallback(async () => {
    if (!userId) return
    try {
      const data = await getStats(userId)
      const newAchs = data?.new_achievements || []
      if (newAchs.length > 0) {
        setToasts(prev => [
          ...prev,
          ...newAchs.map((a, i) => ({ ...a, id: Date.now() + i }))
        ])
      }
    } catch (_) {}
  }, [userId])

  useEffect(() => {
    checkNewAchievements()
  }, [])

  // Track daily tab visits
  useEffect(() => {
    const path = location.pathname
    const isAutoPath = AUTO_VISIT_PATHS.some(p => path.startsWith(p))
    if (isAutoPath) {
      const key = path.replace('/', '').split('/')[0]
      const stored = getDailyTabs()
      if (!stored.tabs.includes(key)) {
        const updated = { date: getTodayStr(), tabs: [...stored.tabs, key] }
        localStorage.setItem('daily_tabs', JSON.stringify(updated))
        setDailyTabs(updated.tabs)
      }
    }
    // Reload daily tabs on every navigation to catch lesson/test completions
    setDailyTabs(getDailyTabs().tabs)
  }, [location.pathname])

  const removeToast = (id) => setToasts(prev => prev.filter(t => t.id !== id))

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar dailyTabs={dailyTabs} />
      <NotificationManager />
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Timer Badge */}
      {timerDisplay && (
        <button
          onClick={() => navigate('/quickmode')}
          className="fixed bottom-6 right-4 z-50 flex items-center gap-2 bg-emerald-700 hover:bg-emerald-600 text-white px-5 py-3 rounded-xl shadow-lg transition-colors"
        >
          <Timer className="w-6 h-6" />
          <span className="font-mono font-bold text-2xl">{timerDisplay}</span>
        </button>
      )}

      {/* Achievement toasts */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-xs">
        {toasts.map((toast) => (
          <AchievementToast
            key={toast.id}
            toast={toast}
            onClose={() => removeToast(toast.id)}
            label={t('achievement.unlocked')}
          />
        ))}
      </div>
    </div>
  )
}

function AchievementToast({ toast, onClose, label }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000)
    return () => clearTimeout(timer)
  }, [onClose])

  return (
    <div className="bg-gray-800 border border-yellow-600/50 rounded-xl px-4 py-3 shadow-2xl flex items-center gap-3 animate-fade-in">
      <span className="text-2xl">{toast.icon}</span>
      <div className="flex-1">
        <p className="text-yellow-300 font-semibold text-sm">{label}</p>
        <p className="text-white text-sm">{toast.title}</p>
        <p className="text-gray-400 text-xs">{toast.description}</p>
      </div>
      <button onClick={onClose} className="text-gray-500 hover:text-gray-300 text-lg leading-none">×</button>
    </div>
  )
}
