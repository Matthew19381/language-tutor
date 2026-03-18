import { useState, useCallback, useEffect } from 'react'
import { t as translate } from '../i18n/translations'

export function useLanguage() {
  const [lang, setLangState] = useState(
    () => localStorage.getItem('ui_language') || 'pl'
  )
  const [hardcoreDict, setHardcoreDict] = useState(() => {
    const cached = localStorage.getItem('ui_hardcore_translations')
    return cached ? JSON.parse(cached) : null
  })

  const targetLanguage = localStorage.getItem('userLanguage') || 'German'

  useEffect(() => {
    if (lang !== 'hardcore') return
    const cachedLang = localStorage.getItem('ui_hardcore_lang')
    if (hardcoreDict && cachedLang === targetLanguage) return

    fetch(`/api/settings/ui-translations?language=${encodeURIComponent(targetLanguage)}`)
      .then(r => r.json())
      .then(data => {
        localStorage.setItem('ui_hardcore_translations', JSON.stringify(data))
        localStorage.setItem('ui_hardcore_lang', targetLanguage)
        setHardcoreDict(data)
      })
      .catch(err => console.error('Failed to load hardcore translations', err))
  }, [lang, targetLanguage])

  const setLang = useCallback((newLang) => {
    if (newLang === 'hardcore') {
      const cachedLang = localStorage.getItem('ui_hardcore_lang')
      if (cachedLang !== targetLanguage) {
        localStorage.removeItem('ui_hardcore_translations')
        localStorage.removeItem('ui_hardcore_lang')
        setHardcoreDict(null)
      }
    }
    localStorage.setItem('ui_language', newLang)
    setLangState(newLang)
  }, [targetLanguage])

  const t = useCallback((key) => {
    if (lang === 'hardcore') {
      if (hardcoreDict) return hardcoreDict[key] || translate(key, 'en')
      return translate(key, 'en')
    }
    return translate(key, lang)
  }, [lang, hardcoreDict])

  return { lang, setLang, t, targetLanguage }
}
