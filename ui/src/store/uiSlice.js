/**
 * UI state slice for useAppStore
 */
export const createUiSlice = (set) => ({
  sidebarExpanded: false,
  toasts: [],

  toggleSidebar: () => {
    set((state) => ({ sidebarExpanded: !state.sidebarExpanded }))
  },

  setSidebarExpanded: (expanded) => {
    set({ sidebarExpanded: expanded })
  },

  addToast: (toast) => {
    const id = Date.now() + Math.random()
    set((state) => ({
      toasts: [...state.toasts, { id, ...toast }],
    }))
    return id
  },

  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    }))
  },
})
