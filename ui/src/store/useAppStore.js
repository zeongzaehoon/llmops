import { create } from 'zustand'
import { createThemeSlice } from './themeSlice'
import { createChatSlice } from './chatSlice'
import { createUiSlice } from './uiSlice'

export const useAppStore = create((...args) => ({
  ...createThemeSlice(...args),
  ...createChatSlice(...args),
  ...createUiSlice(...args),
}))
