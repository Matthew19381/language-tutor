import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Timer, CheckCircle, BookOpen, FlaskConical, Brain, Mic, Newspaper, Play, Pause, RotateCcw } from 'lucide-react'
import { getUserId } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'
import { useLanguage } from '../hooks/useLanguage'
import axios from 'axios'

const LANG_DISPLAY = {
  German: 'Niemiecki', English: 'Angielski', Spanish: 'Hiszpański',
  Russian: 'Rosyjski', Chinese: 'Chiński',
}

const ICON_MAP = {
  BookOpen: <BookOpen className="w-5 h-5" />,
  FlaskConical: <FlaskConical className="w-5 h-5" />,
  Brain: <Brain className="w-5 h-5" />,
  Mic: <Mic className="w-5 h-5" />,
  Newspaper: <Newspaper className="w-5 h-5" />,
}

const TIMER_SECONDS = 15 * 60
const STORAGE_KEY_START = 'quickmode_start'
const STORAGE_KEY_DURATION = 'quickmode_duration'

export default function QuickMode() {
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(true)
  const [checked, setChecked] = useState({})
  const [customMinutes, setCustomMinutes] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY_DURATION)
    return saved ? parseInt(saved) : 15
  })
  const [timerActive, setTimerActive] = useState(() => {
    const startTime = localStorage.getItem(STORAGE_KEY_START)
    if (!startTime) return false
    const duration = parseInt(localStorage.getItem(STORAGE_KEY_DURATION) || '15') * 60
    const elapsed = Math.floor((Date.now() - parseInt(startTime)) / 1000)
    return elapsed > 0 && elapsed < duration
  })
  const [secondsLeft, setSecondsLeft] = useState(() => {
    const startTime = localStorage.getItem(STORAGE_KEY_START)
    const duration = parseInt(localStorage.getItem(STORAGE_KEY_DURATION) || '15') * 60
    if (startTime) {
      const elapsed = Math.floor((Date.now() - parseInt(startTime)) / 1000)
      const remaining = duration - elapsed
      return remaining > 0 ? remaining : 0
    }
    return parseInt(localStorage.getItem(STORAGE_KEY_DURATION) || '15') * 60
  })
  const intervalRef = useRef(null)
  const navigate = useNavigate()
  const userId = getUserId()
  const { t } = useLanguage()

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
    axios.get(`/api/quickmode/${userId}`)
      .then(r => setPlan(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [userId])

  useEffect(() => {
    if (timerActive && secondsLeft > 0) {
      intervalRef.current = setInterval(() => {
        setSecondsLeft(s => {
          if (s <= 1) {
            clearInterval(intervalRef.current)
            setTimerActive(false)
            return 0
          }
          return s - 1
        })
      }, 1000)
    } else {
      clearInterval(intervalRef.current)
    }
    return () => clearInterval(intervalRef.current)
  }, [timerActive])

  const toggleTimer = () => {
    setTimerActive(a => {
      if (!a) {
        localStorage.setItem(STORAGE_KEY_START, String(Date.now() - (customMinutes * 60 - secondsLeft) * 1000))
        localStorage.setItem(STORAGE_KEY_DURATION, String(customMinutes))
      } else {
        localStorage.removeItem(STORAGE_KEY_START)
      }
      return !a
    })
  }
  const resetTimer = () => {
    setTimerActive(false)
    localStorage.removeItem(STORAGE_KEY_START)
    setSecondsLeft(customMinutes * 60)
  }

  const toggleCheck = (id) => setChecked(prev => ({ ...prev, [id]: !prev[id] }))

  const formatTime = (s) => {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
  }

  if (loading) return <PageLoader text={t('quick.loading')} />
  if (!plan) return null

  const allDone = plan.activities.filter(a => !a.completed).every(a => checked[a.id])
  const completedCount = plan.activities.filter(a => a.completed || checked[a.id]).length

  return (
    <div className="page-container max-w-xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Timer className="w-7 h-7 text-emerald-400" />
        <div>
          <h1 className="text-2xl font-bold">{t('quick.title')}</h1>
          <p className="text-gray-400">{t('quick.subtitle')} — {LANG_DISPLAY[plan.target_language] || plan.target_language} · {plan.cefr_level}</p>
        </div>
      </div>

      {/* Custom duration */}
      {!timerActive && secondsLeft === customMinutes * 60 && (
        <div className="flex items-center justify-center gap-3 mb-4">
          <span className="text-gray-400 text-sm">{t('quick.duration')}</span>
          {[5, 10, 15, 20, 30].map(min => (
            <button
              key={min}
              onClick={() => {
                setCustomMinutes(min)
                setSecondsLeft(min * 60)
                localStorage.setItem(STORAGE_KEY_DURATION, String(min))
              }}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                customMinutes === min ? 'bg-emerald-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              {min} min
            </button>
          ))}
        </div>
      )}

      {/* Timer */}
      <div className="card mb-6 text-center bg-gradient-to-r from-emerald-900/30 to-teal-900/30 border-emerald-700/30">
        <div className={`font-mono font-bold mb-4 ${
          secondsLeft <= 5 && secondsLeft > 0 ? 'text-red-500 animate-blink text-7xl' :
          secondsLeft < 60 ? 'text-red-400 text-6xl' :
          secondsLeft < 300 ? 'text-yellow-400 text-6xl' : 'text-emerald-400 text-6xl'
        }`}>
          {formatTime(secondsLeft)}
        </div>
        <div className="flex justify-center gap-3">
          <button
            onClick={toggleTimer}
            className={`flex items-center gap-2 px-6 py-2 rounded-lg font-semibold ${
              timerActive ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-emerald-600 hover:bg-emerald-700'
            } text-white transition-colors`}
          >
            {timerActive
              ? <><Pause className="w-4 h-4" /> {t('quick.pause')}</>
              : <><Play className="w-4 h-4" /> {t('quick.start')}</>
            }
          </button>
          <button
            onClick={resetTimer}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
        {secondsLeft === 0 && (
          <p className="text-emerald-400 font-semibold mt-3">{t('quick.timeUp')}</p>
        )}
      </div>

      {/* Progress */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-gray-400 text-sm">
          {completedCount}/{plan.activities.length} {t('quick.activities')}
        </p>
        <p className="text-gray-400 text-sm">
          ~{plan.total_estimated_minutes} {t('quick.estimated')}
        </p>
      </div>
      <div className="progress-bar mb-6">
        <div
          className="progress-fill bg-emerald-500"
          style={{ width: `${(completedCount / plan.activities.length) * 100}%` }}
        />
      </div>

      {/* Activity List */}
      <div className="space-y-3">
        {plan.activities.map((activity) => {
          const isDone = activity.completed || checked[activity.id]
          return (
            <div
              key={activity.id}
              className={`card flex items-center gap-4 transition-all ${
                isDone ? 'opacity-60' : 'cursor-pointer hover:border-indigo-600/50'
              }`}
            >
              <button
                onClick={() => !activity.completed && toggleCheck(activity.id)}
                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors ${
                  isDone ? 'bg-emerald-600 border-emerald-600' : 'border-gray-600 hover:border-emerald-500'
                }`}
              >
                {isDone && <CheckCircle className="w-4 h-4 text-white" />}
              </button>

              <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                isDone ? 'bg-gray-700' : 'bg-indigo-700'
              }`}>
                {ICON_MAP[activity.icon] || <BookOpen className="w-5 h-5" />}
              </div>

              <div className="flex-1">
                <p className={`font-medium ${isDone ? 'line-through text-gray-500' : ''}`}>
                  {activity.title}
                </p>
                <p className="text-gray-500 text-sm">{activity.description}</p>
              </div>

              <div className="text-right shrink-0">
                <span className="text-xs text-gray-500">{activity.estimated_minutes} min</span>
                {!isDone && (
                  <button
                    onClick={() => navigate(activity.route)}
                    className="block mt-1 text-indigo-400 hover:text-indigo-300 text-xs"
                  >
                    {t('quick.go')}
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {allDone && (
        <div className="card border-emerald-700/30 bg-emerald-900/10 text-center mt-6">
          <CheckCircle className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
          <p className="text-emerald-300 font-bold text-lg">{t('quick.allDone')}</p>
          <p className="text-gray-400 text-sm mt-1">{t('quick.completed15min')}</p>
        </div>
      )}
    </div>
  )
}
