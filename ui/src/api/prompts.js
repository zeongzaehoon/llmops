import apiClient from './client'

const AGENT = 'main'

export function insertPrompt(data) {
  return apiClient.post('/operation/insert_prompt', data, { _agent: AGENT })
}

export function getVersion(data) {
  return apiClient.post('/operation/get_version', data, { _agent: AGENT })
}

export function getData(data) {
  return apiClient.post('/operation/get_data', data, { _agent: AGENT })
}

export function deploy(data) {
  return apiClient.post('/operation/deploy', data, { _agent: AGENT })
}

export function rollback(data) {
  return apiClient.post('/operation/rollback', data, { _agent: AGENT })
}

export function getDeployList() {
  return apiClient.get('/operation/get_deploy_list', { _agent: AGENT })
}

export function updateMemo(data) {
  return apiClient.post('/operation/update_memo', data, { _agent: AGENT })
}

export function downloadQuestion(data) {
  return apiClient.post('/operation/download_question', data, {
    _agent: AGENT,
    responseType: 'blob',
  })
}
