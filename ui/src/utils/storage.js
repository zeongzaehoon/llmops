/**
 * sessionStorage wrapper for token management.
 * Wraps the existing pattern: sessionStorage.getItem(`${agent}_accessToken`)
 */

const TOKEN_TYPES = {
  access: 'accessToken',
  refresh: 'refreshToken',
  session: 'sessionKey',
}

/**
 * Get a token from sessionStorage
 * @param {string} agent - e.g. 'main', 'cs', 'scrollChat'
 * @param {'access'|'refresh'|'session'} type
 * @returns {string|null}
 */
export function getToken(agent, type = 'access') {
  const key = `${agent}_${TOKEN_TYPES[type] || type}`
  return sessionStorage.getItem(key)
}

/**
 * Set a token in sessionStorage
 * @param {string} agent
 * @param {'access'|'refresh'|'session'} type
 * @param {string} value
 */
export function setToken(agent, type, value) {
  if (!value) return
  const key = `${agent}_${TOKEN_TYPES[type] || type}`
  sessionStorage.setItem(key, value)
}

/**
 * Clear all tokens for a given agent
 * @param {string} agent
 */
export function clearTokens(agent) {
  Object.values(TOKEN_TYPES).forEach((suffix) => {
    sessionStorage.removeItem(`${agent}_${suffix}`)
  })
}

/**
 * Save all tokens from an API response for an agent
 * @param {string} agent
 * @param {object} responseData - { access_token, refresh_token, res: { data } }
 */
export function saveTokensFromResponse(agent, responseData) {
  if (!responseData || !agent) return
  setToken(agent, 'access', responseData.access_token)
  setToken(agent, 'refresh', responseData.refresh_token)
  if (responseData.res?.data && typeof responseData.res.data === 'string') {
    setToken(agent, 'session', responseData.res.data)
  }
}
