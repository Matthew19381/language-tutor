import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { BookOpen, CheckCircle, Clock, Trophy } from 'lucide-react'
import { getUserId } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'
import { useLanguage } from '../hooks/useLanguage'

export default function LessonHistory() {
  const [lessons, setLessons] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const userId = getUserId()
  const { t } = useLanguage()

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
    fetch(`/api/lessons/history/${userId}`)
      .then(r => r.json())
      .then(data => setLessons(data.lessons || []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [userId])

  if (loading) return <PageLoader text={t('history.loading')} />

  return (
    <div className="page-container">
      <div className="flex items-center gap-3 mb-6">
        <BookOpen className="w-7 h-7 text-indigo-400" />
        <h1 className="text-2xl font-bold">{t('history.title')}</h1>
      </div>

      {error && (
        <div className="card border-red-700/30 bg-red-900/10 text-center mb-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {lessons.length === 0 && !error ? (
        <div className="card text-center py-12">
          <BookOpen className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-400">{t('history.noHistory')}</p>
          <Link to="/lesson" className="btn-primary mt-4 inline-block">
            {t('nav.lesson')}
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {lessons.map((lesson) => (
            <Link
              key={lesson.lesson_id}
              to={`/lesson/${lesson.lesson_id}`}
              className="card flex items-center gap-4 hover:border-indigo-600/50 transition-colors cursor-pointer"
            >
              {/* Day badge */}
              <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm shrink-0 ${
                lesson.is_completed ? 'bg-emerald-700 text-emerald-100' : 'bg-gray-700 text-gray-300'
              }`}>
                {lesson.day_number}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-100 truncate">{lesson.title}</p>
                <p className="text-gray-400 text-sm truncate">{lesson.topic}</p>
                {lesson.created_at && (
                  <p className="text-gray-600 text-xs mt-0.5">
                    <Clock className="w-3 h-3 inline mr-1" />
                    {new Date(lesson.created_at).toLocaleDateString()}
                  </p>
                )}
              </div>

              {/* Completion + Score */}
              <div className="flex flex-col items-end gap-1 shrink-0">
                {lesson.is_completed ? (
                  <span className="flex items-center gap-1 text-xs text-emerald-400">
                    <CheckCircle className="w-3 h-3" />
                    {t('lesson.completed')}
                  </span>
                ) : (
                  <span className="text-xs text-gray-500">
                    <BookOpen className="w-3 h-3 inline mr-1" />
                    {t('history.day')} {lesson.day_number}
                  </span>
                )}
                {lesson.best_test_score !== null && lesson.best_test_score !== undefined && (
                  <span className={`flex items-center gap-1 text-xs font-bold ${
                    lesson.best_test_score >= 80 ? 'text-emerald-400' :
                    lesson.best_test_score >= 60 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    <Trophy className="w-3 h-3" />
                    {Math.round(lesson.best_test_score)}%
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
