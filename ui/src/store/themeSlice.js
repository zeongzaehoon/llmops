/**
 * Theme slice for useAppStore
 */
export const createThemeSlice = (set, get) => ({
  colorThemes: { default: 'default' },
  customColorThemes: { default: {} },

  getColorTheme: (agent = 'default') => {
    const state = get()
    return state.colorThemes[agent] || state.colorThemes.default || 'default'
  },

  setColorTheme: ({ agent = 'default', theme }) => {
    set((state) => {
      const colorThemes = { ...state.colorThemes, [agent]: theme }
      localStorage.setItem('sol_colorThemes', JSON.stringify(colorThemes))
      return { colorThemes }
    })
  },

  setCustomColorTheme: ({ agent = 'default', colors }) => {
    set((state) => {
      const customColorThemes = { ...state.customColorThemes, [agent]: colors }
      localStorage.setItem('sol_customColorThemes', JSON.stringify(customColorThemes))
      return { customColorThemes }
    })
  },

  initThemes: () => {
    const savedThemes = localStorage.getItem('sol_colorThemes')
    const savedCustom = localStorage.getItem('sol_customColorThemes')
    set((state) => ({
      colorThemes: savedThemes
        ? { ...state.colorThemes, ...JSON.parse(savedThemes) }
        : state.colorThemes,
      customColorThemes: savedCustom
        ? { ...state.customColorThemes, ...JSON.parse(savedCustom) }
        : state.customColorThemes,
    }))
  },
})
