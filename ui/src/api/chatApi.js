import axios from 'axios'
import { refresh } from './connectApi'
import { AGENT, HTTP_STATUS, API_BASE_URL } from '@/utils/constants'

const authFailedStatus = [HTTP_STATUS.unauthorized]
let aborter = new AbortController()

export async function askQuestion(agent, data, onStart, onDataCallback, onEnd) {
  aborter.abort()
  aborter = new AbortController()

  let headers = {
    Authorization: `Bearer ${sessionStorage.getItem(`${agent}_accessToken`)}`,
    'Content-Type': 'application/json'
  }

  if (agent === AGENT.REPORT_CHAT) {
    data.agent = agent
  }

  let url = `${API_BASE_URL}/question/ask`

  fetch(url, {
    credentials: 'include',
    signal: aborter.signal,
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  })
    .then((response) => {
      if (!response.ok) {
        if (authFailedStatus.includes(response.status)) {
          onEnd(null, 'error')
          onDataCallback('세션이 연장되었습니다. 다시 질문해주세요.')
          refresh(agent)
        }
        throw response
      }

      return response
    })
    .then(async (response) => {
      onStart(response)

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      const askCode = response.headers.get('AskCode')

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          onEnd(response)
          break
        }

        const decoded = decoder.decode(value, { stream: true })
        onDataCallback(decoded, askCode)
      }
    })
    .catch((e) => {
      if (aborter.signal.aborted) return
      onEnd(null, e)
    })
}

export function abortRendering() {
  aborter.abort()
}

export function getHistory(agent) {
  const config = {
    headers: {
      Authorization: `Bearer ${sessionStorage.getItem(`${agent}_accessToken`)}`
    },
    params: {
      agent: agent
    },
    withCredentials: true
  }

  return axios.get(`${API_BASE_URL}/question/get`, config)
}

export const updateSurveyResponse = (agent, data) => {
  const config = {
    headers: {
      Authorization: `Bearer ${sessionStorage.getItem(`${agent}_accessToken`)}`,
      'Content-Type': `application/json`
    },
    withCredentials: true
  }
  return axios.post(`${API_BASE_URL}/operation/update_not_satisfy`, data, config)
}
