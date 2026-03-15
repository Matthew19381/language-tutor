import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BarChart3, Flame, Star, Trophy, BookOpen,
  FlaskConical, Brain, TrendingUp, Target, Calendar
} from 'lucide-react'
import { getUserId, getStats } from '../api/client'
import { NotificationSettings } from '../components/NotificationManager'
import { PageLoader } from '../components/LoadingSpinner'

export default function Stats() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const userId = getUserId()

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
    getStats(userId)
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [userId])

  if (loading) return <PageLoader text="Loading statistics..." />
  if (!stats) return null

  const { user, level_info, lessons, tests, flashcards, error_categories, achievements } = stats

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <BarChart3 className="w-7 h-7 text-blue-400" />
        <div>
          <h1 className="text-2xl font-bold">Statistics</h1>
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
              Level {level_info?.level}/{level_info?.max_level || 50} ·{' '}
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

      {/* Quick stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatBox
          icon={<Flame className="w-6 h-6 text-orange-400" />}
          label="Streak"
          value={`${user?.streak_days || 0} days`}
          color="orange"
        />
        <StatBox
          icon={<Star className="w-6 h-6 text-yellow-400" />}
          label="Total XP"
          value={user?.total_xp || 0}
          color="yellow"
        />
        <StatBox
          icon={<BookOpen className="w-6 h-6 text-blue-400" />}
          label="Lessons"
          value={`${lessons?.completed || 0}/${lessons?.total || 0}`}
          color="blue"
        />
        <StatBox
          icon={<Trophy className="w-6 h-6 text-emerald-400" />}
          label="Avg Score"
          value={`${tests?.average_score || 0}%`}
          color="emerald"
        />
      </div>

      {/* Test Score History Chart */}
      {tests?.history?.length > 0 && (
        <div className="card mb-6">
          <h2 className="section-title flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            Test Score History
          </h2>
          <div className="flex items-end gap-1 h-32">
            {tests.history.map((item, i) => {
              const height = Math.max(4, (item.score / 100) * 100)
              const color = item.score >= 80 ? 'bg-emerald-500' :
                            item.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
              return (
                <div key={i} className="flex flex-col items-center flex-1 gap-1">
                  <span className="text-xs text-gray-500">{Math.round(item.score)}%</span>
                  <div className={`w-full ${color} rounded-t transition-all`} style={{ height: `${height}%` }} />
                  <span className="text-xs text-gray-600 rotate-45 origin-left text-[10px]">
                    {item.date}
                  </span>
                </div>
              )
            })}
          </div>
          <div className="flex gap-4 mt-4 text-xs text-gray-500">
            <span>Best: <span className="text-emerald-400">{tests.best_score}%</span></span>
            <span>Average: <span className="text-yellow-400">{tests.average_score}%</span></span>
            <span>Tests taken: <span className="text-blue-400">{tests.total_taken}</span></span>
          </div>
        </div>
      )}

      {/* Lesson Completion */}
      {lessons?.history?.length > 0 && (
        <div className="card mb-6">
          <h2 className="section-title flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            Recent Lessons
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
                    {lesson.title}
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
                <span className="text-gray-400">Completion rate</span>
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

      {/* Error Categories */}
      {error_categories && Object.keys(error_categories).length > 0 && (
        <div className="card mb-6">
          <h2 className="section-title flex items-center gap-2">
            <Target className="w-5 h-5 text-red-400" />
            Error Analysis
          </h2>
          <p className="text-gray-400 text-sm mb-4">Areas that need more practice:</p>
          <div className="space-y-3">
            {Object.entries(error_categories)
              .sort((a, b) => b[1] - a[1])
              .map(([category, count]) => {
                const total = Object.values(error_categories).reduce((a, b) => a + b, 0)
                const pct = Math.round((count / total) * 100)
                return (
                  <div key={category}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-300 capitalize">{category}</span>
                      <span className="text-gray-500">{count} errors ({pct}%)</span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill bg-red-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                )
              })}
          </div>
        </div>
      )}

      {/* Flashcards summary */}
      <div className="card">
        <h2 className="section-title flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-400" />
          Flashcards
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400">{flashcards?.total || 0}</div>
            <div className="text-xs text-gray-500 mt-1">Total Cards</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-400">{flashcards?.due_today || 0}</div>
            <div className="text-xs text-gray-500 mt-1">Due Today</div>
          </div>
        </div>
      </div>

      {/* Achievements */}
      {achievements && (
        <div className="card mb-6">
          <h2 className="section-title flex items-center gap-2 mb-1">
            <Trophy className="w-5 h-5 text-yellow-400" />
            Achievements
          </h2>
          <p className="text-gray-500 text-xs mb-4">
            {achievements.earned}/{achievements.total} unlocked
          </p>
          <div className="progress-bar mb-4">
            <div
              className="progress-fill bg-yellow-500"
              style={{ width: `${achievements.total ? (achievements.earned / achievements.total) * 100 : 0}%` }}
            />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            {achievements.achievements?.map((ach) => (
              <div
                key={ach.type}
                className={`rounded-lg p-3 text-center transition-all ${
                  ach.earned
                    ? 'bg-yellow-900/20 border border-yellow-700/40'
                    : 'bg-gray-800/50 opacity-40'
                }`}
                title={ach.description}
              >
                <div className="text-2xl mb-1">{ach.icon}</div>
                <p className={`text-xs font-medium ${ach.earned ? 'text-yellow-300' : 'text-gray-500'}`}>
                  {ach.title}
                </p>
                {ach.earned && ach.unlocked_at && (
                  <p className="text-[10px] text-gray-600 mt-0.5">
                    {new Date(ach.unlocked_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notification Settings */}
      <NotificationSettings />

      {/* Member since */}
      <p className="text-center text-gray-600 text-sm mt-6">
        Member since {user?.member_since}
      </p>
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
