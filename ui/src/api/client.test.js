import { describe, it, expect, afterEach } from 'vitest'
import apiClient from './client'
import { getToken, setToken } from '@/utils/storage'

// Replace the network adapter so requests resolve locally.
function mockAdapter(responseData = {}) {
  return async (config) => ({
    data: responseData,
    status: 200,
    statusText: 'OK',
    headers: {},
    config
  })
}

describe('apiClient interceptors', () => {
  afterEach(() => {
    sessionStorage.clear()
    delete apiClient.defaults.adapter
  })

  it('attaches a Bearer token from storage for _agent requests', async () => {
    setToken('a1', 'access', 'TOK123')
    let captured
    apiClient.defaults.adapter = async (config) => {
      captured = config
      return { data: {}, status: 200, statusText: 'OK', headers: {}, config }
    }
    await apiClient.get('/x', { _agent: 'a1' })
    const auth = captured.headers.Authorization ?? captured.headers.get?.('Authorization')
    expect(auth).toBe('Bearer TOK123')
  })

  it('does not attach Authorization without an _agent', async () => {
    let captured
    apiClient.defaults.adapter = async (config) => {
      captured = config
      return { data: {}, status: 200, statusText: 'OK', headers: {}, config }
    }
    await apiClient.get('/x')
    const auth = captured.headers.Authorization ?? captured.headers.get?.('Authorization')
    expect(auth).toBeFalsy()
  })

  it('saves access/refresh tokens from the response for _agent', async () => {
    apiClient.defaults.adapter = mockAdapter({ access_token: 'NEW_AT', refresh_token: 'NEW_RT' })
    await apiClient.get('/y', { _agent: 'a2' })
    expect(getToken('a2', 'access')).toBe('NEW_AT')
    expect(getToken('a2', 'refresh')).toBe('NEW_RT')
  })
})
