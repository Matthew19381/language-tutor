import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Youtube, Search, RefreshCw, ExternalLink, Play, X, BookOpen, CheckCircle } from 'lucide-react'
import { getUserId, searchYouTube, addXP } from '../api/client'
import { PageLoader } from '../components/LoadingSpinner'
import { useLanguage } from '../hooks/useLanguage'

export default function Videos() {
  const navigate = useNavigate()
  const userId = getUserId()
  const { t } = useLanguage()

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [activeVideoId, setActiveVideoId] = useState(null)
  const [activityDone, setActivityDone] = useState(false)

  useEffect(() => {
    if (!userId) { navigate('/placement'); return }
    loadSuggested()
  }, [userId])

  const loadSuggested = async () => {
    setLoading(true)
    setError('')
    setActiveVideoId(null)
    setQuery('')
    try {
      const result = await searchYouTube(userId, '')
      setData(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!query.trim()) return
    setSearching(true)
    setError('')
    setActiveVideoId(null)
    try {
      const result = await searchYouTube(userId, query.trim())
      setData(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setSearching(false)
    }
  }

  const handleSuggestedClick = async (sq) => {
    setQuery(sq)
    setSearching(true)
    setError('')
    setActiveVideoId(null)
    try {
      const result = await searchYouTube(userId, sq)
      setData({ ...result, suggested: false })
    } catch (e) {
      setError(e.message)
    } finally {
      setSearching(false)
    }
  }

  const markTabComplete = (tabKey) => {
    try {
      const today = new Date().toISOString().slice(0, 10)
      const raw = localStorage.getItem('daily_tabs')
      const stored = raw ? JSON.parse(raw) : { date: today, tabs: [] }
      const current = stored.date === today ? stored : { date: today, tabs: [] }
      if (!current.tabs.includes(tabKey)) {
        current.tabs.push(tabKey)
        localStorage.setItem('daily_tabs', JSON.stringify(current))
      }
    } catch {}
  }

  const handleMarkDone = async () => {
    markTabComplete('videos')
    setActivityDone(true)
    try { await addXP(userId, 10, 'activity_complete') } catch {}
  }

  if (loading) return <PageLoader text="Szukam filmów dopasowanych do Twojej lekcji..." />

  const videos = data?.videos || []
  const topicVideos = videos.filter(v => v.is_lesson_related)
  const generalVideos = videos.filter(v => !v.is_lesson_related)
  const isCustomSearch = data && !data.suggested

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Youtube className="w-7 h-7 text-red-400" />
          <div>
            <h1 className="text-2xl font-bold">Filmy YouTube</h1>
            <p className="text-gray-400 text-sm">
              {data?.language} · poziom {data?.cefr_level}
              {data?.lesson_topic && !isCustomSearch && (
                <span className="ml-2 text-indigo-400">· temat: {data.lesson_topic}</span>
              )}
            </p>
          </div>
        </div>
        <button
          onClick={loadSuggested}
          disabled={loading || searching}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${(loading || searching) ? 'animate-spin' : ''}`} />
          Odśwież
        </button>
      </div>

      {!activityDone ? (
        <button
          onClick={handleMarkDone}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-700/30 hover:bg-emerald-700/50 border border-emerald-700/40 text-emerald-300 text-sm font-medium transition-colors mb-4"
        >
          <CheckCircle className="w-4 h-4" />
          Oznacz Filmy jako ukończone (+10 XP)
        </button>
      ) : (
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-900/30 border border-emerald-700/40 text-emerald-400 text-sm font-medium mb-4">
          <CheckCircle className="w-4 h-4" />
          Filmy ukończone dziś ✓
        </div>
      )}

      {/* Lesson context banner */}
      {data?.lesson_title && !isCustomSearch && (
        <div className="flex items-center gap-3 bg-indigo-900/20 border border-indigo-700/30 rounded-lg px-4 py-3 mb-5">
          <BookOpen className="w-4 h-4 text-indigo-400 shrink-0" />
          <p className="text-sm text-indigo-300">
            Filmy dopasowane do dzisiejszej lekcji: <span className="font-semibold">{data.lesson_title}</span>
          </p>
        </div>
      )}

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Szukaj filmów... (np. Deutsche Grammatik, Spanish music)"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
          />
          {query && (
            <button type="button" onClick={() => setQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2">
              <X className="w-4 h-4 text-gray-500 hover:text-gray-300" />
            </button>
          )}
        </div>
        <button
          type="submit"
          disabled={searching || !query.trim()}
          className="btn-primary px-4 disabled:opacity-50"
        >
          {searching ? '...' : 'Szukaj'}
        </button>
      </form>

      {/* Suggested queries */}
      {data?.suggested_queries?.length > 0 && !isCustomSearch && (
        <div className="flex flex-wrap gap-2 mb-5">
          {data.suggested_queries.map((sq, i) => (
            <button
              key={i}
              onClick={() => handleSuggestedClick(sq)}
              disabled={searching}
              className={`px-3 py-1.5 rounded-full border text-xs transition-colors ${
                data.topic_queries?.includes(sq)
                  ? 'bg-indigo-900/30 border-indigo-700/50 text-indigo-300 hover:border-indigo-500'
                  : 'bg-gray-800 border-gray-700 text-gray-300 hover:border-gray-500'
              }`}
            >
              {data.topic_queries?.includes(sq) && <span className="mr-1">📚</span>}
              {sq}
            </button>
          ))}
        </div>
      )}

      {error && (
        <div className="card border-red-800/50 bg-red-900/10 mb-4">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Embedded player */}
      {activeVideoId && (
        <div className="card mb-6 p-0 overflow-hidden">
          <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
            <iframe
              className="absolute inset-0 w-full h-full"
              src={`https://www.youtube.com/embed/${activeVideoId}?autoplay=1`}
              title="YouTube video"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
          <div className="p-3 flex justify-end">
            <button
              onClick={() => setActiveVideoId(null)}
              className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-200"
            >
              <X className="w-4 h-4" /> Zamknij odtwarzacz
            </button>
          </div>
        </div>
      )}

      {videos.length === 0 && !error && (
        <p className="text-center text-gray-500 mt-12">Brak wyników.</p>
      )}

      {/* Topic-related section */}
      {topicVideos.length > 0 && (
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-indigo-400 uppercase tracking-wide mb-3 flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            Powiązane z lekcją · {data?.lesson_topic}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {topicVideos.map(video => (
              <VideoCard
                key={video.video_id}
                video={video}
                isActive={activeVideoId === video.video_id}
                onPlay={() => setActiveVideoId(activeVideoId === video.video_id ? null : video.video_id)}
                highlight
              />
            ))}
          </div>
        </div>
      )}

      {/* General / all videos */}
      {generalVideos.length > 0 && (
        <div>
          {topicVideos.length > 0 && (
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Ogólne · poziom {data?.cefr_level}
            </h2>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {generalVideos.map(video => (
              <VideoCard
                key={video.video_id}
                video={video}
                isActive={activeVideoId === video.video_id}
                onPlay={() => setActiveVideoId(activeVideoId === video.video_id ? null : video.video_id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Custom search — no sections */}
      {isCustomSearch && videos.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {videos.map(video => (
            <VideoCard
              key={video.video_id}
              video={video}
              isActive={activeVideoId === video.video_id}
              onPlay={() => setActiveVideoId(activeVideoId === video.video_id ? null : video.video_id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function VideoCard({ video, isActive, onPlay, highlight }) {
  return (
    <div className={`card p-0 overflow-hidden transition-all ${
      isActive ? 'ring-2 ring-indigo-500' : highlight ? 'ring-1 ring-indigo-800/40' : ''
    }`}>
      <div className="relative group cursor-pointer" onClick={onPlay}>
        {video.thumbnail ? (
          <img src={video.thumbnail} alt={video.title} className="w-full aspect-video object-cover" />
        ) : (
          <div className="w-full aspect-video bg-gray-800 flex items-center justify-center">
            <Youtube className="w-10 h-10 text-gray-600" />
          </div>
        )}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="w-14 h-14 bg-black/70 rounded-full flex items-center justify-center">
            <Play className="w-6 h-6 text-white ml-1" fill="white" />
          </div>
        </div>
        {isActive && (
          <div className="absolute top-2 left-2 bg-red-600 text-white text-xs px-2 py-0.5 rounded font-medium">
            ▶ ODTWARZANIE
          </div>
        )}
      </div>

      <div className="p-3">
        <h3 className="text-sm font-semibold text-gray-100 line-clamp-2 mb-1 leading-snug">{video.title}</h3>
        <p className="text-xs text-gray-500 mb-2">{video.channel} · {video.published_at}</p>
        {video.description && (
          <p className="text-xs text-gray-600 line-clamp-2">{video.description}</p>
        )}

        <div className="flex gap-2 mt-3">
          <button
            onClick={onPlay}
            className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-red-700/30 hover:bg-red-700/50 text-red-300 text-xs font-medium transition-colors"
          >
            <Play className="w-3.5 h-3.5" />
            {isActive ? 'Zamknij' : 'Odtwórz'}
          </button>
          <a
            href={video.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 text-xs transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            YT
          </a>
        </div>
      </div>
    </div>
  )
}
