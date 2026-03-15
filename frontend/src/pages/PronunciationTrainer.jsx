import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mic, MicOff, Volume2, RotateCcw, ChevronRight } from 'lucide-react'
import { getUserId } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'
import axios from 'axios'

export default function PronunciationTrainer() {
  const [phrases, setPhrases] = useState([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [recording, setRecording] = useState(false)
  const [result, setResult] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [customPhrase, setCustomPhrase] = useState('')
  const [useCustom, setUseCustom] = useState(false)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const navigate = useNavigate()
  const userId = getUserId()

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
    axios.get(`/api/pronunciation/phrases/${userId}`)
      .then(r => setPhrases(r.data.phrases || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [userId])

  const currentPhrase = useCustom ? customPhrase : phrases[currentIdx]?.text || ''

  const startRecording = async () => {
    setError('')
    setResult(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        stream.getTracks().forEach(t => t.stop())
        await analyzeAudio(blob)
      }

      mediaRecorder.start()
      setRecording(true)
    } catch (e) {
      setError('Could not access microphone. Please allow microphone access.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop()
      setRecording(false)
    }
  }

  const analyzeAudio = async (blob) => {
    if (!currentPhrase.trim()) {
      setError('Please enter a phrase to practice.')
      return
    }
    setAnalyzing(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('audio', blob, 'recording.webm')
      formData.append('target_text', currentPhrase)
      formData.append('user_id', userId)

      const response = await axios.post('/api/pronunciation/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000,
      })
      setResult(response.data)
    } catch (e) {
      const detail = e.response?.data?.detail || e.message
      setError(`Analysis failed: ${detail}`)
    } finally {
      setAnalyzing(false)
    }
  }

  const nextPhrase = () => {
    setResult(null)
    setCurrentIdx(i => (i + 1) % (phrases.length || 1))
  }

  if (loading) return <PageLoader text="Loading pronunciation trainer..." />

  const scoreColor = result
    ? result.score >= 80 ? 'text-emerald-400'
    : result.score >= 50 ? 'text-yellow-400'
    : 'text-red-400'

  return (
    <div className="page-container max-w-xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Mic className="w-7 h-7 text-purple-400" />
        <div>
          <h1 className="text-2xl font-bold">Pronunciation Trainer</h1>
          <p className="text-gray-400">Record yourself and get instant feedback</p>
        </div>
      </div>

      {/* Phrase Selection */}
      <div className="card mb-4">
        <div className="flex items-center gap-2 mb-3">
          <button
            onClick={() => setUseCustom(false)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              !useCustom ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            From Lessons
          </button>
          <button
            onClick={() => setUseCustom(true)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              useCustom ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Custom Phrase
          </button>
        </div>

        {useCustom ? (
          <input
            type="text"
            className="input-field"
            placeholder="Enter a phrase to practice..."
            value={customPhrase}
            onChange={e => setCustomPhrase(e.target.value)}
          />
        ) : (
          <div>
            {phrases.length > 0 ? (
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-lg font-semibold text-indigo-200">{currentPhrase}</p>
                  {phrases[currentIdx]?.source && (
                    <p className="text-xs text-gray-500 mt-0.5">{phrases[currentIdx].source}</p>
                  )}
                </div>
                <button
                  onClick={nextPhrase}
                  className="p-2 text-gray-400 hover:text-gray-200 transition-colors"
                  title="Next phrase"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <p className="text-gray-400 text-sm">
                Complete some lessons to get practice phrases, or use Custom Phrase.
              </p>
            )}
            {phrases.length > 1 && (
              <p className="text-xs text-gray-600 mt-2">
                {currentIdx + 1} / {phrases.length}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Recording Control */}
      <div className="card mb-4 text-center">
        <p className="text-gray-400 text-sm mb-4">
          {recording ? 'Recording... Click to stop' : 'Click the microphone to start recording'}
        </p>
        <button
          onClick={recording ? stopRecording : startRecording}
          disabled={analyzing || (!currentPhrase.trim())}
          className={`w-24 h-24 rounded-full mx-auto flex items-center justify-center transition-all ${
            recording
              ? 'bg-red-600 hover:bg-red-700 animate-pulse'
              : 'bg-purple-700 hover:bg-purple-600'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {recording
            ? <MicOff className="w-10 h-10 text-white" />
            : <Mic className="w-10 h-10 text-white" />
          }
        </button>
        {analyzing && (
          <p className="text-indigo-400 text-sm mt-4 animate-pulse">Analyzing pronunciation...</p>
        )}
        {error && (
          <p className="text-red-400 text-sm mt-4">{error}</p>
        )}
      </div>

      {/* Result */}
      {result && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-lg">Results</h2>
            <button
              onClick={() => setResult(null)}
              className="text-gray-500 hover:text-gray-300"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          {/* Score */}
          <div className="text-center mb-4">
            <div className={`text-6xl font-bold ${scoreColor}`}>{result.score}</div>
            <div className="text-gray-400 text-sm">/100</div>
            <div className="progress-bar mt-3">
              <div
                className={`progress-fill ${
                  result.score >= 80 ? 'bg-emerald-500' :
                  result.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${result.score}%` }}
              />
            </div>
          </div>

          {/* Feedback */}
          <div className="bg-gray-800 rounded-lg p-3 mb-4">
            <p className="text-gray-200">{result.feedback}</p>
          </div>

          {/* Transcription */}
          <div className="grid grid-cols-1 gap-3 text-sm">
            <div>
              <span className="text-gray-500">You said:</span>
              <p className="text-yellow-300 mt-0.5">{result.transcribed || '(nothing detected)'}</p>
            </div>
            <div>
              <span className="text-gray-500">Target:</span>
              <p className="text-indigo-200 mt-0.5">{result.target}</p>
            </div>
          </div>

          {/* Word-by-word */}
          {result.word_scores?.length > 0 && (
            <div className="mt-4">
              <p className="text-gray-500 text-sm mb-2">Word analysis:</p>
              <div className="flex flex-wrap gap-2">
                {result.word_scores.map((w, i) => (
                  <span
                    key={i}
                    className={`px-2 py-1 rounded text-sm font-medium ${
                      w.correct ? 'bg-emerald-900/40 text-emerald-300' : 'bg-red-900/40 text-red-300'
                    }`}
                  >
                    {w.word}
                    {!w.correct && w.said && (
                      <span className="text-xs text-gray-500 ml-1">({w.said})</span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="flex gap-4 mt-4 text-xs text-gray-500">
            {result.char_similarity !== undefined && (
              <span>Char similarity: <span className="text-gray-300">{result.char_similarity}%</span></span>
            )}
            {result.word_accuracy !== undefined && (
              <span>Word accuracy: <span className="text-gray-300">{result.word_accuracy}%</span></span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
