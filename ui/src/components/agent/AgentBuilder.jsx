import { useState, useEffect, useCallback, useMemo } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useStore } from '@/store'
import {
  getMCPServerList,
  getMCPServerTools,
  getMCPToolSetList,
  createMCPToolSet,
  updateMCPToolSet
} from '@/api/mcpApi'
import { agentMeta } from '@/utils/constants'
import styles from './AgentBuilder.module.scss'

const MCP_CATEGORIES = Object.entries(agentMeta)
  .filter(([, meta]) => meta.isMCP)
  .map(([key, meta]) => ({ key, agent: meta.agent }))

export default function AgentBuilder() {
  const { t } = useTranslation()
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const updateMcpServerList = useStore(state => state.updateMcpServerList)

  const isEditing = Boolean(id)
  const initialAgent = searchParams.get('category') || MCP_CATEGORIES[0]?.agent || ''

  // Form state
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [agent, setAgent] = useState(initialAgent)

  // Server & tool state
  const [servers, setServers] = useState([])
  const [serverToolsMap, setServerToolsMap] = useState({})
  const [expandedServers, setExpandedServers] = useState({})
  const [loadingTools, setLoadingTools] = useState({})

  // Selected tools: { serverId, serverName, tools: string[] }[]
  const [selectedMcpInfo, setSelectedMcpInfo] = useState([])

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoadingData, setIsLoadingData] = useState(true)

  // Fetch servers
  const fetchServers = useCallback(async () => {
    try {
      const res = await getMCPServerList()
      const list = res.data?.res?.data || []
      setServers(list)
      updateMcpServerList(list)
    } catch (e) { console.error(e) }
  }, [updateMcpServerList])

  // Fetch tools for a server
  const fetchServerTools = useCallback(async (serverId) => {
    if (serverToolsMap[serverId]) return
    setLoadingTools(prev => ({ ...prev, [serverId]: true }))
    try {
      const res = await getMCPServerTools({ serverId })
      const tools = res.data?.res?.data || []
      setServerToolsMap(prev => ({ ...prev, [serverId]: tools }))
    } catch (e) { console.error(e) }
    finally { setLoadingTools(prev => ({ ...prev, [serverId]: false })) }
  }, [serverToolsMap])

  // Fetch existing toolset for editing
  const fetchToolset = useCallback(async () => {
    if (!isEditing) { setIsLoadingData(false); return }
    try {
      const categoryParam = searchParams.get('category') || ''
      const res = await getMCPToolSetList({ agent: categoryParam })
      const list = res.data?.res?.data || []
      const toolset = list.find(ts => ts.id === id)
      if (toolset) {
        setName(toolset.name || '')
        setDescription(toolset.description || '')
        setAgent(toolset.agent || categoryParam)
        setSelectedMcpInfo(toolset.mcpInfo || [])
      }
    } catch (e) { console.error(e) }
    finally { setIsLoadingData(false) }
  }, [id, isEditing, searchParams])

  useEffect(() => { fetchServers() }, [fetchServers])
  useEffect(() => { fetchToolset() }, [fetchToolset])

  // Toggle server expansion and fetch tools
  const toggleServer = (server) => {
    const serverId = server.id
    setExpandedServers(prev => {
      const next = { ...prev, [serverId]: !prev[serverId] }
      if (next[serverId]) fetchServerTools(serverId)
      return next
    })
  }

  // Check if a tool is selected
  const isToolSelected = (serverId, toolName) => {
    const serverInfo = selectedMcpInfo.find(info => info.serverId === serverId)
    return serverInfo?.tools?.includes(toolName) || false
  }

  // Toggle a tool selection
  const toggleTool = (server, toolName) => {
    setSelectedMcpInfo(prev => {
      const existing = prev.find(info => info.serverId === server.id)
      if (existing) {
        const hasTool = existing.tools.includes(toolName)
        if (hasTool) {
          const newTools = existing.tools.filter(t => t !== toolName)
          if (newTools.length === 0) {
            return prev.filter(info => info.serverId !== server.id)
          }
          return prev.map(info =>
            info.serverId === server.id ? { ...info, tools: newTools } : info
          )
        } else {
          return prev.map(info =>
            info.serverId === server.id
              ? { ...info, tools: [...info.tools, toolName] }
              : info
          )
        }
      } else {
        return [...prev, { serverId: server.id, serverName: server.name, tools: [toolName] }]
      }
    })
  }

  // Add all tools from a server
  const addAllTools = (server) => {
    const tools = serverToolsMap[server.id]
    if (!tools || tools.length === 0) return
    const toolNames = tools.map(t => t.name || t)
    setSelectedMcpInfo(prev => {
      const filtered = prev.filter(info => info.serverId !== server.id)
      return [...filtered, { serverId: server.id, serverName: server.name, tools: toolNames }]
    })
  }

  // Remove all tools from a server
  const removeServerTools = (serverId) => {
    setSelectedMcpInfo(prev => prev.filter(info => info.serverId !== serverId))
  }

  // Remove a single tool from selected
  const removeSelectedTool = (serverId, toolName) => {
    setSelectedMcpInfo(prev => {
      return prev.map(info => {
        if (info.serverId !== serverId) return info
        const newTools = info.tools.filter(t => t !== toolName)
        return newTools.length === 0 ? null : { ...info, tools: newTools }
      }).filter(Boolean)
    })
  }

  // Summary counts
  const totalSelectedTools = useMemo(
    () => selectedMcpInfo.reduce((acc, info) => acc + info.tools.length, 0),
    [selectedMcpInfo]
  )
  const totalSelectedServers = selectedMcpInfo.length

  // Submit
  const handleSubmit = async () => {
    if (!name.trim()) return
    if (selectedMcpInfo.length === 0) return

    setIsSubmitting(true)
    try {
      const payload = {
        name: name.trim(),
        description: description.trim(),
        agent: agent,
        mcpInfo: selectedMcpInfo
      }

      if (isEditing) {
        await updateMCPToolSet({ ...payload, id })
      } else {
        await createMCPToolSet(payload)
      }
      navigate(`/admin/agents?category=${agent}`)
    } catch (e) { console.error(e) }
    finally { setIsSubmitting(false) }
  }

  if (isLoadingData) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>{t('common.loading')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      {/* Top Bar */}
      <div className={styles.topBar}>
        <button className={styles.backButton} onClick={() => navigate(-1)}>
          &larr; {t('common.back')}
        </button>
        <h1 className={styles.pageTitle}>
          {isEditing ? t('agent.builder.editTitle') : t('agent.builder.createTitle')}
        </h1>
      </div>

      <div className={styles.columns}>
        {/* Left: Source Panel */}
        <div className={styles.sourcePanel}>
          <h3 className={styles.panelTitle}>{t('agent.builder.availableTools')}</h3>
          <div className={styles.serverAccordion}>
            {servers.map(server => (
              <div key={server.id} className={styles.accordionItem}>
                <div
                  className={styles.accordionHeader}
                  onClick={() => toggleServer(server)}
                >
                  <div className={styles.accordionLeft}>
                    <span className={`${styles.chevron} ${expandedServers[server.id] ? styles.expanded : ''}`}>
                      &#9654;
                    </span>
                    <span className={`${styles.statusDot} ${server.live ? styles.live : styles.dead}`} />
                    <span className={styles.accordionName}>{server.name}</span>
                  </div>
                  {serverToolsMap[server.id] && (
                    <button
                      className={styles.addAllBtn}
                      onClick={(e) => { e.stopPropagation(); addAllTools(server) }}
                    >
                      {t('agent.builder.addAll')}
                    </button>
                  )}
                </div>

                {expandedServers[server.id] && (
                  <div className={styles.accordionBody}>
                    {loadingTools[server.id] ? (
                      <div className={styles.toolsLoading}>
                        <div className={styles.miniSpinner} />
                      </div>
                    ) : (
                      <ul className={styles.toolList}>
                        {(serverToolsMap[server.id] || []).map((tool, idx) => {
                          const toolName = tool.name || tool
                          const toolDesc = tool.description || ''
                          const selected = isToolSelected(server.id, toolName)
                          return (
                            <li
                              key={idx}
                              className={`${styles.toolItem} ${selected ? styles.selected : ''}`}
                              onClick={() => toggleTool(server, toolName)}
                            >
                              <div className={styles.toolCheckbox}>
                                <span className={`${styles.checkbox} ${selected ? styles.checked : ''}`} />
                              </div>
                              <div className={styles.toolInfo}>
                                <span className={styles.toolName}>{toolName}</span>
                                {toolDesc && <span className={styles.toolDesc}>{toolDesc}</span>}
                              </div>
                            </li>
                          )
                        })}
                        {(serverToolsMap[server.id] || []).length === 0 && (
                          <li className={styles.noTools}>{t('agent.builder.noTools')}</li>
                        )}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            ))}
            {servers.length === 0 && (
              <p className={styles.noServers}>{t('agent.builder.noServers')}</p>
            )}
          </div>
        </div>

        {/* Center: Workspace */}
        <div className={styles.workspace}>
          <h3 className={styles.panelTitle}>{t('agent.builder.configuration')}</h3>
          <div className={styles.formGroup}>
            <label className={styles.label}>{t('agent.builder.name')}</label>
            <input
              className={styles.input}
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder={t('agent.builder.namePlaceholder')}
              maxLength={100}
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>{t('agent.builder.agent')}</label>
            {isEditing ? (
              <div className={styles.readonlyField}>{agent}</div>
            ) : (
              <select
                className={styles.select}
                value={agent}
                onChange={e => setAgent(e.target.value)}
              >
                {MCP_CATEGORIES.map(cat => (
                  <option key={cat.agent} value={cat.agent}>{cat.agent}</option>
                ))}
              </select>
            )}
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>{t('agent.builder.description')}</label>
            <textarea
              className={styles.textarea}
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder={t('agent.builder.descriptionPlaceholder')}
              rows={3}
            />
          </div>

          <div className={styles.selectedSection}>
            <h4 className={styles.selectedTitle}>
              {t('agent.builder.selectedTools')}
              <span className={styles.selectedCount}>{totalSelectedTools}</span>
            </h4>

            {selectedMcpInfo.length === 0 ? (
              <div className={styles.selectedEmpty}>
                <p>{t('agent.builder.selectedEmptyDesc')}</p>
              </div>
            ) : (
              <div className={styles.selectedGroups}>
                {selectedMcpInfo.map(info => (
                  <div key={info.serverId} className={styles.selectedGroup}>
                    <div className={styles.selectedGroupHeader}>
                      <span className={styles.selectedGroupName}>
                        {info.serverName || info.serverId}
                      </span>
                      <button
                        className={styles.removeGroupBtn}
                        onClick={() => removeServerTools(info.serverId)}
                      >
                        {t('agent.builder.removeAll')}
                      </button>
                    </div>
                    <div className={styles.selectedTags}>
                      {info.tools.map(toolName => (
                        <span key={toolName} className={styles.selectedTag}>
                          {toolName}
                          <button
                            className={styles.removeTagBtn}
                            onClick={() => removeSelectedTool(info.serverId, toolName)}
                          >
                            &times;
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Preview */}
        <div className={styles.previewPanel}>
          <h3 className={styles.panelTitle}>{t('agent.builder.preview')}</h3>
          <div className={styles.previewCard}>
            <div className={styles.previewField}>
              <span className={styles.previewLabel}>{t('agent.builder.name')}</span>
              <span className={styles.previewValue}>{name || '-'}</span>
            </div>
            <div className={styles.previewField}>
              <span className={styles.previewLabel}>{t('agent.builder.agent')}</span>
              <span className={styles.previewValue}>{agent}</span>
            </div>
            {description && (
              <div className={styles.previewField}>
                <span className={styles.previewLabel}>{t('agent.builder.description')}</span>
                <span className={styles.previewValue}>{description}</span>
              </div>
            )}
            <div className={styles.previewDivider} />
            <div className={styles.previewStats}>
              <div className={styles.previewStat}>
                <span className={styles.previewStatNum}>{totalSelectedServers}</span>
                <span className={styles.previewStatLabel}>{t('agent.hub.servers')}</span>
              </div>
              <div className={styles.previewStat}>
                <span className={styles.previewStatNum}>{totalSelectedTools}</span>
                <span className={styles.previewStatLabel}>{t('agent.server.tools')}</span>
              </div>
            </div>
            <div className={styles.previewDivider} />
            {selectedMcpInfo.map(info => (
              <div key={info.serverId} className={styles.previewGroup}>
                <span className={styles.previewGroupName}>{info.serverName || info.serverId}</span>
                <ul className={styles.previewToolList}>
                  {info.tools.map(toolName => (
                    <li key={toolName} className={styles.previewToolItem}>{toolName}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <button
            className={styles.submitButton}
            onClick={handleSubmit}
            disabled={isSubmitting || !name.trim() || selectedMcpInfo.length === 0}
          >
            {isSubmitting
              ? t('common.loading')
              : isEditing
                ? t('agent.builder.update')
                : t('agent.builder.create')
            }
          </button>
        </div>
      </div>
    </div>
  )
}
