import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Brain, ChevronLeft, ChevronRight, Download, Eye,
  CheckCircle, AlertCircle, Clock, Plus
} from 'lucide-react'
import { getUserId, getFlashcards, getDueFlashcards, reviewFlashcard, exportAnki, addFlashcard, addFlashcardAI } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'
import { useLanguage } from '../hooks/useLanguage'
import PlayButton from '../components/PlayButton'

const TABS = { ALL: 'all', DUE: 'due' }

export default function Flashcards() {
  const [tab, setTab] = useState(TABS.DUE)
  const [allCards, setAllCards] = useState([])
  const [dueCards, setDueCards] = useState([])
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [reviewDone, setReviewDone] = useState(new Set())
  const [dateFilter, setDateFilter] = useState('all') // 'all', 'today', 'week', 'month'
  const [lessonFilter, setLessonFilter] = useState('all') // 'all' or lesson_day number
  const navigate = useNavigate()
  const userId = getUserId()
  const { t, targetLanguage } = useLanguage()

  const [showAddForm, setShowAddForm] = useState(true)

  // Add card form
  const [newWord, setNewWord] = useState('')
  const [newTranslation, setNewTranslation] = useState('')
  const [newExample, setNewExample] = useState('')
  const [addMsg, setAddMsg] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [aiPreview, setAiPreview] = useState(null)
  const [reversed, setReversed] = useState(false) // PL→target instead of target→PL

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
    loadCards()
  }, [userId])

  const loadCards = async () => {
    setLoading(true)
    try {
      const [all, due] = await Promise.all([
        getFlashcards(userId),
        getDueFlashcards(userId)
      ])
      setAllCards(all.flashcards || [])
      setDueCards(due.due_cards || [])
    } catch (e) {}
    finally { setLoading(false) }
  }

  const filterCards = (cards) => {
    if (tab === TABS.DUE) return cards
    const now = new Date()
    return cards.filter(c => {
      // Date filter
      if (dateFilter !== 'all') {
        if (!c.created_at) return true
        const created = new Date(c.created_at)
        if (dateFilter === 'today' && created.toDateString() !== now.toDateString()) return false
        if (dateFilter === 'week' && (now - created) > 7 * 24 * 60 * 60 * 1000) return false
        if (dateFilter === 'month' && (now - created) > 30 * 24 * 60 * 60 * 1000) return false
      }
      // Lesson day filter
      if (lessonFilter !== 'all' && c.lesson_day !== parseInt(lessonFilter)) return false
      return true
    })
  }
  const displayCards = filterCards(tab === TABS.DUE ? dueCards : allCards)
  const currentCard = displayCards[currentIndex]

  const handleFlip = () => setIsFlipped(!isFlipped)

  const handleNext = () => {
    setIsFlipped(false)
    setCurrentIndex(i => Math.min(i + 1, displayCards.length - 1))
  }

  const handlePrev = () => {
    setIsFlipped(false)
    setCurrentIndex(i => Math.max(0, i - 1))
  }

  const handleReview = async (rating) => {
    if (!currentCard) return
    try {
      await reviewFlashcard(currentCard.id, rating)
      setReviewDone(prev => new Set([...prev, currentCard.id]))
      if (currentIndex < displayCards.length - 1) {
        handleNext()
      }
    } catch (e) {}
  }

  // Keyboard navigation: Space/Enter = flip, 1-4 = review rating, ←/→ = prev/next
  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
      if (!currentCard) return
      if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); handleFlip() }
      else if (e.key === 'ArrowRight') handleNext()
      else if (e.key === 'ArrowLeft') handlePrev()
      else if (e.key === '1') handleReview(1)
      else if (e.key === '2') handleReview(2)
      else if (e.key === '3') handleReview(3)
      else if (e.key === '4') handleReview(4)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [currentCard, isFlipped, currentIndex, displayCards.length, tab])

  const handleExport = async () => {
    setExporting(true)
    try {
      const response = await exportAnki(userId)
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'flashcards.apkg')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      alert('Export failed: ' + e.message)
    } finally {
      setExporting(false)
    }
  }

  const handleAddCard = async () => {
    if (!newWord || !newTranslation) return
    try {
      const res = await addFlashcard(userId, {
        word: newWord,
        translation: newTranslation,
        example_sentence: newExample
      })
      if (res.success) {
        setAddMsg(t('flash.cardAdded') || 'Card added successfully!')
        setNewWord('')
        setNewTranslation('')
        setNewExample('')
        loadCards()
      } else {
        setAddMsg(res.message || t('flash.cardExists'))
      }
    } catch (e) {
      setAddMsg('Error: ' + e.message)
    }
  }

  if (loading) return <PageLoader text={t('flash.loading')} />

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Brain className="w-7 h-7 text-purple-400" />
          <div>
            <h1 className="text-2xl font-bold">{t('flash.title')}</h1>
            <p className="text-gray-400 text-sm">
              {allCards.length} {t('flash.total')} · {dueCards.length} {t('flash.dueToday')}
            </p>
          </div>
        </div>
        <button
          className="btn-secondary flex items-center gap-2 text-sm"
          onClick={handleExport}
          disabled={exporting || allCards.length === 0}
        >
          <Download className="w-4 h-4" />
          {exporting ? t('flash.exporting') : t('flash.exportAnki')}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 mb-4">
        {[
          { key: TABS.DUE, label: `${t('flash.dueTab')} (${dueCards.length})`, icon: <Clock className="w-4 h-4" /> },
          { key: TABS.ALL, label: `${t('flash.allTab')} (${allCards.length})`, icon: <Eye className="w-4 h-4" /> },
        ].map(({ key, label, icon }) => (
          <button
            key={key}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === key
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-gray-100'
            }`}
            onClick={() => { setTab(key); setCurrentIndex(0); setIsFlipped(false) }}
          >
            {icon}{label}
          </button>
        ))}
        <button
          onClick={() => setShowAddForm(s => !s)}
          className={`ml-auto flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${showAddForm ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-100'}`}
        >
          <Plus className="w-4 h-4" />{t('flash.addTab')}
        </button>
      </div>

      {/* Add Card Panel */}
      {showAddForm && (
        <div className="card mb-6 max-w-lg">
          <h2 className="text-xl font-semibold mb-2">{t('flash.addNew')}</h2>
          <p className="text-gray-500 text-sm mb-4">Wpisz słowo — AI automatycznie doda tłumaczenie i przykład.</p>
          {addMsg && (
            <div className={`p-3 rounded-lg mb-4 text-sm ${
              addMsg.includes('successfully') || addMsg.includes('dodana') || addMsg.includes('AI')
                ? 'bg-emerald-900/30 text-emerald-300'
                : 'bg-yellow-900/30 text-yellow-300'
            }`}>
              {addMsg}
            </div>
          )}
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-400 mb-1">{t('flash.wordPhrase')}</label>
              <input
                className="input-field"
                placeholder={t('flash.wordPlaceholder')}
                value={newWord}
                onChange={e => { setNewWord(e.target.value); setAiPreview(null) }}
              />
            </div>

            {aiPreview && (
              <div className="bg-gray-800 rounded-lg p-3 border border-indigo-700/40">
                <p className="text-xs text-gray-500 mb-2">Podgląd fiszki (wygenerowane przez AI):</p>
                <div className="space-y-1 text-sm">
                  <p><span className="text-gray-500">Słowo:</span> <span className="text-indigo-300 font-medium">{newWord}</span></p>
                  <p><span className="text-gray-500">Tłumaczenie:</span> <span className="text-emerald-300">{aiPreview.translation || '(brak)'}</span></p>
                  <p><span className="text-gray-500">Przykład:</span> <span className="text-gray-300 italic">{aiPreview.example || '(brak)'}</span></p>
                </div>
              </div>
            )}

            {!aiPreview ? (
              <button
                className="btn-primary w-full flex items-center justify-center gap-2"
                onClick={async () => {
                  if (!newWord.trim()) return
                  setAiLoading(true)
                  setAddMsg('')
                  try {
                    const res = await addFlashcardAI(userId, newWord.trim())
                    if (res.success) {
                      setAiPreview({ translation: res.translation, example: res.example })
                      setAddMsg('AI wygenerowało fiszkę. Sprawdź podgląd poniżej.')
                    } else {
                      setAddMsg(res.message || t('flash.cardExists'))
                      setNewWord('')
                    }
                  } catch (e) {
                    setAddMsg('Błąd: ' + e.message)
                  } finally {
                    setAiLoading(false)
                  }
                }}
                disabled={!newWord.trim() || aiLoading}
              >
                {aiLoading ? <><Plus className="w-4 h-4 animate-spin" /> Generowanie AI...</> : <><Plus className="w-4 h-4" /> Dodaj z AI</>}
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  className="btn-primary flex-1"
                  onClick={() => {
                    setAddMsg('Fiszka dodana! ✓')
                    setNewWord('')
                    setAiPreview(null)
                    loadCards()
                  }}
                >
                  Zapisz fiszkę
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => { setAiPreview(null); setAddMsg('') }}
                >
                  Anuluj
                </button>
              </div>
            )}

            <div className="border-t border-gray-700 pt-3">
              <p className="text-xs text-gray-600 mb-2">Lub dodaj ręcznie:</p>
              <div className="space-y-2">
                <input
                  className="input-field text-sm"
                  placeholder={t('flash.translationPlaceholder')}
                  value={newTranslation}
                  onChange={e => setNewTranslation(e.target.value)}
                />
                <input
                  className="input-field text-sm"
                  placeholder={t('flash.examplePlaceholder')}
                  value={newExample}
                  onChange={e => setNewExample(e.target.value)}
                />
                <button
                  className="btn-secondary w-full text-sm"
                  onClick={handleAddCard}
                  disabled={!newWord || !newTranslation}
                >
                  {t('flash.addButton')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Flashcard Viewer */}
      {(tab === TABS.ALL || tab === TABS.DUE) && (
        <>
          {tab === TABS.ALL && (
            <div className="mb-4 space-y-2">
              <div className="flex gap-2 flex-wrap">
                <span className="text-gray-500 text-sm self-center">Data:</span>
                {[
                  { key: 'all', label: 'Wszystkie' },
                  { key: 'today', label: 'Dzisiaj' },
                  { key: 'week', label: 'Ten tydzień' },
                  { key: 'month', label: 'Ten miesiąc' },
                ].map(({ key, label }) => (
                  <button
                    key={key}
                    onClick={() => { setDateFilter(key); setCurrentIndex(0) }}
                    className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                      dateFilter === key ? 'bg-purple-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
              {/* Lesson day filter */}
              {(() => {
                const days = [...new Set(allCards.filter(c => c.lesson_day).map(c => c.lesson_day))].sort((a, b) => a - b)
                if (days.length === 0) return null
                return (
                  <div className="flex gap-2 flex-wrap">
                    <span className="text-gray-500 text-sm self-center">Lekcja:</span>
                    <button
                      onClick={() => { setLessonFilter('all'); setCurrentIndex(0) }}
                      className={`px-3 py-1 rounded text-xs font-medium transition-colors ${lessonFilter === 'all' ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'}`}
                    >Wszystkie</button>
                    {days.map(day => (
                      <button
                        key={day}
                        onClick={() => { setLessonFilter(String(day)); setCurrentIndex(0) }}
                        className={`px-3 py-1 rounded text-xs font-medium transition-colors ${lessonFilter === String(day) ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'}`}
                      >
                        Dzień {day}
                      </button>
                    ))}
                  </div>
                )
              })()}
            </div>
          )}
          {displayCards.length === 0 ? (
            <div className="card text-center py-12">
              {tab === TABS.DUE ? (
                <>
                  <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold mb-1">{t('flash.allCaughtUp')}</h3>
                  <p className="text-gray-400">{t('flash.noDueCards')}</p>
                </>
              ) : (
                <>
                  <Brain className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold mb-1">{t('flash.noCards')}</h3>
                  <p className="text-gray-400">{t('flash.completeLesson')}</p>
                </>
              )}
            </div>
          ) : (
            <div className="max-w-lg mx-auto">
              {/* Card counter */}
              <div className="flex justify-between text-sm text-gray-400 mb-3">
                <span>{currentIndex + 1} / {displayCards.length}</span>
                <div className="flex items-center gap-3">
                  {tab === TABS.DUE && (
                    <span>{reviewDone.size} {t('flash.reviewed')}</span>
                  )}
                  <button
                    onClick={() => { setReversed(r => !r); setIsFlipped(false) }}
                    className={`text-xs px-2 py-0.5 rounded transition-colors ${reversed ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'}`}
                    title="Odwróć kierunek fiszek"
                  >
                    {reversed ? 'PL → cel' : 'cel → PL'}
                  </button>
                </div>
              </div>

              {/* Flashcard */}
              {currentCard && (
                <div className="flashcard-container mb-6">
                  <div
                    className={`flashcard ${isFlipped ? 'flipped' : ''}`}
                    onClick={handleFlip}
                  >
                    {/* Front */}
                    <div className="flashcard-front">
                      <div className="text-center">
                        <p className="text-gray-400 text-xs mb-2 uppercase tracking-wider">
                          {reversed ? 'Polski' : t('flash.wordSide')}
                        </p>
                        {reversed ? (
                          <p className="text-3xl font-bold text-emerald-300">{currentCard.translation}</p>
                        ) : (
                          <div className="flex items-center justify-center gap-2">
                            <p className="text-3xl font-bold text-indigo-300">{currentCard.word}</p>
                            <div onClick={e => e.stopPropagation()}>
                              <PlayButton text={currentCard.word} language={currentCard.language || targetLanguage} />
                            </div>
                          </div>
                        )}
                        <p className="text-gray-500 text-xs mt-3">{t('flash.clickReveal')}</p>
                      </div>
                    </div>
                    {/* Back */}
                    <div className="flashcard-back">
                      <div className="text-center">
                        <p className="text-gray-400 text-xs mb-2 uppercase tracking-wider">
                          {reversed ? t('flash.wordSide') : t('flash.translationSide')}
                        </p>
                        {reversed ? (
                          <div className="flex items-center justify-center gap-2 mb-1">
                            <p className="text-3xl font-bold text-indigo-300">{currentCard.word}</p>
                            <div onClick={e => e.stopPropagation()}>
                              <PlayButton text={currentCard.word} language={currentCard.language || targetLanguage} />
                            </div>
                          </div>
                        ) : (
                          <>
                            <div className="flex items-center justify-center gap-2 mb-1">
                              <p className="text-3xl font-bold text-indigo-300">{currentCard.word}</p>
                              <div onClick={e => e.stopPropagation()}>
                                <PlayButton text={currentCard.word} language={currentCard.language || targetLanguage} />
                              </div>
                            </div>
                            <p className="text-2xl font-bold text-emerald-300">{currentCard.translation}</p>
                          </>
                        )}
                        {currentCard.example_sentence && (
                          <p className="text-gray-400 text-sm mt-3 italic max-w-xs">
                            {currentCard.example_sentence}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Review buttons (only for due tab) */}
              {tab === TABS.DUE && isFlipped && currentCard && (
                <div className="grid grid-cols-4 gap-2 mb-4">
                  {[
                    { rating: 1, labelKey: 'flash.again', color: 'bg-red-700 hover:bg-red-600 text-white', desc: '<1d' },
                    { rating: 2, labelKey: 'flash.hard', color: 'bg-orange-700 hover:bg-orange-600 text-white', desc: '~3d' },
                    { rating: 3, labelKey: 'flash.good', color: 'bg-blue-700 hover:bg-blue-600 text-white', desc: '~7d' },
                    { rating: 4, labelKey: 'flash.easy', color: 'bg-emerald-700 hover:bg-emerald-600 text-white', desc: '~14d' },
                  ].map(({ rating, labelKey, color, desc }) => (
                    <button
                      key={rating}
                      className={`${color} rounded-lg py-2 text-sm font-medium transition-colors`}
                      onClick={() => handleReview(rating)}
                    >
                      <div>{t(labelKey)}</div>
                      <div className="text-xs opacity-75">{desc}</div>
                    </button>
                  ))}
                </div>
              )}

              {/* Navigation */}
              <div className="flex justify-between">
                <button
                  className="btn-secondary flex items-center gap-2"
                  onClick={handlePrev}
                  disabled={currentIndex === 0}
                >
                  <ChevronLeft className="w-4 h-4" />
                  {t('flash.previous')}
                </button>
                <button
                  className={isFlipped ? 'btn-primary' : 'btn-secondary'}
                  onClick={handleFlip}
                >
                  {isFlipped ? t('flash.showFront') : t('flash.reveal')}
                </button>
                <button
                  className="btn-secondary flex items-center gap-2"
                  onClick={handleNext}
                  disabled={currentIndex === displayCards.length - 1}
                >
                  {t('flash.next')}
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              {/* Progress dots */}
              <div className="flex gap-1.5 mt-4 justify-center flex-wrap">
                {displayCards.map((card, i) => (
                  <button
                    key={i}
                    className={`w-2 h-2 rounded-full transition-all ${
                      i === currentIndex
                        ? 'bg-indigo-400 w-4'
                        : reviewDone.has(card.id)
                        ? 'bg-emerald-600'
                        : 'bg-gray-700'
                    }`}
                    onClick={() => { setCurrentIndex(i); setIsFlipped(false) }}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
