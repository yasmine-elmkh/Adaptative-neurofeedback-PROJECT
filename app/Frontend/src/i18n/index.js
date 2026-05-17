import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import en from './locales/en.json'
import fr from './locales/fr.json'
import ar from './locales/ar.json'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      fr: { translation: fr },
      ar: { translation: ar },
    },
    fallbackLng: 'fr',
    supportedLngs: ['fr', 'en', 'ar'],
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'neurocap_language',
    },
    interpolation: { escapeValue: false },
  })

/* ── Apply RTL + font on language change ── */
i18n.on('languageChanged', (lng) => {
  const isRTL = lng === 'ar'
  document.documentElement.lang = lng
  document.documentElement.dir  = isRTL ? 'rtl' : 'ltr'
})

/* ── Trigger on initial load ── */
const isRTL = i18n.language === 'ar'
document.documentElement.lang = i18n.language || 'fr'
document.documentElement.dir  = isRTL ? 'rtl' : 'ltr'

export default i18n
