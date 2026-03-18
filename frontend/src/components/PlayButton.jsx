import { useState } from 'react'
import { Volume2, Loader2 } from 'lucide-react'

export default function PlayButton({ text, language, className = '' }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)

  const handlePlay = async (e) => {
    e.stopPropagation()
    if (loading || !text) return
    setLoading(true)
    setError(false)
    try {
      const res = await fetch('/api/audio/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language: language || 'German' }),
      })
      if (!res.ok) throw new Error('TTS failed')
      const data = await res.json()
      const audio = new Audio(data.url)
      audio.play()
    } catch (err) {
      setError(true)
      setTimeout(() => setError(false), 2000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handlePlay}
      disabled={loading}
      title={`Play: ${text}`}
      className={`inline-flex items-center justify-center w-6 h-6 rounded-full hover:bg-gray-700 text-gray-400 hover:text-indigo-300 transition-colors disabled:opacity-50 ${error ? 'text-red-400' : ''} ${className}`}
    >
      {loading ? (
        <Loader2 className="w-3.5 h-3.5 animate-spin" />
      ) : (
        <Volume2 className="w-3.5 h-3.5" />
      )}
    </button>
  )
}
