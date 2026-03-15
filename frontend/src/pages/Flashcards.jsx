import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Brain, ChevronLeft, ChevronRight, Download, Eye,
  CheckCircle, AlertCircle, Clock, Plus
} from 'lucide-react'
import { getUserId, getFlashcards, getDueFlashcards, reviewFlashcard, exportAnki, addFlashcard } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'

const TABS = { ALL: 'all', DUE: 'due', ADD: 'add' }

export default function Flashcards() {
  const [tab, setTab] = useState(TABS.DUE)
  const [allCards, setAllCards] = useState([])
  const [dueCards, setDueCards] = useState([])
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [reviewDone, setReviewDone] = useState(new Set())
  const navigate = useNavigate()
  const userId = getUserId()

  // Add card form
  const [newWord, setNewWord] = useState('')
  const [newTranslation, setNewTranslation] = useState('')
  const [newExample, setNewExample] = useState('')
  const [addMsg, setAddMsg] = useState('')

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

  const displayCards = tab === TABS.DUE ? dueCards : allCards
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
        setAddMsg('Card added successfully!')
        setNewWord('')
        setNewTranslation('')
        setNewExample('')
        loadCards()
      } else {
        setAddMsg(res.message || 'Card already exists')
      }
    } catch (e) {
      setAddMsg('Error: ' + e.message)
    }
  }

  if (loading) return <PageLoader text="Loading flashcards..." />

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Brain className="w-7 h-7 text-purple-400" />
          <div>
            <h1 className="text-2xl font-bold">Flashcards</h1>
            <p className="text-gray-400 text-sm">
              {allCards.length} total · {dueCards.length} due today
            </p>
          </div>
        </div>
        <button
          className="btn-secondary flex items-center gap-2 text-sm"
          onClick={handleExport}
          disabled={exporting || allCards.length === 0}
        >
          <Download className="w-4 h-4" />
          {exporting ? 'Exporting...' : 'Export Anki'}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {[
          { key: TABS.DUE, label: `Due Today (${dueCards.length})`, icon: <Clock className="w-4 h-4" /> },
          { key: TABS.ALL, label: `All Cards (${allCards.length})`, icon: <Eye className="w-4 h-4" /> },
          { key: TABS.ADD, label: 'Add Card', icon: <Plus className="w-4 h-4" /> },
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
      </div>

      {/* Add Card Tab */}
      {tab === TABS.ADD && (
        <div className="card max-w-lg mx-auto">
          <h2 className="text-xl font-semibold mb-4">Add New Flashcard</h2>
          {addMsg && (
            <div className={`p-3 rounded-lg mb-4 text-sm ${
              addMsg.includes('successfully') ? 'bg-emerald-900/30 text-emerald-300' : 'bg-yellow-900/30 text-yellow-300'
            }`}>
              {addMsg}
            </div>
          )}
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Word / Phrase</label>
              <input
                className="input-field"
                placeholder="Word in target language"
                value={newWord}
                onChange={e => setNewWord(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Translation</label>
              <input
                className="input-field"
                placeholder="Translation in your language"
                value={newTranslation}
                onChange={e => setNewTranslation(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Example sentence (optional)</label>
              <input
                className="input-field"
                placeholder="Example sentence"
                value={newExample}
                onChange={e => setNewExample(e.target.value)}
              />
            </div>
            <button
              className="btn-primary w-full"
              onClick={handleAddCard}
              disabled={!newWord || !newTranslation}
            >
              Add Card
            </button>
          </div>
        </div>
      )}

      {/* Flashcard Viewer */}
      {(tab === TABS.ALL || tab === TABS.DUE) && (
        <>
          {displayCards.length === 0 ? (
            <div className="card text-center py-12">
              {tab === TABS.DUE ? (
                <>
                  <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold mb-1">All caught up!</h3>
                  <p className="text-gray-400">No cards due for review today. Check back tomorrow!</p>
                </>
              ) : (
                <>
                  <Brain className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold mb-1">No flashcards yet</h3>
                  <p className="text-gray-400">Complete lessons to automatically add vocabulary cards.</p>
                </>
              )}
            </div>
          ) : (
            <div className="max-w-lg mx-auto">
              {/* Card counter */}
              <div className="flex justify-between text-sm text-gray-400 mb-3">
                <span>{currentIndex + 1} / {displayCards.length}</span>
                {tab === TABS.DUE && (
                  <span>{reviewDone.size} reviewed</span>
                )}
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
                          {isFlipped ? 'translation' : 'word'}
                        </p>
                        <p className="text-3xl font-bold text-indigo-300">{currentCard.word}</p>
                        <p className="text-gray-500 text-xs mt-3">Click to reveal translation</p>
                      </div>
                    </div>
                    {/* Back */}
                    <div className="flashcard-back">
                      <div className="text-center">
                        <p className="text-gray-400 text-xs mb-2 uppercase tracking-wider">translation</p>
                        <p className="text-3xl font-bold text-emerald-300">{currentCard.translation}</p>
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
                    { rating: 1, label: 'Again', color: 'bg-red-700 hover:bg-red-600 text-white', desc: '<1d' },
                    { rating: 2, label: 'Hard', color: 'bg-orange-700 hover:bg-orange-600 text-white', desc: '~3d' },
                    { rating: 3, label: 'Good', color: 'bg-blue-700 hover:bg-blue-600 text-white', desc: '~7d' },
                    { rating: 4, label: 'Easy', color: 'bg-emerald-700 hover:bg-emerald-600 text-white', desc: '~14d' },
                  ].map(({ rating, label, color, desc }) => (
                    <button
                      key={rating}
                      className={`${color} rounded-lg py-2 text-sm font-medium transition-colors`}
                      onClick={() => handleReview(rating)}
                    >
                      <div>{label}</div>
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
                  Previous
                </button>
                <button
                  className={isFlipped ? 'btn-primary' : 'btn-secondary'}
                  onClick={handleFlip}
                >
                  {isFlipped ? 'Show Front' : 'Reveal'}
                </button>
                <button
                  className="btn-secondary flex items-center gap-2"
                  onClick={handleNext}
                  disabled={currentIndex === displayCards.length - 1}
                >
                  Next
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
