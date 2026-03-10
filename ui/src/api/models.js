import apiClient from './client'

const AGENT = 'main'

export function getModels() {
  return apiClient.get('/operation/get_models', { _agent: AGENT })
}

export function getCurrentModel(agent) {
  return apiClient.get('/operation/get_current_model', {
    _agent: AGENT,
    params: { agent },
  })
}

export function setVendorAndModel(data) {
  return apiClient.post('/operation/set_vendor_and_model', data, { _agent: AGENT })
}
