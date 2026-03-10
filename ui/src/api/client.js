import axios from 'axios'
import { API_BASE_URL } from '@/utils/constants'
import { getToken, setToken, clearTokens } from '@/utils/storage'

/**
 * Centralized axios instance with:
 * - Request interceptor: auto-attach Bearer token per agent
 * - Response interceptor: auto-save tokens + 401 refresh retry queue
 *
 * Usage: pass `_agent` in the request config:
 *   apiClient.post('/question/ask', data, { _agent: 'main' })
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

// --- Request interceptor ---
apiClient.interceptors.request.use((config) => {
  const agent = config._agent
  if (agent) {
    const token = getToken(agent, 'access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// --- Response interceptor with refresh + retry queue ---
let isRefreshing = false
let refreshSubscribers = []

function onRefreshed(agent) {
  refreshSubscribers.forEach((cb) => cb(agent))
  refreshSubscribers = []
}

function addRefreshSubscriber(callback) {
  refreshSubscribers.push(callback)
}

apiClient.interceptors.response.use(
  (response) => {
    // Auto-save tokens from successful responses
    const agent = response.config._agent
    if (agent && response.data) {
      if (response.data.access_token) {
        setToken(agent, 'access', response.data.access_token)
      }
      if (response.data.refresh_token) {
        setToken(agent, 'refresh', response.data.refresh_token)
      }
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config
    const agent = originalRequest?._agent

    if (
      error.response?.status === 401 &&
      agent &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true

      if (!isRefreshing) {
        isRefreshing = true

        try {
          const refreshToken = getToken(agent, 'refresh')
          if (!refreshToken) {
            throw new Error('No refresh token')
          }

          const res = await axios.get(`${API_BASE_URL}/refresh`, {
            headers: { Authorization: `Bearer ${refreshToken}` },
            withCredentials: true,
          })

          const newAccessToken = res.data.access_token
          if (newAccessToken) {
            setToken(agent, 'access', newAccessToken)
          }

          isRefreshing = false
          onRefreshed(agent)
        } catch (refreshError) {
          isRefreshing = false
          refreshSubscribers = []
          clearTokens(agent)

          // Attempt full reconnect
          try {
            const connectRes = await axios.get(`${API_BASE_URL}/hello`, {
              withCredentials: true,
            })
            if (connectRes.data.access_token) {
              setToken(agent, 'access', connectRes.data.access_token)
            }
            if (connectRes.data.refresh_token) {
              setToken(agent, 'refresh', connectRes.data.refresh_token)
            }
            if (connectRes.data.res?.data) {
              setToken(agent, 'session', connectRes.data.res.data)
            }
          } catch {
            return Promise.reject(refreshError)
          }
        }
      }

      // Queue the retry until refresh completes
      return new Promise((resolve) => {
        addRefreshSubscriber(() => {
          originalRequest.headers.Authorization = `Bearer ${getToken(agent, 'access')}`
          resolve(apiClient(originalRequest))
        })
      })
    }

    return Promise.reject(error)
  }
)

export default apiClient
