import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  MessageSquare, Send, Square, User, Bot,
  Lightbulb, ChevronDown, ChevronUp, BarChart3,
  HelpCircle, AlertCircle
} from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import { getUserId, startConversation, sendMessage, analyzeConversation, askQuestion } from '../api/client'

const TOPICS = [
  'everyday conversation',
  'at a restaurant',
  'shopping',
  'asking for directions',
  'at the doctor',
  'job interview',
  'talking about hobbies',
  'planning a trip',
  'at the hotel',
  'making friends'
]

const MODES = { SETUP: 'setup', CHAT: 'chat', RESULTS: 'results', QA: 'qa' }

export default function Conversation() {
  const [mode, setMode] = useState(MODES.SETUP)
  const [topic, setTopic] = useState('everyday conversation')
  const [sessionId, setSessionId] = useState(null)
  const [scenario, setScenario] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiTyping, setAiTyping] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [showPhrases, setShowPhrases] = useState(false)
  const [question, setQuestion] = useState('')
  const [qaAnswer, setQaAnswer] = useState('')
  const [qaLoading, setQaLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const navigate = useNavigate()
  const userId = getUserId()

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
  }, [userId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleStart = async () => {
    setLoading(true)
    try {
      const res = await startConversation(userId, topic)
      setSessionId(res.session_id)
      setScenario(res)
      setMessages([{
        role: 'assistant',
        content: res.opening_line,
        id: Date.now()
      }])
      setMode(MODES.CHAT)
    } catch (e) {
      alert('Error: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!inputText.trim() || !sessionId) return

    const userMsg = { role: 'user', content: inputText.trim(), id: Date.now() }
    setMessages(prev => [...prev, userMsg])
    setInputText('')
    setAiTyping(true)

    try {
      const res = await sendMessage(sessionId, userMsg.content)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.response,
        id: Date.now()
      }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Error getting response. Please try again.',
        id: Date.now()
      }])
    } finally {
      setAiTyping(false)
    }
  }

  const handleEnd = async () => {
    if (!sessionId) return
    setLoading(true)
    try {
      const res = await analyzeConversation(sessionId, userId)
      setAnalysis(res)
      setMode(MODES.RESULTS)
    } catch (e) {
      alert('Error analyzing: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAskQuestion = async () => {
    if (!question.trim()) return
    setQaLoading(true)
    try {
      const res = await askQuestion(question, userId)
      setQaAnswer(res.answer)
    } catch (e) {
      setQaAnswer('Error: ' + e.message)
    } finally {
      setQaLoading(false)
    }
  }

  // Setup
  if (mode === MODES.SETUP) {
    return (
      <div className="page-container">
        <div className="flex items-center gap-3 mb-8">
          <MessageSquare className="w-7 h-7 text-emerald-400" />
          <h1 className="text-2xl font-bold">Conversation Practice</h1>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Start conversation */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Start Conversation</h2>
            <p className="text-gray-400 text-sm mb-4">
              Practice speaking with an AI tutor. Choose a scenario and have a realistic conversation.
            </p>
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2">Choose a topic</label>
              <select
                className="input-field"
                value={topic}
                onChange={e => setTopic(e.target.value)}
              >
                {TOPICS.map(t => (
                  <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2">Or enter custom topic</label>
              <input
                className="input-field"
                placeholder="e.g., talking about German culture"
                value={topic}
                onChange={e => setTopic(e.target.value)}
              />
            </div>
            <button
              className="btn-success w-full py-3 flex items-center justify-center gap-2"
              onClick={handleStart}
              disabled={loading}
            >
              {loading ? <LoadingSpinner size="sm" /> : <MessageSquare className="w-4 h-4" />}
              {loading ? 'Setting up scenario...' : 'Start Conversation'}
            </button>
          </div>

          {/* Ask a question */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-blue-400" />
              Ask a Question
            </h2>
            <p className="text-gray-400 text-sm mb-4">
              Got a grammar question? Not sure about a word? Ask your AI tutor!
            </p>
            <textarea
              className="input-field h-24 resize-none mb-3"
              placeholder="e.g., What's the difference between 'du' and 'Sie' in German?"
              value={question}
              onChange={e => setQuestion(e.target.value)}
            />
            <button
              className="btn-primary w-full mb-3"
              onClick={handleAskQuestion}
              disabled={qaLoading || !question.trim()}
            >
              {qaLoading ? 'Thinking...' : 'Ask Question'}
            </button>
            {qaAnswer && (
              <div className="bg-gray-800 rounded-lg p-4 text-sm text-gray-300 leading-relaxed max-h-40 overflow-y-auto whitespace-pre-line">
                {qaAnswer}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Chat
  if (mode === MODES.CHAT) {
    return (
      <div className="max-w-2xl mx-auto flex flex-col h-[calc(100vh-64px)]">
        {/* Chat header */}
        <div className="bg-gray-900 border-b border-gray-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold">{scenario?.scenario}</h2>
              <p className="text-gray-400 text-sm">
                You: {scenario?.user_role} | AI: {scenario?.ai_role}
              </p>
            </div>
            <button
              className="btn-danger text-sm flex items-center gap-1.5"
              onClick={handleEnd}
              disabled={loading}
            >
              {loading ? <LoadingSpinner size="sm" /> : <Square className="w-3 h-3" />}
              End & Analyze
            </button>
          </div>

          {/* Suggested phrases toggle */}
          {scenario?.suggested_phrases?.length > 0 && (
            <div className="mt-3">
              <button
                className="text-indigo-400 text-xs flex items-center gap-1"
                onClick={() => setShowPhrases(!showPhrases)}
              >
                <Lightbulb className="w-3 h-3" />
                Useful phrases
                {showPhrases ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
              {showPhrases && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {scenario.suggested_phrases.map((phrase, i) => (
                    <button
                      key={i}
                      className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-2 py-1 rounded-full transition-colors"
                      onClick={() => setInputText(phrase)}
                    >
                      {phrase}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map(msg => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'assistant' ? 'bg-emerald-700' : 'bg-indigo-700'
              }`}>
                {msg.role === 'assistant' ? (
                  <Bot className="w-4 h-4 text-white" />
                ) : (
                  <User className="w-4 h-4 text-white" />
                )}
              </div>
              <div className={`max-w-xs lg:max-w-sm rounded-2xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-tr-sm'
                  : msg.role === 'system'
                  ? 'bg-red-900/50 text-red-300 rounded-tl-sm'
                  : 'bg-gray-800 text-gray-100 rounded-tl-sm'
              }`}>
                <p className="text-sm leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}

          {aiTyping && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-700 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex gap-1">
                  {[0, 1, 2].map(i => (
                    <div
                      key={i}
                      className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-gray-900 border-t border-gray-800 p-4">
          <div className="flex gap-3">
            <input
              className="input-field flex-1"
              placeholder="Type your message..."
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
              disabled={aiTyping}
            />
            <button
              className="btn-primary px-4 flex items-center justify-center"
              onClick={handleSend}
              disabled={!inputText.trim() || aiTyping}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-gray-600 text-xs mt-2 text-center">
            {messages.filter(m => m.role === 'user').length} messages sent
          </p>
        </div>
      </div>
    )
  }

  // Results
  if (mode === MODES.RESULTS && analysis) {
    const score = analysis.score || 0
    return (
      <div className="page-container">
        <div className="flex items-center gap-3 mb-6">
          <BarChart3 className="w-7 h-7 text-emerald-400" />
          <h1 className="text-2xl font-bold">Conversation Analysis</h1>
        </div>

        {/* Score */}
        <div className="card text-center mb-6">
          <div className={`text-5xl font-bold mb-2 ${
            score >= 80 ? 'text-emerald-400' : score >= 60 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {Math.round(score)}%
          </div>
          <p className="text-gray-400">{analysis.summary}</p>
          {analysis.xp_earned > 0 && (
            <span className="badge-blue mt-2 inline-block">+{analysis.xp_earned} XP</span>
          )}
        </div>

        {/* Strengths */}
        {analysis.strengths?.length > 0 && (
          <div className="card mb-4">
            <h3 className="font-semibold text-emerald-400 mb-3">What you did well</h3>
            <ul className="space-y-1">
              {analysis.strengths.map((s, i) => (
                <li key={i} className="text-gray-300 text-sm flex gap-2">
                  <span className="text-emerald-500">✓</span> {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Errors */}
        {analysis.errors?.length > 0 && (
          <div className="card mb-4">
            <h3 className="font-semibold text-red-400 mb-3">Errors to review</h3>
            <div className="space-y-3">
              {analysis.errors.map((err, i) => (
                <div key={i} className="border-l-2 border-red-700 pl-3">
                  <div className="flex gap-2 text-sm mb-1">
                    <span className="text-red-400 line-through">{err.original}</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-emerald-400">{err.correction}</span>
                  </div>
                  <p className="text-gray-500 text-xs">{err.explanation}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {analysis.recommendations?.length > 0 && (
          <div className="card mb-6">
            <h3 className="font-semibold text-indigo-400 mb-3">Recommendations</h3>
            <ul className="space-y-2">
              {analysis.recommendations.map((r, i) => (
                <li key={i} className="text-gray-300 text-sm flex gap-2">
                  <span className="text-indigo-400 shrink-0">•</span> {r}
                </li>
              ))}
            </ul>
          </div>
        )}

        <button
          className="btn-primary w-full"
          onClick={() => { setMode(MODES.SETUP); setMessages([]); setAnalysis(null) }}
        >
          Start New Conversation
        </button>
      </div>
    )
  }

  return null
}
