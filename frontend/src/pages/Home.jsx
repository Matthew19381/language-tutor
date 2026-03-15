import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  BookOpen, FlaskConical, MessageSquare, Brain,
  Flame, Star, TrendingUp, ChevronRight, Sparkles,
  Target, Clock, CheckCircle
} from 'lucide-react'
import { getUserId, getStats, getDailyTips } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'

export default function Home() {
  const [stats, setStats] = useState(null)
  const [tips, setTips] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const userId = getUserId()

  useEffect(() => {
    if (!userId) {
      setLoading(false)
      return
    }
    Promise.all([
      getStats(userId),
      getDailyTips(userId)
    ])
      .then(([statsData, tipsData]) => {
        setStats(statsData)
        setTips(tipsData.tips || [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [userId])

  if (loading) return <PageLoader text="Loading your dashboard..." />

  if (!userId) {
    return <WelcomeScreen />
  }

  return (
    <div className="page-container">
      {/* Greeting */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-1">
          Welcome back, <span className="gradient-text">{stats?.user?.name || 'Learner'}</span>!
        </h1>
        <p className="text-gray-400">
          Learning {stats?.user?.target_language || 'your language'} — {stats?.user?.cefr_level || 'A1'} level
        </p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={<Flame className="w-6 h-6 text-orange-400" />}
          label="Day Streak"
          value={stats?.user?.streak_days || 0}
          color="orange"
        />
        <StatCard
          icon={<Star className="w-6 h-6 text-yellow-400" />}
          label="Total XP"
          value={stats?.user?.total_xp || 0}
          color="yellow"
        />
        <StatCard
          icon={<CheckCircle className="w-6 h-6 text-emerald-400" />}
          label="Lessons Done"
          value={stats?.lessons?.completed || 0}
          color="emerald"
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6 text-indigo-400" />}
          label="Avg Score"
          value={`${stats?.tests?.average_score || 0}%`}
          color="indigo"
        />
      </div>

      {/* Level Progress */}
      {stats?.level_info && (
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-2">
            <div>
              <span className="text-gray-400 text-sm">Level {stats.level_info.level}</span>
              <h3 className="text-lg font-semibold">{stats.level_info.level_name}</h3>
            </div>
            <div className="text-right">
              <span className="text-indigo-400 font-bold">{stats.level_info.xp} XP</span>
              <p className="text-gray-500 text-xs">/{stats.level_info.next_level_xp} for next level</p>
            </div>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill bg-indigo-500"
              style={{ width: `${stats.level_info.progress_percent}%` }}
            />
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <h2 className="section-title flex items-center gap-2">
        <Target className="w-5 h-5 text-indigo-400" />
        Today's Activities
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <ActionCard
          to="/lesson"
          icon={<BookOpen className="w-8 h-8 text-blue-400" />}
          title="Today's Lesson"
          description="Learn new vocabulary and grammar"
          color="blue"
          xp="+25 XP"
        />
        <ActionCard
          to="/test"
          icon={<FlaskConical className="w-8 h-8 text-purple-400" />}
          title="Daily Test"
          description="Test what you've learned today"
          color="purple"
          xp="+50 XP"
        />
        <ActionCard
          to="/conversation"
          icon={<MessageSquare className="w-8 h-8 text-emerald-400" />}
          title="Practice Speaking"
          description="Conversation with AI tutor"
          color="emerald"
          xp="+30 XP"
        />
      </div>

      {/* Flashcards due */}
      {stats?.flashcards?.due_today > 0 && (
        <div className="card mb-6 border-yellow-600/30 bg-yellow-900/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Brain className="w-6 h-6 text-yellow-400" />
              <div>
                <p className="font-semibold">Flashcards Due</p>
                <p className="text-gray-400 text-sm">
                  {stats.flashcards.due_today} cards ready for review
                </p>
              </div>
            </div>
            <Link to="/flashcards" className="btn-primary text-sm">
              Review Now
            </Link>
          </div>
        </div>
      )}

      {/* Daily Tips */}
      {tips.length > 0 && (
        <div className="mb-6">
          <h2 className="section-title flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-yellow-400" />
            Daily Tips
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tips.slice(0, 4).map((tip, i) => (
              <TipCard key={i} tip={tip} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function WelcomeScreen() {
  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="text-center max-w-2xl">
        <div className="w-20 h-20 bg-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 xp-glow">
          <BookOpen className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl font-bold mb-4">
          Learn Languages with <span className="gradient-text">AI Power</span>
        </h1>
        <p className="text-gray-400 text-lg mb-8 leading-relaxed">
          Personalized lessons, adaptive tests, flashcards, and AI conversation practice.
          Take the placement test to find your level and start learning today.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { icon: '📚', label: 'Daily Lessons' },
            { icon: '✍️', label: 'Smart Tests' },
            { icon: '🃏', label: 'Flashcards' },
            { icon: '💬', label: 'AI Conversation' },
          ].map((f, i) => (
            <div key={i} className="card text-center py-4">
              <div className="text-3xl mb-2">{f.icon}</div>
              <p className="text-sm text-gray-400">{f.label}</p>
            </div>
          ))}
        </div>

        <Link to="/placement" className="btn-primary text-lg py-3 px-8 inline-flex items-center gap-2">
          Start Placement Test
          <ChevronRight className="w-5 h-5" />
        </Link>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className="card text-center">
      <div className="flex justify-center mb-2">{icon}</div>
      <div className={`text-2xl font-bold text-${color}-400`}>{value}</div>
      <div className="text-xs text-gray-500 mt-1">{label}</div>
    </div>
  )
}

function ActionCard({ to, icon, title, description, color, xp }) {
  return (
    <Link to={to} className="card-hover">
      <div className="flex items-start gap-4">
        <div className={`p-3 rounded-xl bg-${color}-900/30`}>
          {icon}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold mb-1">{title}</h3>
          <p className="text-gray-400 text-sm mb-2">{description}</p>
          <span className={`badge bg-${color}-900 text-${color}-300`}>{xp}</span>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-600 mt-1" />
      </div>
    </Link>
  )
}

function TipCard({ tip }) {
  const typeColors = {
    grammar: 'blue',
    vocabulary: 'green',
    culture: 'yellow',
    memory_tip: 'purple'
  }
  const color = typeColors[tip.type] || 'gray'

  return (
    <div className="card">
      <div className="flex items-start gap-3">
        <span className={`badge-${color === 'gray' ? 'blue' : color} mt-0.5 shrink-0`}>
          {tip.type?.replace('_', ' ') || 'tip'}
        </span>
        <div>
          <h4 className="font-medium mb-1">{tip.title}</h4>
          <p className="text-gray-400 text-sm leading-relaxed">{tip.content}</p>
        </div>
      </div>
    </div>
  )
}
