import { useState, useCallback } from 'react'
import { t as translate } from '../i18n/translations'

export function useLanguage() {
  const [lang, setLangState] = useState(
    () => localStorage.getItem('ui_language') || 'pl'
  )

  const setLang = useCallback((newLang) => {
    localStorage.setItem('ui_language', newLang)
    setLangState(newLang)
  }, [])

  const t = useCallback((key) => translate(key, lang), [lang])

  return { lang, setLang, t }
}
