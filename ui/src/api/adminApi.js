import axios from 'axios'
import { API_BASE_URL } from '@/utils/constants'

export const getPromptList = (data) => {
  return axios.post(`${API_BASE_URL}/operation/get_version`, data)
}

export const getPrompt = (data) => {
  return axios.post(`${API_BASE_URL}/operation/get_data`, data)
}

export const getPromptHistory = (data) => {
  return axios.post(`${API_BASE_URL}/operation/get_prompt_history`, data)
}

export const insertPrompt = (data) => {
  return axios.post(`${API_BASE_URL}/operation/insert_prompt`, data)
}

export const getReference = (agent, data) => {
  const config = {
    headers: {
      Authorization: `Bearer ${sessionStorage.getItem(`${agent}_accessToken`)}`,
      'Content-Type': `application/json`
    },
    withCredentials: true
  }

  return axios.post(`${API_BASE_URL}/question/refer`, data, config)
}

export const updateMemo = (data) => {
  return axios.post(`${API_BASE_URL}/operation/update_memo`, data)
}

export const downloadQuestion = (data) => {
  return axios.post(`${API_BASE_URL}/operation/download_question`, data, { responseType: 'blob' })
}


export const getDeployList = () => {
  return axios.get(`${API_BASE_URL}/operation/get_deploy_list`)
}

export const deployPrompt = (data) => {
  return axios.post(`${API_BASE_URL}/operation/deploy`, data)
}

export const rollbackPrompt = (data) => {
  return axios.post(`${API_BASE_URL}/operation/rollback`, data)
}

export const getTestModelList = (agent) => {
  return axios.get(`${API_BASE_URL}/question/model?agent=${agent}`)
}

export const getModel = (agent) => {
    return axios.get(`${API_BASE_URL}/operation/get_current_model?agent=${agent}`)
}

export const getModelList = () => {
  return axios.get(`${API_BASE_URL}/operation/get_models`)
}

export const setModel = (data) => {
  return axios.post(`${API_BASE_URL}/operation/set_vendor_and_model`, data)
}
