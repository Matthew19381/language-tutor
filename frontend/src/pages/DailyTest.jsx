import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FlaskConical, ChevronRight, CheckCircle, XCircle,
  AlertTriangle, Trophy, RotateCcw
} from 'lucide-react'
import { getUserId, getDailyTest, submitTest } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'

const STEPS = {
  LOADING: 'loading',
  TESTING: 'testing',
  SUBMITTING: 'submitting',
  RESULTS: 'results',
}

export default function DailyTest() {
  const [step, setStep] = useState(STEPS.LOADING)
  const [testData, setTestData] = useState(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')
  const [textInputs, setTextInputs] = useState({})
  const navigate = useNavigate()
  const userId = getUserId()

  useEffect(() => {
    if (!userId) {
      navigate('/placement')
      return
    }
    getDailyTest(userId)
      .then(data => {
        if (data.already_taken) {
          setResults({
            score: data.score,
            already_taken: true,
            errors: [],
            performance_summary: 'You already completed this test today!'
          })
          setStep(STEPS.RESULTS)
        } else {
          setTestData(data)
          setStep(STEPS.TESTING)
        }
      })
      .catch(e => {
        setError(e.message)
        setStep(STEPS.TESTING)
      })
  }, [userId])

  const questions = testData?.questions || []
  const currentQuestion = questions[currentIndex]

  const handleSelectAnswer = (questionId, letter) => {
    setAnswers(prev => ({ ...prev, [questionId]: letter }))
  }

  const handleTextInput = (questionId, value) => {
    setTextInputs(prev => ({ ...prev, [questionId]: value }))
    setAnswers(prev => ({ ...prev, [questionId]: value }))
  }

  const handleSubmit = async () => {
    setStep(STEPS.SUBMITTING)
    try {
      const res = await submitTest({
        user_id: userId,
        test_type: 'daily',
        questions,
        answers
      })
      setResults(res)
      setStep(STEPS.RESULTS)
    } catch (e) {
      setError(e.message)
      setStep(STEPS.TESTING)
    }
  }

  const answeredCount = Object.keys(answers).length

  if (step === STEPS.LOADING) return <PageLoader text="Loading your daily test..." />

  if (error && step === STEPS.TESTING) {
    return (
      <div className="page-container">
        <div className="card border-red-700/30 bg-red-900/10 text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h2 className="text-xl font-semibold mb-2">Could not load test</h2>
          <p className="text-gray-400 mb-4">{error}</p>
          {error.includes('lesson') && (
            <button onClick={() => navigate('/lesson')} className="btn-primary">
              Go to Today's Lesson
            </button>
          )}
        </div>
      </div>
    )
  }

  if (step === STEPS.SUBMITTING) {
    return (
      <div className="page-container">
        <div className="card text-center py-12">
          <PageLoader text="Analyzing your answers..." />
        </div>
      </div>
    )
  }

  if (step === STEPS.RESULTS && results) {
    return <TestResults results={results} onRetry={() => navigate('/lesson')} />
  }

  if (!currentQuestion) return null

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <FlaskConical className="w-7 h-7 text-purple-400" />
        <div>
          <h1 className="text-2xl font-bold">Daily Test</h1>
          {testData?.lesson_title && (
            <p className="text-gray-400 text-sm">{testData.lesson_title}</p>
          )}
        </div>
      </div>

      {/* Progress */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>Question {currentIndex + 1} of {questions.length}</span>
          <span>{answeredCount}/{questions.length} answered</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-fill bg-purple-500"
            style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Question Card */}
      <div className="card mb-4">
        <div className="flex items-center gap-2 mb-4">
          <span className="badge-purple capitalize">{currentQuestion.type}</span>
          <span className="text-gray-500 text-sm">{currentQuestion.points} pts</span>
        </div>

        <h3 className="text-lg font-medium mb-5 leading-relaxed">
          {currentQuestion.question}
        </h3>

        {/* Options or text input */}
        {currentQuestion.options ? (
          <div className="space-y-3">
            {currentQuestion.options.map((opt, i) => {
              const letter = opt.split('.')[0]?.trim()
              const isSelected = answers[currentQuestion.id] === letter
              return (
                <div
                  key={i}
                  className={`answer-option ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleSelectAnswer(currentQuestion.id, letter)}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0 ${
                    isSelected ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300'
                  }`}>
                    {letter}
                  </div>
                  <span>{opt.substring(opt.indexOf('.') + 1).trim()}</span>
                </div>
              )
            })}
          </div>
        ) : (
          <input
            type="text"
            className="input-field"
            placeholder="Type your answer..."
            value={textInputs[currentQuestion.id] || ''}
            onChange={e => handleTextInput(currentQuestion.id, e.target.value)}
          />
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <button
          className="btn-secondary"
          onClick={() => setCurrentIndex(i => Math.max(0, i - 1))}
          disabled={currentIndex === 0}
        >
          Previous
        </button>

        {currentIndex < questions.length - 1 ? (
          <button
            className="btn-primary flex items-center gap-2"
            onClick={() => setCurrentIndex(i => i + 1)}
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            className="btn-success flex items-center gap-2"
            onClick={handleSubmit}
            disabled={answeredCount === 0}
          >
            Submit <CheckCircle className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Question dots */}
      <div className="flex flex-wrap gap-1.5 mt-4 justify-center">
        {questions.map((q, i) => (
          <button
            key={i}
            className={`w-6 h-6 rounded text-xs transition-colors ${
              i === currentIndex
                ? 'bg-purple-600 text-white'
                : answers[q.id]
                ? 'bg-emerald-700 text-emerald-100'
                : 'bg-gray-700 text-gray-400'
            }`}
            onClick={() => setCurrentIndex(i)}
          >
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  )
}

function TestResults({ results, onRetry }) {
  const score = Math.round(results.score || 0)
  const scoreColor = score >= 80 ? 'emerald' : score >= 60 ? 'yellow' : 'red'
  const errors = results.errors || []

  return (
    <div className="page-container">
      {/* Score */}
      <div className="card text-center mb-6">
        <Trophy className={`w-12 h-12 text-${scoreColor}-400 mx-auto mb-3`} />
        <h2 className="text-2xl font-bold mb-1">
          {results.already_taken ? 'Already completed!' : 'Test Complete!'}
        </h2>
        <div className={`text-5xl font-bold text-${scoreColor}-400 my-3`}>{score}%</div>

        {results.xp_earned > 0 && (
          <div className="badge-blue mx-auto w-fit mb-3">+{results.xp_earned} XP earned</div>
        )}

        {results.performance_summary && (
          <p className="text-gray-400 text-sm leading-relaxed max-w-md mx-auto">
            {results.performance_summary}
          </p>
        )}

        {/* Score bar */}
        <div className="progress-bar mt-4 max-w-xs mx-auto">
          <div
            className={`progress-fill bg-${scoreColor}-500`}
            style={{ width: `${score}%` }}
          />
        </div>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="mb-6">
          <h3 className="section-title flex items-center gap-2">
            <XCircle className="w-5 h-5 text-red-400" />
            Errors to Review ({errors.length})
          </h3>
          <div className="space-y-3">
            {errors.map((err, i) => (
              <div key={i} className="card border-red-700/20">
                <div className="flex items-center gap-2 mb-2">
                  <span className="badge-red capitalize">{err.type}</span>
                </div>
                <p className="text-gray-300 text-sm mb-2">{err.question}</p>
                <div className="flex gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Your answer: </span>
                    <span className="text-red-400">{err.user_answer}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Correct: </span>
                    <span className="text-emerald-400">{err.correct_answer}</span>
                  </div>
                </div>
                {err.explanation && (
                  <p className="text-gray-400 text-sm mt-2 border-t border-gray-700 pt-2">
                    {err.explanation}
                  </p>
                )}
                {err.rule && (
                  <p className="text-indigo-300 text-xs mt-1 italic">Rule: {err.rule}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {errors.length === 0 && score > 0 && !results.already_taken && (
        <div className="card border-emerald-700/30 bg-emerald-900/10 text-center mb-6">
          <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <p className="text-emerald-300 font-semibold">Perfect score! No errors!</p>
          <p className="text-gray-400 text-sm mt-1">Excellent work on today's lesson!</p>
        </div>
      )}

      <button
        className="btn-primary w-full py-3 flex items-center justify-center gap-2"
        onClick={onRetry}
      >
        <RotateCcw className="w-4 h-4" />
        Go to Today's Lesson
      </button>
    </div>
  )
}
