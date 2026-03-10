import apiClient from './client'

const AGENT = 'main'

export function createGraph(data) {
  return apiClient.post('/agent/create_multi_agent_graph', data, { _agent: AGENT })
}

export function getGraphs() {
  return apiClient.get('/agent/get_multi_agent_graphs', { _agent: AGENT })
}

export function getGraph(data) {
  return apiClient.post('/agent/get_multi_agent_graph', data, { _agent: AGENT })
}

export function updateGraph(data) {
  return apiClient.post('/agent/update_multi_agent_graph', data, { _agent: AGENT })
}

export function deleteGraph(data) {
  return apiClient.post('/agent/delete_multi_agent_graph', data, { _agent: AGENT })
}
