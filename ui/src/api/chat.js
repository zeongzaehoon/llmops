import { API_BASE_URL } from '@/utils/constants'
import { getToken } from '@/utils/storage'
import { refresh } from './connectApi'
import apiClient from './client'

/**
 * SSE streaming via fetch (axios does not support streaming).
 * Returns an AbortController so the caller can abort.
 */
export function askStream(agent, payload, { onStart, onData, onEnd, onError } = {}) {
  const aborter = new AbortController()
  const token = getToken(agent, 'access')

  fetch(`${API_BASE_URL}/question/ask`, {
    method: 'POST',
    credentials: 'include',
    signal: aborter.signal,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
    .then((response) => {
      if (!response.ok) {
        if (response.status === 401) {
          refresh(agent)
          onError?.('세션이 만료되었습니다. 다시 질문해주세요.')
        }
        throw response
      }

      const askCode = response.headers.get('AskCode')
      onStart?.(askCode)

      return (async () => {
        const reader = response.body.getReader()
        const decoder = new TextDecoder()

        while (true) {
          const { done, value } = await reader.read()
          if (done) {
            onEnd?.(askCode)
            break
          }
          const decoded = decoder.decode(value, { stream: true })
          onData?.(decoded, askCode)
        }
      })()
    })
    .catch((e) => {
      if (aborter.signal.aborted) return
      onError?.(e)
    })

  return aborter
}

/**
 * Get chat history
 */
export function getHistory(agent) {
  return apiClient.get('/question/get', {
    _agent: agent,
    params: { agent },
  })
}

/**
 * Update rating
 */
export function updateRating(agent, data) {
  return apiClient.post('/question/update_rating', data, { _agent: agent })
}

/**
 * Refer
 */
export function refer(agent, data) {
  return apiClient.post('/question/refer', data, { _agent: agent })
}
