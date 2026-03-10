import apiClient from './client'

const AGENT = 'main'

export function getTokenSize(data) {
  return apiClient.post('/operation/get_token_size', data, { _agent: AGENT })
}
