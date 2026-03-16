import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BookOpen, CheckCircle, ChevronDown, ChevronUp,
  AlertTriangle, MessageSquare, PenTool, Star, Download,
  RefreshCw, Eye, EyeOff, FileText
} from 'lucide-react'
import axios from 'axios'
import { getUserId, getTodayLesson, completeLesson } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'
import { useLanguage } from '../hooks/useLanguage'

const OBSIDIAN_OFFSETS = [
  { offset: -1, key: 'lesson.yesterday' },
  { offset: 0, key: 'lesson.today' },
  { offset: 1, key: 'lesson.tomorrow' },
  { offset: 2, key: 'lesson.dayAfterTomorrow' },
]

export default function DailyLesson() {
  const [lesson, setLesson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [completing, setCompleting] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [expandedSections, setExpandedSections] = useState({
    explanation: true,
    vocabulary: true,
    dialogue: false,
    exercises: false,
    production: false,
    errorReview: false,
    comprehensibleInput: false,
    interleaved: false,
    outputForcing: false,
  })
  const [pdfLoading, setPdfLoading] = useState(false)
  const [obsidianLoading, setObsidianLoading] = useState(false)
  const [obsidianOffset, setObsidianOffset] = useState(0)
  const [obsidianUpload, setObsidianUpload] = useState(false)
  const [showObsidianMenu, setShowObsidianMenu] = useState(false)
  const navigate = useNavigate()
  const userId = getUserId()
  const { t } = useLanguage()

  useEffect(() => {
    if (!userId) {
      navigate('/placement')
      return
    }
    setLoading(true)
    getTodayLesson(userId)
      .then(data => {
        setLesson(data)
        setCompleted(data.is_completed)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [userId])

  const toggleSection = (key) => {
    setExpandedSections(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const handleComplete = async () => {
    if (!lesson) return
    setCompleting(true)
    try {
      await completeLesson(lesson.lesson_id, userId)
      setCompleted(true)
    } catch (e) {
      setError(e.message)
    } finally {
      setCompleting(false)
    }
  }

  const handleDownloadPDF = async () => {
    if (!lesson) return
    setPdfLoading(true)
    try {
      const response = await axios.get(`/api/lessons/${lesson.lesson_id}/export-pdf`, {
        responseType: 'blob',
      })
      const url = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = url
      link.download = `lesson_${lesson.lesson_id}.pdf`
      link.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      console.error('PDF download failed:', e)
    } finally {
      setPdfLoading(false)
    }
  }

  const handleExportObsidian = async () => {
    if (!lesson) return
    setObsidianLoading(true)
    setShowObsidianMenu(false)
    try {
      const response = await axios.get(
        `/api/lessons/${lesson.lesson_id}/export-obsidian`,
        {
          params: { day_offset: obsidianOffset, upload: obsidianUpload },
          responseType: obsidianUpload ? 'json' : 'blob',
        }
      )
      if (obsidianUpload) {
        const data = response.data
        alert(`Uploaded to Google Drive: ${data.url || 'success'}`)
      } else {
        const url = URL.createObjectURL(new Blob([response.data], { type: 'text/markdown' }))
        const link = document.createElement('a')
        link.href = url
        link.download = `lesson_${lesson.lesson_id}.md`
        link.click()
        URL.revokeObjectURL(url)
      }
    } catch (e) {
      console.error('Obsidian export failed:', e)
    } finally {
      setObsidianLoading(false)
    }
  }

  if (loading) return <PageLoader text={t('lesson.loading')} />

  if (error) {
    return (
      <div className="page-container">
        <div className="card border-red-700/30 bg-red-900/10 text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h2 className="text-xl font-semibold mb-2">{t('lesson.errorTitle')}</h2>
          <p className="text-gray-400 mb-4">{error}</p>
          {error.includes('study plan') && (
            <button onClick={() => navigate('/placement')} className="btn-primary">
              {t('lesson.takePlacement')}
            </button>
          )}
        </div>
      </div>
    )
  }

  if (!lesson) return null

  const content = lesson.content || {}

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge-blue">{t('lesson.day')} {lesson.day_number}</span>
            {completed && <span className="badge-green flex items-center gap-1">
              <CheckCircle className="w-3 h-3" /> {t('lesson.completed')}
            </span>}
          </div>
          <h1 className="text-2xl font-bold">{lesson.title}</h1>
          <p className="text-gray-400 mt-1">{lesson.topic}</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadPDF}
            disabled={pdfLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors disabled:opacity-50"
            title="Download PDF"
          >
            <Download className="w-4 h-4" />
            {pdfLoading ? t('lesson.generating') : t('lesson.pdf')}
          </button>

          {/* Obsidian Export Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowObsidianMenu(m => !m)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors"
              title={t('lesson.exportObsidian')}
            >
              <FileText className="w-4 h-4" />
              <span className="hidden sm:block">MD</span>
              <ChevronDown className="w-3 h-3" />
            </button>

            {showObsidianMenu && (
              <div className="absolute right-0 top-full mt-1 z-50 bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-3 min-w-[220px]">
                <p className="text-xs text-gray-400 mb-2 font-medium">{t('lesson.exportObsidian')}</p>

                {/* Day offset selector */}
                <div className="flex flex-wrap gap-1 mb-3">
                  {OBSIDIAN_OFFSETS.map(({ offset, key }) => (
                    <button
                      key={offset}
                      onClick={() => setObsidianOffset(offset)}
                      className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                        obsidianOffset === offset
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {t(key)}
                    </button>
                  ))}
                </div>

                {/* Upload toggle */}
                <div className="flex gap-1 mb-3">
                  <button
                    onClick={() => setObsidianUpload(false)}
                    className={`flex-1 px-2 py-1 rounded text-xs font-medium transition-colors ${
                      !obsidianUpload ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {t('lesson.downloadLocal')}
                  </button>
                  <button
                    onClick={() => setObsidianUpload(true)}
                    className={`flex-1 px-2 py-1 rounded text-xs font-medium transition-colors ${
                      obsidianUpload ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {t('lesson.sendToDrive')}
                  </button>
                </div>

                <button
                  onClick={handleExportObsidian}
                  disabled={obsidianLoading}
                  className="w-full px-3 py-1.5 rounded bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-medium transition-colors disabled:opacity-50"
                >
                  {obsidianLoading ? '...' : t('lesson.exportObsidian')}
                </button>
              </div>
            )}
          </div>

          <BookOpen className="w-8 h-8 text-indigo-400" />
        </div>
      </div>

      {/* Explanation */}
      <Section
        title={t('lesson.grammar')}
        icon={<BookOpen className="w-5 h-5" />}
        expanded={expandedSections.explanation}
        onToggle={() => toggleSection('explanation')}
      >
        <div className="prose prose-invert max-w-none">
          <p className="text-gray-300 leading-relaxed whitespace-pre-line">{content.explanation}</p>
        </div>
      </Section>

      {/* Vocabulary */}
      {content.vocabulary?.length > 0 && (
        <Section
          title={`${t('lesson.vocabulary')} (${content.vocabulary.length} ${t('lesson.words')})`}
          icon={<Star className="w-5 h-5" />}
          expanded={expandedSections.vocabulary}
          onToggle={() => toggleSection('vocabulary')}
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left border-b border-gray-700">
                  <th className="pb-2 text-gray-400 font-medium text-sm">{t('lesson.word')}</th>
                  <th className="pb-2 text-gray-400 font-medium text-sm">{t('lesson.translation')}</th>
                  <th className="pb-2 text-gray-400 font-medium text-sm hidden md:table-cell">{t('lesson.example')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {content.vocabulary.map((item, i) => (
                  <tr key={i} className="hover:bg-gray-800/50">
                    <td className="py-2.5 pr-4">
                      <span className="font-medium text-indigo-300">{item.word}</span>
                    </td>
                    <td className="py-2.5 pr-4">
                      <span className="text-emerald-300">{item.translation}</span>
                    </td>
                    <td className="py-2.5 text-gray-400 text-sm hidden md:table-cell">
                      {item.example}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {/* Dialogue */}
      {content.dialogue && (
        <Section
          title={t('lesson.dialogue')}
          icon={<MessageSquare className="w-5 h-5" />}
          expanded={expandedSections.dialogue}
          onToggle={() => toggleSection('dialogue')}
        >
          {content.dialogue.context && (
            <p className="text-gray-400 text-sm italic mb-4 bg-gray-800 rounded-lg p-3">
              {content.dialogue.context}
            </p>
          )}
          <div className="space-y-3">
            {(content.dialogue.lines || []).map((line, i) => (
              <div
                key={i}
                className={`flex gap-3 ${line.speaker === 'B' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm shrink-0 ${
                  line.speaker === 'A' ? 'bg-indigo-700' : 'bg-purple-700'
                }`}>
                  {line.speaker}
                </div>
                <div className={`max-w-sm rounded-2xl px-4 py-2.5 ${
                  line.speaker === 'A'
                    ? 'bg-gray-800 rounded-tl-sm'
                    : 'bg-gray-700 rounded-tr-sm'
                }`}>
                  <p className="font-medium">{line.text}</p>
                  {line.translation && (
                    <p className="text-gray-400 text-sm mt-0.5 italic">{line.translation}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Exercises */}
      {content.exercises?.length > 0 && (
        <Section
          title={`${t('lesson.exercises')} (${content.exercises.length})`}
          icon={<PenTool className="w-5 h-5" />}
          expanded={expandedSections.exercises}
          onToggle={() => toggleSection('exercises')}
        >
          <div className="space-y-4">
            {content.exercises.map((ex, i) => (
              <ExerciseCard key={i} exercise={ex} number={i + 1} t={t} />
            ))}
          </div>
        </Section>
      )}

      {/* Production Task */}
      {content.production_task && (
        <Section
          title={t('lesson.productionTask')}
          icon={<PenTool className="w-5 h-5" />}
          expanded={expandedSections.production}
          onToggle={() => toggleSection('production')}
        >
          <div className="bg-indigo-900/20 border border-indigo-700/30 rounded-lg p-4">
            <p className="font-medium text-indigo-300 mb-2">{content.production_task.instruction}</p>
            {content.production_task.example && (
              <p className="text-gray-400 text-sm italic">
                {t('lesson.exampleLabel')} {content.production_task.example}
              </p>
            )}
          </div>
          <textarea
            className="input-field mt-3 h-24 resize-none"
            placeholder={t('lesson.writeResponse')}
          />
        </Section>
      )}

      {/* Error Review */}
      {content.error_review?.length > 0 && (
        <Section
          title={`${t('lesson.errorReview')} (${content.error_review.length})`}
          icon={<AlertTriangle className="w-5 h-5 text-yellow-400" />}
          expanded={expandedSections.errorReview}
          onToggle={() => toggleSection('errorReview')}
        >
          <div className="space-y-3">
            {content.error_review.map((err, i) => (
              <div key={i} className="bg-yellow-900/10 border border-yellow-700/30 rounded-lg p-4">
                <div className="flex items-start gap-2 mb-2">
                  <span className="text-red-400 font-medium line-through">{err.error}</span>
                  <span className="text-gray-500">→</span>
                  <span className="text-emerald-400 font-medium">{err.correction}</span>
                </div>
                <p className="text-gray-400 text-sm">{err.explanation}</p>
                {err.practice && (
                  <p className="text-yellow-300 text-sm mt-2 italic">{t('lesson.practiceLabel')} {err.practice}</p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Comprehensible Input (i+1) */}
      {content.comprehensible_input?.text && (
        <Section
          title={t('lesson.readingPractice')}
          icon={<BookOpen className="w-5 h-5 text-teal-400" />}
          expanded={expandedSections.comprehensibleInput}
          onToggle={() => toggleSection('comprehensibleInput')}
        >
          <div className="bg-teal-900/10 border border-teal-700/30 rounded-lg p-4 mb-3">
            <p className="text-gray-200 leading-relaxed">
              {content.comprehensible_input.text.split(/(\b\S+\b)/).map((part, i) => {
                const newWords = content.comprehensible_input.new_words || []
                const isNew = newWords.some(w => part.toLowerCase().includes(w.toLowerCase()) && w.length > 2)
                return isNew
                  ? <mark key={i} className="bg-yellow-500/30 text-yellow-200 rounded px-0.5">{part}</mark>
                  : <span key={i}>{part}</span>
              })}
            </p>
          </div>
          {content.comprehensible_input.new_words?.length > 0 && (
            <div className="mb-3">
              <p className="text-sm text-gray-400 mb-1">{t('lesson.newWords')}</p>
              <div className="flex flex-wrap gap-2">
                {content.comprehensible_input.new_words.map((w, i) => (
                  <span key={i} className="bg-yellow-500/20 text-yellow-300 px-2 py-0.5 rounded text-sm">{w}</span>
                ))}
              </div>
            </div>
          )}
          {content.comprehensible_input.comprehension_questions?.length > 0 && (
            <div>
              <p className="text-sm text-gray-400 mb-2">{t('lesson.comprehensionCheck')}</p>
              <div className="space-y-2">
                {content.comprehensible_input.comprehension_questions.map((q, i) => (
                  <ComprehensionQ key={i} question={q.question} answer={q.answer} t={t} />
                ))}
              </div>
            </div>
          )}
        </Section>
      )}

      {/* Interleaved Review */}
      {content.interleaved_review?.length > 0 && (
        <Section
          title={`${t('lesson.mixedReview')} (${content.interleaved_review.length} ${t('lesson.questions')})`}
          icon={<RefreshCw className="w-5 h-5 text-orange-400" />}
          expanded={expandedSections.interleaved}
          onToggle={() => toggleSection('interleaved')}
        >
          <p className="text-gray-400 text-sm mb-3">{t('lesson.reviewPrevious')}</p>
          <div className="space-y-3">
            {content.interleaved_review.map((item, i) => (
              <div key={i} className="bg-orange-900/10 border border-orange-700/30 rounded-lg p-3">
                <p className="text-xs text-orange-400 mb-1">{t('lesson.topic')} {item.topic}</p>
                <ComprehensionQ question={item.question} answer={item.answer} t={t} />
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Output Forcing */}
      {content.output_forcing?.text && (
        <Section
          title={t('lesson.outputForcing')}
          icon={<PenTool className="w-5 h-5 text-pink-400" />}
          expanded={expandedSections.outputForcing}
          onToggle={() => toggleSection('outputForcing')}
        >
          <OutputForcingCard
            instruction={content.output_forcing.instruction}
            text={content.output_forcing.text}
            t={t}
          />
        </Section>
      )}

      {/* Complete Button */}
      {!completed ? (
        <button
          className="btn-success w-full py-3 mt-4 flex items-center justify-center gap-2 text-lg"
          onClick={handleComplete}
          disabled={completing}
        >
          {completing ? (
            <>{t('lesson.marking')}</>
          ) : (
            <>
              <CheckCircle className="w-5 h-5" />
              {t('lesson.markComplete')}
            </>
          )}
        </button>
      ) : (
        <div className="card border-emerald-700/30 bg-emerald-900/10 text-center mt-4">
          <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <p className="text-emerald-300 font-semibold">{t('lesson.lessonCompleted')}</p>
          <p className="text-gray-400 text-sm mt-1">{t('lesson.earnedXP')}</p>
          <button
            className="btn-primary mt-3"
            onClick={() => navigate('/test')}
          >
            {t('lesson.takeDailyTest')}
          </button>
        </div>
      )}
    </div>
  )
}

function Section({ title, icon, expanded, onToggle, children }) {
  return (
    <div className="card mb-4">
      <button
        className="flex items-center justify-between w-full text-left"
        onClick={onToggle}
      >
        <div className="flex items-center gap-2 text-indigo-300">
          {icon}
          <h2 className="font-semibold">{title}</h2>
        </div>
        {expanded ? (
          <ChevronUp className="w-5 h-5 text-gray-500" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-500" />
        )}
      </button>
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-800">
          {children}
        </div>
      )}
    </div>
  )
}

function ComprehensionQ({ question, answer, t }) {
  const [show, setShow] = useState(false)
  return (
    <div className="bg-gray-800 rounded p-3">
      <p className="text-gray-200 text-sm">{question}</p>
      <button
        onClick={() => setShow(s => !s)}
        className="text-indigo-400 hover:text-indigo-300 text-xs mt-1"
      >
        {show ? t('lesson.hideAnswer') : t('lesson.showAnswer')}
      </button>
      {show && <p className="text-emerald-300 text-sm mt-1">{answer}</p>}
    </div>
  )
}

function OutputForcingCard({ instruction, text, t }) {
  const [phase, setPhase] = useState(1)
  const [userRecall, setUserRecall] = useState('')

  const similarity = () => {
    if (!userRecall || !text) return 0
    const a = userRecall.toLowerCase().split(/\s+/)
    const b = text.toLowerCase().split(/\s+/)
    const matches = a.filter(w => b.includes(w)).length
    return Math.round((matches / b.length) * 100)
  }

  const score = phase === 2 && userRecall ? similarity() : null

  return (
    <div>
      <p className="text-gray-400 text-sm mb-3">{instruction}</p>
      {phase === 1 ? (
        <div>
          <div className="bg-pink-900/10 border border-pink-700/30 rounded-lg p-4 mb-3">
            <p className="text-gray-100 leading-relaxed">{text}</p>
          </div>
          <button
            onClick={() => setPhase(2)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-pink-700 hover:bg-pink-600 text-white text-sm transition-colors"
          >
            <EyeOff className="w-4 h-4" /> {t('lesson.hideTest')}
          </button>
        </div>
      ) : (
        <div>
          <p className="text-gray-400 text-sm mb-2">{t('lesson.recallText')}</p>
          <textarea
            className="input-field h-24 resize-none mb-3"
            placeholder={t('lesson.writeRemember')}
            value={userRecall}
            onChange={e => setUserRecall(e.target.value)}
          />
          <div className="flex items-center gap-3">
            {score !== null && (
              <span className={`text-sm font-bold ${
                score >= 70 ? 'text-emerald-400' : score >= 40 ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {t('lesson.similarity')} {score}%
              </span>
            )}
            <button
              onClick={() => setPhase(1)}
              className="flex items-center gap-1 text-gray-400 hover:text-gray-200 text-sm"
            >
              <Eye className="w-4 h-4" /> {t('lesson.showOriginal')}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function ExerciseCard({ exercise, number, t }) {
  const [showAnswer, setShowAnswer] = useState(false)
  const [userAnswer, setUserAnswer] = useState('')
  const [selectedOption, setSelectedOption] = useState('')

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="w-6 h-6 rounded-full bg-indigo-700 flex items-center justify-center text-xs font-bold">
          {number}
        </span>
        <span className="badge-blue capitalize text-xs">{exercise.type?.replace('_', ' ')}</span>
      </div>
      <p className="text-gray-300 font-medium mb-3">{exercise.instruction}</p>
      <p className="text-gray-100 mb-3 text-lg">{exercise.content}</p>

      {exercise.type === 'multiple_choice' && exercise.options ? (
        <div className="space-y-2">
          {exercise.options.map((opt, i) => {
            const letter = opt.split('.')[0]?.trim()
            const isSelected = selectedOption === letter
            const isCorrect = showAnswer && letter === exercise.answer
            const isWrong = showAnswer && isSelected && letter !== exercise.answer
            return (
              <div
                key={i}
                className={`answer-option text-sm ${
                  isSelected ? 'selected' : ''
                } ${isCorrect ? 'correct' : ''} ${isWrong ? 'incorrect' : ''}`}
                onClick={() => !showAnswer && setSelectedOption(letter)}
              >
                <span>{opt}</span>
              </div>
            )
          })}
        </div>
      ) : (
        <input
          type="text"
          className="input-field text-sm"
          placeholder={t('lesson.yourAnswer')}
          value={userAnswer}
          onChange={e => setUserAnswer(e.target.value)}
          disabled={showAnswer}
        />
      )}

      <button
        className="text-indigo-400 hover:text-indigo-300 text-sm mt-3 flex items-center gap-1"
        onClick={() => setShowAnswer(!showAnswer)}
      >
        {showAnswer ? t('lesson.hideExerciseAnswer') : t('lesson.showExerciseAnswer')}
      </button>
      {showAnswer && (
        <div className="mt-2 p-2 bg-emerald-900/20 border border-emerald-700/30 rounded text-sm text-emerald-300">
          {t('lesson.answerLabel')} {exercise.answer}
        </div>
      )}
    </div>
  )
}
