import { useEffect, useMemo } from 'react'
import { useParams, useLocation } from 'react-router-dom'
import { useStore } from './store'
import { agentMeta } from './utils/constants'
import { getInitThemeStyle } from './utils/init'
import AppRoutes from './router'

export default function App() {
  const location = useLocation()
  const params = useParams()

  const categoryFromPath = useMemo(() => {
    const match = location.pathname.match(/\/admin\/(?:chat|history)\/([^/]+)/)
    return match ? match[1] : 'default'
  }, [location.pathname])

  const category = categoryFromPath
  const categoryMetaData = agentMeta[category] || {}

  const colorThemes = useStore((s) => s.colorThemes)
  const customColorThemes = useStore((s) => s.customColorThemes)
  const getColorTheme = useStore((s) => s.getColorTheme)
  const getCustomColorTheme = useStore((s) => s.getCustomColorTheme)
  const initializeColorThemes = useStore((s) => s.initializeColorThemes)

  const customColorTheme = getCustomColorTheme(category)

  const colorTheme = useMemo(() => {
    if (category === 'cs') {
      return colorThemes[category] || 'darkblue'
    } else if (categoryMetaData.isMCP) {
      return colorThemes[category] || 'orange'
    }
    return getColorTheme(category)
  }, [category, categoryMetaData, colorThemes, getColorTheme])

  const themeStyle = useMemo(
    () => getInitThemeStyle(colorTheme, customColorTheme),
    [colorTheme, customColorTheme]
  )

  useEffect(() => {
    initializeColorThemes()
  }, [initializeColorThemes])

  return (
    <div id="app" data-theme={colorTheme} style={themeStyle ? parseCssString(themeStyle) : undefined}>
      <AppRoutes />
      <div id="modals"></div>
    </div>
  )
}

function parseCssString(cssString) {
  if (!cssString) return {}
  const style = {}
  cssString.split(';').forEach((declaration) => {
    const [property, value] = declaration.split(':').map((s) => s.trim())
    if (property && value) {
      const camelCase = property.replace(/^--/, '').startsWith('-')
        ? property
        : property.replace(/-([a-z])/g, (_, c) => c.toUpperCase())
      style[camelCase] = value
    }
  })
  return style
}
