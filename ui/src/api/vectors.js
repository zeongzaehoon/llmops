import apiClient from './client'

const AGENT = 'main'

export function upsert(data) {
  return apiClient.post('/vector/upsert', data, { _agent: AGENT })
}

export function search(data) {
  return apiClient.post('/vector/search', data, { _agent: AGENT })
}

export function deleteById(data) {
  return apiClient.post('/vector/delete_id', data, { _agent: AGENT })
}

export function deleteByFilter(data) {
  return apiClient.post('/vector/delete_filter', data, { _agent: AGENT })
}
