import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, ChevronDown, ChevronUp, BookOpen } from 'lucide-react'
import { getUserId, getAllErrors } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'
import PlayButton from '../components/PlayButton'
import { useLanguage } from '../hooks/useLanguage'

const CATEGORY_LABELS = {
  grammar: 'Gramatyka',
  vocabulary: 'Słownictwo',
  word_order: 'Szyk zdania',
  articles: 'Rodzajniki',
  verb_conjugation: 'Koniugacja',
  prepositions: 'Przyimki',
  pronunciation_spelling: 'Wymowa/Pisownia',
  fluency: 'Płynność',
  register: 'Rejestr',
  comprehension: 'Rozumienie',
  application: 'Zastosowanie',
  syntax: 'Składnia',
  unknown: 'Inne',
}

export default function ErrorReview() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState({})
  const navigate = useNavigate()
  const userId = getUserId()
  const { targetLanguage } = useLanguage()

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
    getAllErrors(userId)
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [userId])

  const toggleGroup = (type) => setExpanded(prev => ({ ...prev, [type]: !prev[type] }))

  if (loading) return <PageLoader text="Ładowanie błędów..." />
  if (!data) return null

  return (
    <div className="page-container max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <AlertTriangle className="w-7 h-7 text-yellow-400" />
        <div>
          <h1 className="text-2xl font-bold">Przegląd błędów</h1>
          <p className="text-gray-400">
            {data.total} błędów łącznie · {data.language}
          </p>
        </div>
      </div>

      {data.total === 0 ? (
        <div className="card text-center py-12">
          <BookOpen className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
          <p className="text-emerald-300 font-semibold text-lg">Brak błędów!</p>
          <p className="text-gray-500 text-sm mt-1">Zrób kilka testów, żeby zobaczyć swoje błędy tutaj.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data.groups.map(group => (
            <div key={group.type} className="card">
              <button
                className="w-full flex items-center justify-between"
                onClick={() => toggleGroup(group.type)}
              >
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 rounded-full bg-red-900/50 border border-red-700/40 flex items-center justify-center text-sm font-bold text-red-300">
                    {group.count}
                  </span>
                  <span className="font-semibold text-gray-200">
                    {CATEGORY_LABELS[group.type] || group.type}
                  </span>
                </div>
                {expanded[group.type]
                  ? <ChevronUp className="w-4 h-4 text-gray-500" />
                  : <ChevronDown className="w-4 h-4 text-gray-500" />
                }
              </button>

              {expanded[group.type] && (
                <div className="mt-4 space-y-3">
                  {group.errors.map((err, i) => (
                    <div key={i} className="bg-gray-800/60 rounded-lg p-3 border border-gray-700/40">
                      {/* Error → Correction */}
                      <div className="flex items-center gap-2 flex-wrap mb-2">
                        <div className="flex items-center gap-1">
                          <span className="text-red-400 font-medium line-through text-sm">{err.error}</span>
                          {err.error && <PlayButton text={err.error} language={data.language} />}
                        </div>
                        <span className="text-gray-600">→</span>
                        <div className="flex items-center gap-1">
                          <span className="text-emerald-400 font-medium text-sm">{err.correction}</span>
                          {err.correction && <PlayButton text={err.correction} language={data.language} />}
                        </div>
                        <span className="text-xs text-gray-600 ml-auto">{err.date}</span>
                      </div>

                      {err.explanation && (
                        <p className="text-gray-400 text-xs leading-relaxed">{err.explanation}</p>
                      )}

                      {err.practice && (
                        <div className="flex items-center gap-1 mt-2 pt-2 border-t border-gray-700/40">
                          <p className="text-yellow-300 text-xs italic flex-1">Ćwicz: {err.practice}</p>
                          <PlayButton text={err.practice} language={data.language} />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
