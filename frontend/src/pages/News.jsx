import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Newspaper, BookOpen, ChevronDown, ChevronUp, ExternalLink, Plus } from 'lucide-react'
import { getUserId, addFlashcard } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'
import { useLanguage } from '../hooks/useLanguage'
import axios from 'axios'

export default function News() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState({})
  const [addedWords, setAddedWords] = useState({})
  const navigate = useNavigate()
  const userId = getUserId()
  const { t } = useLanguage()

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
    axios.get(`/api/news/${userId}`)
      .then(r => setArticles(r.data.articles || []))
      .catch(e => setError(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [userId])

  const toggleArticle = (i) => setExpanded(prev => ({ ...prev, [i]: !prev[i] }))

  const handleAddFlashcard = async (word, translation, articleTitle) => {
    const key = `${word}-${translation}`
    if (addedWords[key]) return
    try {
      await addFlashcard(userId, {
        word,
        translation,
        example_sentence: `From article: ${articleTitle}`,
      })
      setAddedWords(prev => ({ ...prev, [key]: true }))
    } catch (e) {
      console.error('Failed to add flashcard:', e)
    }
  }

  if (loading) return <PageLoader text={t('news.loading')} />

  if (error) {
    return (
      <div className="page-container">
        <div className="card border-red-700/30 bg-red-900/10 text-center">
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <div className="flex items-center gap-3 mb-6">
        <Newspaper className="w-7 h-7 text-blue-400" />
        <div>
          <h1 className="text-2xl font-bold">{t('news.title')}</h1>
          <p className="text-gray-400">{t('news.subtitle')}</p>
        </div>
      </div>

      {articles.length === 0 && (
        <div className="card text-center text-gray-400">
          {t('news.noArticles')}
        </div>
      )}

      <div className="space-y-4">
        {articles.map((article, i) => (
          <div key={i} className="card">
            {/* Article Header */}
            <button
              onClick={() => toggleArticle(i)}
              className="w-full flex items-start justify-between gap-3 text-left"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="badge-blue text-xs">{article.source || 'News'}</span>
                </div>
                <h2 className="font-semibold text-lg text-indigo-200">{article.title}</h2>
                {article.original_title && article.original_title !== article.title && (
                  <p className="text-gray-500 text-xs mt-0.5 italic">{article.original_title}</p>
                )}
              </div>
              {expanded[i]
                ? <ChevronUp className="w-5 h-5 text-gray-500 shrink-0 mt-1" />
                : <ChevronDown className="w-5 h-5 text-gray-500 shrink-0 mt-1" />
              }
            </button>

            {expanded[i] && (
              <div className="mt-4 pt-4 border-t border-gray-800 space-y-4">
                {/* Simplified Text */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 mb-2 flex items-center gap-1">
                    <BookOpen className="w-4 h-4" /> {t('news.simplified')}
                  </h3>
                  <p className="text-gray-200 leading-relaxed">{article.simplified_text}</p>
                </div>

                {/* Vocabulary */}
                {article.vocabulary?.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-400 mb-2">{t('news.vocabulary')}</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {article.vocabulary.map((v, j) => {
                        const key = `${v.word}-${v.translation}`
                        return (
                          <div key={j} className="bg-gray-800 rounded-lg px-3 py-2 flex items-center justify-between gap-2">
                            <div>
                              <span className="text-indigo-300 font-medium">{v.word}</span>
                              <span className="text-gray-500 mx-2">→</span>
                              <span className="text-emerald-300">{v.translation}</span>
                              {v.cefr_level && (
                                <span className="ml-2 text-xs text-gray-600">{v.cefr_level}</span>
                              )}
                            </div>
                            <button
                              onClick={() => handleAddFlashcard(v.word, v.translation, article.title)}
                              className={`shrink-0 ${addedWords[key] ? 'text-emerald-500' : 'text-gray-600 hover:text-indigo-400'}`}
                              title={addedWords[key] ? t('news.addedToFlash') : t('news.addToFlash')}
                            >
                              {addedWords[key] ? '✓' : <Plus className="w-4 h-4" />}
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}

                {/* Comprehension Questions */}
                {article.comprehension_questions?.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-400 mb-2">{t('news.comprehension')}</h3>
                    <div className="space-y-3">
                      {article.comprehension_questions.map((q, j) => (
                        <ComprehensionQuestion key={j} question={q.question} answer={q.answer} t={t} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Source Link */}
                {article.link && (
                  <a
                    href={article.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-indigo-400 hover:text-indigo-300 text-sm"
                  >
                    <ExternalLink className="w-3 h-3" /> {t('news.readOriginal')}
                  </a>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function ComprehensionQuestion({ question, answer, t }) {
  const [showAnswer, setShowAnswer] = useState(false)
  return (
    <div className="bg-gray-800 rounded-lg p-3">
      <p className="text-gray-200 text-sm mb-2">{question}</p>
      <button
        onClick={() => setShowAnswer(s => !s)}
        className="text-indigo-400 hover:text-indigo-300 text-xs"
      >
        {showAnswer ? t('news.hideAnswer') : t('news.showAnswer')}
      </button>
      {showAnswer && (
        <p className="mt-2 text-emerald-300 text-sm">{answer}</p>
      )}
    </div>
  )
}
