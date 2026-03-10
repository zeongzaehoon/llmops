import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import ko from './ko.json'
import en from './en.json'
import ja from './ja.json'

i18n.use(initReactI18next).init({
  resources: {
    ko: { translation: ko },
    en: { translation: en },
    ja: { translation: ja }
  },
  lng: 'ko',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false
  }
})

i18n.on('languageChanged', (lng) => {
  document.documentElement.lang = lng
})

document.documentElement.lang = i18n.language

export default i18n
