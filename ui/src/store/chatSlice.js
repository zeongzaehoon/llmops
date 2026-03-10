/**
 * Chat options slice for useAppStore
 */
const initialChatOptions = {
  company: null,
  model: null,
  lang: '한국어',
  test: false,
}

export const createChatSlice = (set) => ({
  chatOptions: { ...initialChatOptions },

  setChatOptions: (options) => {
    set((state) => ({
      chatOptions: { ...state.chatOptions, ...options },
    }))
  },

  resetChatOptions: () => {
    set({ chatOptions: { ...initialChatOptions } })
  },
})
