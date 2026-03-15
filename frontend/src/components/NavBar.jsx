import { Link, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  BookOpen, FlaskConical, MessageSquare, LayoutGrid,
  BarChart3, Flame, Star, Brain, Timer, Newspaper, Mic
} from 'lucide-react'
import { getUserId, getStats } from '../api/client'

const navItems = [
  { to: '/', label: 'Home', icon: LayoutGrid, exact: true },
  { to: '/lesson', label: 'Lesson', icon: BookOpen },
  { to: '/test', label: 'Test', icon: FlaskConical },
  { to: '/flashcards', label: 'Flashcards', icon: Brain },
  { to: '/conversation', label: 'Speak', icon: MessageSquare },
  { to: '/quickmode', label: '15 min', icon: Timer },
  { to: '/news', label: 'News', icon: Newspaper },
  { to: '/pronunciation', label: 'Pronounce', icon: Mic },
  { to: '/stats', label: 'Stats', icon: BarChart3 },
]

export default function NavBar() {
  const location = useLocation()
  const [userStats, setUserStats] = useState(null)
  const userId = getUserId()

  useEffect(() => {
    if (userId) {
      getStats(userId)
        .then(data => setUserStats(data))
        .catch(() => {})
    }
  }, [userId, location.pathname])

  const isActive = (to, exact = false) => {
    if (exact) return location.pathname === to
    return location.pathname.startsWith(to) && to !== '/'
  }

  return (
    <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
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

          {/* User Stats */}
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
              Get Started
            </Link>
          )}
        </div>
      </div>
    </nav>
  )
}
