import apiClient from './client'

const AGENT = 'main'

/**
 * MCP Server CRUD
 */
export function getMcpServers() {
  return apiClient.get('/agent/get_mcp_server', { _agent: AGENT })
}

export function enrollMcpServer(data) {
  return apiClient.post('/agent/enroll_mcp_server', data, { _agent: AGENT })
}

export function updateMcpServer(data) {
  return apiClient.post('/agent/update_mcp_server', data, { _agent: AGENT })
}

export function deleteMcpServer(data) {
  return apiClient.post('/agent/delete_mcp_server', data, { _agent: AGENT })
}

/**
 * Agent CRUD
 */
export function getAgents() {
  return apiClient.get('/agent/get_agents', { _agent: AGENT })
}

export function createAgent(data) {
  return apiClient.post('/agent/create_agent', data, { _agent: AGENT })
}

export function updateAgent(data) {
  return apiClient.post('/agent/update_agent', data, { _agent: AGENT })
}

export function deleteAgent(data) {
  return apiClient.post('/agent/delete_agent', data, { _agent: AGENT })
}

/**
 * MCP Toolset CRUD
 */
export function getToolsets() {
  return apiClient.post('/agent/get_mcp_toolset', {}, { _agent: AGENT })
}

export function getToolset(data) {
  return apiClient.post('/agent/get_mcp_toolset', data, { _agent: AGENT })
}

export function createToolset(data) {
  return apiClient.post('/agent/create_mcp_toolset', data, { _agent: AGENT })
}

export function updateToolset(data) {
  return apiClient.post('/agent/update_mcp_toolset', data, { _agent: AGENT })
}

export function deleteToolset(data) {
  return apiClient.post('/agent/delete_mcp_toolset', data, { _agent: AGENT })
}

/**
 * Toolset deploy
 */
export function deployToolset(data) {
  return apiClient.post('/agent/adapt_toolset_on_service', data, { _agent: AGENT })
}
