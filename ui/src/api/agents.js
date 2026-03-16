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

/**
 * Prompt versioning & deployment
 */
export function insertPrompt(data) {
  return apiClient.post('/agent/insert_prompt', data, { _agent: AGENT })
}

export function getPromptVersions(data) {
  return apiClient.post('/agent/get_prompt_versions', data, { _agent: AGENT })
}

export function getPromptData(data) {
  return apiClient.post('/agent/get_prompt_data', data, { _agent: AGENT })
}

export function deployPrompt(data) {
  return apiClient.post('/operation/deploy', data, { _agent: AGENT })
}

export function rollbackPrompt(data) {
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

/**
 * Model management
 */
export function getModels() {
  return apiClient.get('/agent/get_models', { _agent: AGENT })
}

export function getCurrentModel(agent) {
  return apiClient.get('/agent/get_current_model', {
    _agent: AGENT,
    params: { agent },
  })
}

export function setVendorAndModel(data) {
  return apiClient.post('/agent/set_vendor_and_model', data, { _agent: AGENT })
}

/**
 * Token operations
 */
export function getTokenSize(data) {
  return apiClient.post('/operation/get_token_size', data, { _agent: AGENT })
}
