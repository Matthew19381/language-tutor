import { useState, useEffect, useCallback } from 'react'
import { Outlet } from 'react-router-dom'
import NavBar from './NavBar'
import NotificationManager from './NotificationManager'
import { getUserId, getStats } from '../api/client'
import { useLanguage } from '../hooks/useLanguage'

export default function Layout() {
  const [toasts, setToasts] = useState([])
  const userId = getUserId()
  const { t } = useLanguage()

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

  const removeToast = (id) => setToasts(prev => prev.filter(t => t.id !== id))

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar />
      <NotificationManager />
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Achievement Toasts */}
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
