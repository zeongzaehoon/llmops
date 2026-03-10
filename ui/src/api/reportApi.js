import axios from 'axios'
import { getCookieValue } from '@/utils/utils'
import { BEUSABLE_TOKEN_COOKIE, API_BASE_URL, BEUSABLE_BASE_URL, HUB_BASE_URL } from '@/utils/constants'

const beusableConfig = {
  headers: {
    'Content-Type': `application/json`,
    Authorization: `Bearer ${getCookieValue(BEUSABLE_TOKEN_COOKIE)}`
  }
}

export const getReport = (id) => {
  return axios.get(`${BEUSABLE_BASE_URL}/ai/journeymap/report/${id}`, beusableConfig)
}

export const getReportByVersion = (id, version) => {
  const config = {
    params: { version: version },
    ...beusableConfig
  }

  return axios.get(`${BEUSABLE_BASE_URL}/ai/journeymap/report/${id}`, config)
}

export const updateReportBannerCount = (data) => {
  return axios.post(`${BEUSABLE_BASE_URL}/ai/journeymap/banner_count`, data, beusableConfig)
}

export const updateReportHtml = (data) => {
  return axios.post(`${BEUSABLE_BASE_URL}/ai/journeymap/report_save`, data, beusableConfig)
}

export const getAiCategoryList = () => {
  return axios.post(`${BEUSABLE_BASE_URL}/ai/journeymap/get_ai_category_list`, {}, beusableConfig)
}

export function reportProblem(data) {
  return axios.post(`${BEUSABLE_BASE_URL}/ai/journeymap/report_problem`, data, beusableConfig)
}

export const setReportForChat = (data) => {
  const config = {
    headers: {
      Authorization: `Bearer ${sessionStorage.getItem(`${data.agent}_accessToken`)}`
    }
  }
  return axios.post(`${API_BASE_URL}/question/set_report`, data, config)
}

export const getUserInfo = () => {
  return axios.post(`${BEUSABLE_BASE_URL}/ba/user/get_info`, {}, beusableConfig)
}

export const resetReportChat = (agent) => {
  const config = {
    headers: {
      Authorization: `Bearer ${sessionStorage.getItem(`${agent}_accessToken`)}`
    }
  }
  return axios.get(`${API_BASE_URL}/question/reset_report`, config)
}

export const getTokenStatus = (id, agent) => {
  const config = {
    headers: {
      Authorization: `Bearer ${sessionStorage.getItem(`${agent}_accessToken`)}`
    }
  }
  return axios.get(`${API_BASE_URL}/question/get_token_for_reportchat?Id=${id}`, config)
}

export const docentCheck = (data) => {
  return axios.post(`${HUB_BASE_URL}/v1/heatmap/ai/docent_check`, data, beusableConfig)
}

export const docentStop = (data) => {
  return axios.post(`${HUB_BASE_URL}/v1/heatmap/ai/docent_stop`, data, beusableConfig)
}

export const getScrollReport = (data) => {
  return axios.post(`${HUB_BASE_URL}/v1/heatmap/ai/get_ai_report`, data, beusableConfig)
}

export const getGeoReport = (data) => {
  return axios.post(`${HUB_BASE_URL}/v1/geo/schema/get_report`, data, beusableConfig)
}

export const geoDocentCheck = (data) => {
  return axios.post(`${HUB_BASE_URL}/v1/geo/schema/docent_check`, data, beusableConfig)
}

export const geoDocentStop = (data) => {
  return axios.post(`${HUB_BASE_URL}/v1/geo/schema/docent_stop`, data, beusableConfig)
}
