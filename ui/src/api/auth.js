import apiClient from './client'

/**
 * Create session and get JWT tokens
 */
export function connect(agent) {
  return apiClient.get('/hello', { _agent: agent })
}

/**
 * Refresh access token
 */
export function refreshToken(agent) {
  return apiClient.get('/refresh', { _agent: agent })
}
