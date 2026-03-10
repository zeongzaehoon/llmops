import { create } from 'zustand'
import { LANGS } from '@/utils/constants'

const initialChatOptions = {
  company: null,
  model: null,
  lang: Object.keys(LANGS)[0],
  test: false
}

export const useStore = create((set, get) => ({
  // State
  referenceList: {},
  colorThemes: { default: 'default' },
  customColorThemes: { default: {} },
  chatOptions: { ...initialChatOptions },
  reportIdList: [],
  toolSetList: [],
  activeToolSetId: null,
  mcpServerList: [],
  isDemoReport: false,

  // Getters
  getColorTheme: (agent = 'default') => {
    const state = get()
    return state.colorThemes[agent] || state.colorThemes.default || 'default'
  },
  getCustomColorTheme: (agent = 'default') => {
    const state = get()
    return state.customColorThemes[agent] || state.customColorThemes.default || {}
  },

  // Actions
  updateColorTheme: ({ agent = 'default', theme }) => {
    set((state) => {
      const colorThemes = { ...state.colorThemes, [agent]: theme }
      localStorage.setItem('colorThemes', JSON.stringify(colorThemes))
      return { colorThemes }
    })
  },

  initializeColorThemes: () => {
    const savedThemes = localStorage.getItem('colorThemes')
    const savedCustomThemes = localStorage.getItem('customColorThemes')
    set((state) => ({
      colorThemes: savedThemes
        ? { ...state.colorThemes, ...JSON.parse(savedThemes) }
        : state.colorThemes,
      customColorThemes: savedCustomThemes
        ? { ...state.customColorThemes, ...JSON.parse(savedCustomThemes) }
        : state.customColorThemes
    }))
  },

  updateCustomColorTheme: ({ agent = 'default', colors }) => {
    set((state) => {
      const customColorThemes = { ...state.customColorThemes, [agent]: colors }
      localStorage.setItem('customColorThemes', JSON.stringify(customColorThemes))
      return { customColorThemes }
    })
  },

  insertReferenceItem: ({ agent, reference }) => {
    set((state) => {
      const list = state.referenceList[agent]
        ? [...state.referenceList[agent], reference]
        : [reference]
      return { referenceList: { ...state.referenceList, [agent]: list } }
    })
  },

  changeReferenceList: ({ agent, referenceList }) => {
    set((state) => ({
      referenceList: { ...state.referenceList, [agent]: referenceList }
    }))
  },

  updateChatOptions: (options) => {
    set((state) => ({
      chatOptions: { ...state.chatOptions, ...options }
    }))
  },

  resetChatOptions: () => {
    set({ chatOptions: { ...initialChatOptions } })
  },

  updateReportIdList: (list) => set({ reportIdList: list }),
  updateToolSetList: (list) => set({ toolSetList: list }),
  updateActiveToolSetId: (id) => set({ activeToolSetId: id }),
  updateMcpServerList: (list) => set({ mcpServerList: list }),
  updateIsDemoReport: (value) => set({ isDemoReport: value }),
  selectedAgent: '',
  updateSelectedAgent: (agent) => set({ selectedAgent: agent })
}))
