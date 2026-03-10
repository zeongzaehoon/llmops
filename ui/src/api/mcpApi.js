import axios from 'axios'
import { API_BASE_URL } from '@/utils/constants'

export const getMCPToolSetList = (data) => {
  return axios.post(`${API_BASE_URL}/agent/get_mcp_toolset`, data)
}

export const getMCPServerList = () => {
  return axios.get(`${API_BASE_URL}/agent/get_mcp_server`)
}

export const getMCPServerTools = (data) => {
  return axios.post(`${API_BASE_URL}/agent/get_mcp_server_tools`, data)
}

export const createMCPToolSet = (data) => {
  return axios.post(`${API_BASE_URL}/agent/create_mcp_toolset`, data)
}

export const updateMCPToolSet = (data) => {
  return axios.post(`${API_BASE_URL}/agent/update_mcp_toolset`, data)
}


export const deleteMCPToolSet = (data) => {
  return axios.post(`${API_BASE_URL}/agent/delete_mcp_toolset`, data)
}

export const updateMCPServer = (data) => {
  return axios.post(`${API_BASE_URL}/agent/update_mcp_server`, data)
}

export const deleteMCPServer = (data) => {
  return axios.post(`${API_BASE_URL}/agent/delete_mcp_server`, data)
}

export const applyToolSetService = (data) => {
  return axios.post(`${API_BASE_URL}/agent/adapt_toolset_on_service`, data)
}

export const enrollMCPServer = (data) => {
  return axios.post(`${API_BASE_URL}/agent/enroll_mcp_server`, data)
}