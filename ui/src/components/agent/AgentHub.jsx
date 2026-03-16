import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useStore } from '@/store'
import { getMCPToolSetList, getMCPServerList, deleteMCPToolSet, applyToolSetService } from '@/api/mcpApi'
import { agentMeta } from '@/utils/constants'
import styles from './AgentHub.module.scss'

const MCP_CATEGORIES = Object.entries(agentMeta)
  .filter(([, meta]) => meta.isMCP)
  .map(([key, meta]) => ({ key, agent: meta.agent }))

export default function AgentHub() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const mcpServerList = useStore(state => state.mcpServerList)
  const updateMcpServerList = useStore(state => state.updateMcpServerList)

  const [selectedCategory, setSelectedCategory] = useState(MCP_CATEGORIES[0]?.agent || '')
  const [toolsets, setToolsets] = useState([])
  const [servers, setServers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [deployConfirm, setDeployConfirm] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  const fetchServers = useCallback(async () => {
    try {
      const res = await getMCPServerList()
      const list = res.data?.data || []
      setServers(list)
      updateMcpServerList(list)
    } catch (e) { console.error(e) }
  }, [updateMcpServerList])

  const fetchToolsets = useCallback(async (agent) => {
    setIsLoading(true)
    try {
      const res = await getMCPToolSetList({ agent })
      setToolsets(res.data?.data || [])
    } catch (e) { console.error(e) }
    finally { setIsLoading(false) }
  }, [])

  useEffect(() => { fetchServers() }, [fetchServers])
  useEffect(() => { if (selectedCategory) fetchToolsets(selectedCategory) }, [selectedCategory, fetchToolsets])

  const handleDeploy = async (toolset) => {
    try {
      await applyToolSetService({ id: toolset.id, agent: toolset.agent })
      await fetchToolsets(selectedCategory)
      setDeployConfirm(null)
    } catch (e) { console.error(e) }
  }

  const handleDelete = async (toolset) => {
    try {
      await deleteMCPToolSet({ id: toolset.id })
      await fetchToolsets(selectedCategory)
      setDeleteConfirm(null)
    } catch (e) { console.error(e) }
  }

  const liveServerCount = servers.filter(s => s.live).length

  return (
    <div className={styles.container}>
      {/* Summary Bar */}
      <div className={styles.summaryBar}>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>{t('agent.hub.categories')}</span>
          <span className={styles.summaryValue}>{MCP_CATEGORIES.length}</span>
        </div>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>{t('agent.hub.servers')}</span>
          <span className={styles.summaryValue}>
            {liveServerCount}/{servers.length}
            <span className={styles.summaryLive}> live</span>
          </span>
        </div>
      </div>

      <div className={styles.main}>
        {/* Sidebar */}
        <aside className={styles.sidebar}>
          <div className={styles.sidebarSection}>
            <h3 className={styles.sidebarTitle}>{t('agent.hub.agentCategories')}</h3>
            <ul className={styles.categoryList}>
              {MCP_CATEGORIES.map(cat => (
                <li
                  key={cat.agent}
                  className={`${styles.categoryItem} ${selectedCategory === cat.agent ? styles.active : ''}`}
                  onClick={() => setSelectedCategory(cat.agent)}
                >
                  <span className={styles.categoryName}>{cat.agent}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className={styles.sidebarSection}>
            <h3 className={styles.sidebarTitle}>{t('agent.hub.servers')}</h3>
            <ul className={styles.serverList}>
              {servers.map(s => (
                <li key={s.id} className={styles.serverItem}>
                  <span className={`${styles.dot} ${s.live ? styles.live : styles.dead}`} />
                  <span className={styles.serverName}>{s.name}</span>
                </li>
              ))}
            </ul>
            <button className={styles.manageServers} onClick={() => navigate('/admin/servers')}>
              {t('agent.hub.manageServers')}
            </button>
          </div>
        </aside>

        {/* Content */}
        <section className={styles.content}>
          <div className={styles.contentHeader}>
            <h2 className={styles.contentTitle}>{selectedCategory}</h2>
            <button className={styles.createButton} onClick={() => navigate(`/admin/agents/new?category=${selectedCategory}`)}>
              + {t('agent.hub.createAgent')}
            </button>
          </div>

          {isLoading ? (
            <div className={styles.skeletonList}>
              {[1, 2].map(i => <div key={i} className={styles.skeleton} />)}
            </div>
          ) : toolsets.length === 0 ? (
            <div className={styles.empty}>
              <p className={styles.emptyTitle}>{t('agent.hub.emptyTitle')}</p>
              <p className={styles.emptyDesc}>{t('agent.hub.emptyDesc')}</p>
              <button className={styles.emptyButton} onClick={() => navigate(`/admin/agents/new?category=${selectedCategory}`)}>
                {t('agent.hub.createAgent')}
              </button>
            </div>
          ) : (
            <div className={styles.toolsetList}>
              {toolsets.map(ts => (
                <div key={ts.id} className={`${styles.toolsetCard} ${ts.isService ? styles.activeCard : ''}`}>
                  <div className={styles.toolsetHeader}>
                    <div className={styles.toolsetLeft}>
                      <span className={styles.toolsetName}>{ts.name}</span>
                      {ts.isService && <span className={styles.liveBadge}>LIVE</span>}
                      {!ts.isService && <span className={styles.draftBadge}>Draft</span>}
                    </div>
                    <div className={styles.toolsetMeta}>
                      <span>{ts.mcpInfo?.length || 0} {t('agent.hub.servers')}</span>
                      <span>{ts.mcpInfo?.reduce((acc, info) => acc + (info.tools?.length || 0), 0) || 0} {t('agent.server.tools')}</span>
                    </div>
                  </div>
                  {ts.description && <p className={styles.toolsetDesc}>{ts.description}</p>}
                  {ts.mcpInfo?.map((info, idx) => (
                    <div key={idx} className={styles.serverToolGroup}>
                      <span className={styles.serverGroupName}>{info.serverName || info.serverId}</span>
                      <div className={styles.toolTags}>
                        {info.tools?.map((tool, ti) => (
                          <span key={ti} className={styles.toolTag}>{tool}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                  <div className={styles.toolsetFooter}>
                    <span className={styles.toolsetDate}>
                      {ts.regDate ? new Date(ts.regDate).toLocaleDateString() : ''}
                    </span>
                    <div className={styles.toolsetActions}>
                      {!ts.isService && (
                        <button className={styles.deployBtn} onClick={() => setDeployConfirm(ts)}>
                          {t('agent.hub.deploy')}
                        </button>
                      )}
                      <button className={styles.editBtn} onClick={() => navigate(`/admin/agents/${ts.id}?category=${ts.agent}`)}>
                        {t('agent.common.edit')}
                      </button>
                      <button className={styles.deleteActionBtn} onClick={() => setDeleteConfirm(ts)}>
                        {t('agent.common.delete')}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Deploy Confirm Modal */}
      {deployConfirm && (
        <div className={styles.modalOverlay} onClick={() => setDeployConfirm(null)}>
          <div className={styles.confirmModal} onClick={e => e.stopPropagation()}>
            <p className={styles.confirmTitle}>{t('agent.hub.deployConfirmTitle')}</p>
            <p className={styles.confirmDesc}>
              {t('agent.hub.deployConfirmDesc', { name: deployConfirm.name, category: deployConfirm.agent })}
            </p>
            <div className={styles.confirmButtons}>
              <button className={styles.cancelButton} onClick={() => setDeployConfirm(null)}>{t('common.cancel')}</button>
              <button className={styles.confirmButton} onClick={() => handleDeploy(deployConfirm)}>{t('agent.hub.deploy')}</button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm Modal */}
      {deleteConfirm && (
        <div className={styles.modalOverlay} onClick={() => setDeleteConfirm(null)}>
          <div className={styles.confirmModal} onClick={e => e.stopPropagation()}>
            <p className={styles.confirmTitle}>{t('agent.hub.deleteConfirmTitle')}</p>
            <p className={styles.confirmDesc}>
              {t('agent.hub.deleteConfirmDesc', { name: deleteConfirm.name })}
            </p>
            <div className={styles.confirmButtons}>
              <button className={styles.cancelButton} onClick={() => setDeleteConfirm(null)}>{t('common.cancel')}</button>
              <button className={styles.dangerButton} onClick={() => handleDelete(deleteConfirm)}>{t('common.confirm')}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
