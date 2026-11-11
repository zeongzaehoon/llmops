import { describe, it, expect, beforeEach } from 'vitest'
import { createChatSlice } from './chatSlice'
import { createUiSlice } from './uiSlice'
import { createThemeSlice } from './themeSlice'

// Build a slice in isolation with a minimal zustand-like set/get.
function makeSlice(factory) {
  let state
  const get = () => state
  const set = (update) => {
    const partial = typeof update === 'function' ? update(state) : update
    state = { ...state, ...partial }
  }
  state = factory(set, get)
  return get
}

describe('chatSlice', () => {
  it('has sensible defaults', () => {
    const get = makeSlice(createChatSlice)
    expect(get().chatOptions).toEqual({ company: null, model: null, lang: '한국어', test: false })
  })

  it('merges options on setChatOptions', () => {
    const get = makeSlice(createChatSlice)
    get().setChatOptions({ model: 'gpt-4', test: true })
    expect(get().chatOptions).toEqual({ company: null, model: 'gpt-4', lang: '한국어', test: true })
  })

  it('restores defaults on resetChatOptions', () => {
    const get = makeSlice(createChatSlice)
    get().setChatOptions({ model: 'gpt-4' })
    get().resetChatOptions()
    expect(get().chatOptions.model).toBeNull()
  })
})

describe('uiSlice', () => {
  it('toggles and sets the sidebar', () => {
    const get = makeSlice(createUiSlice)
    expect(get().sidebarExpanded).toBe(false)
    get().toggleSidebar()
    expect(get().sidebarExpanded).toBe(true)
    get().setSidebarExpanded(false)
    expect(get().sidebarExpanded).toBe(false)
  })

  it('adds and removes toasts by id', () => {
    const get = makeSlice(createUiSlice)
    const id = get().addToast({ message: 'hi' })
    expect(get().toasts).toHaveLength(1)
    expect(get().toasts[0]).toMatchObject({ id, message: 'hi' })
    get().removeToast(id)
    expect(get().toasts).toHaveLength(0)
  })
})

describe('themeSlice', () => {
  beforeEach(() => localStorage.clear())

  it('falls back to default theme for unknown agents', () => {
    const get = makeSlice(createThemeSlice)
    expect(get().getColorTheme('unknown')).toBe('default')
  })

  it('sets a per-agent theme and persists it', () => {
    const get = makeSlice(createThemeSlice)
    get().setColorTheme({ agent: 'cs', theme: 'darkblue' })
    expect(get().getColorTheme('cs')).toBe('darkblue')
    expect(JSON.parse(localStorage.getItem('sol_colorThemes')).cs).toBe('darkblue')
  })
})
