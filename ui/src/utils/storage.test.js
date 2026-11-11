import { describe, it, expect, beforeEach } from 'vitest'
import { getToken, setToken, clearTokens, saveTokensFromResponse } from './storage'

describe('storage token helpers', () => {
  beforeEach(() => sessionStorage.clear())

  it('sets and gets a token by agent + type', () => {
    setToken('main', 'access', 'AT')
    expect(getToken('main', 'access')).toBe('AT')
    expect(sessionStorage.getItem('main_accessToken')).toBe('AT')
  })

  it('defaults to the access type', () => {
    setToken('cs', 'access', 'X')
    expect(getToken('cs')).toBe('X')
  })

  it('ignores empty values on set', () => {
    setToken('main', 'access', '')
    expect(getToken('main', 'access')).toBeNull()
  })

  it('clears all token types for an agent', () => {
    setToken('main', 'access', 'A')
    setToken('main', 'refresh', 'R')
    setToken('main', 'session', 'S')
    clearTokens('main')
    expect(getToken('main', 'access')).toBeNull()
    expect(getToken('main', 'refresh')).toBeNull()
    expect(getToken('main', 'session')).toBeNull()
  })

  it('saves access/refresh/session from an API response', () => {
    saveTokensFromResponse('main', {
      access_token: 'AT',
      refresh_token: 'RT',
      res: { data: 'SESSION_KEY' }
    })
    expect(getToken('main', 'access')).toBe('AT')
    expect(getToken('main', 'refresh')).toBe('RT')
    expect(getToken('main', 'session')).toBe('SESSION_KEY')
  })

  it('is a no-op for missing response or agent', () => {
    saveTokensFromResponse('main', null)
    expect(getToken('main', 'access')).toBeNull()
  })
})
