import axios from 'axios'
import { HTTP_STATUS, API_BASE_URL } from '@/utils/constants'

const authFailedStatus = [HTTP_STATUS.unauthorized, HTTP_STATUS.unprocessableEntity]

export async function connect(agent, onConnect = false) {
  const token = sessionStorage.getItem(`${agent}_accessToken`)
  const headers = {
    headers: token && {
      Authorization: `Bearer ${token}`
    },
    withCredentials: true
  }

  return new Promise((resolve, reject) => {
    axios
      .get(`${API_BASE_URL}/hello`, headers)
      .then((res) => {
        if (onConnect) onConnect()
        const accessToken = res.data.access_token
        const refreshToken = res.data.refresh_token
        const sessionKey = res.data.res.data
        if (accessToken) sessionStorage.setItem(`${agent}_accessToken`, accessToken)
        if (refreshToken) sessionStorage.setItem(`${agent}_refreshToken`, refreshToken)
        if (sessionKey) sessionStorage.setItem(`${agent}_sessionKey`, sessionKey)
        resolve()
      })
      .catch((e) => {
        if (authFailedStatus.includes(e.response.status)) {
          refresh(agent, onConnect)
        }
        reject(new Error(e))
      })
  })
}

export function refresh(agent, onConnect = false) {
  const headers = {
    headers: {
      Authorization: `Bearer ${sessionStorage.getItem(`${agent}_refreshToken`)}`
    },
    withCredentials: true
  }

  axios
    .get(`${API_BASE_URL}/refresh`, headers)
    .then((res) => {
      if (onConnect) onConnect()
      const accessToken = res.data.access_token
      sessionStorage.setItem(`${agent}_accessToken`, accessToken)
    })
    .catch((e) => {
      console.log(e)
      if (authFailedStatus.includes(e.response.status)) {
        sessionStorage.removeItem(`${agent}_accessToken`)
        sessionStorage.removeItem(`${agent}_refreshToken`)
        sessionStorage.removeItem(`${agent}_sessionKey`)
        connect(agent, onConnect)
      }
    })
}
