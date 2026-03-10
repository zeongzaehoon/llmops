import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { useStore } from '@/store'
import { getMCPServerList, deleteMCPServer } from '@/api/mcpApi'
import ServerCard from './components/ServerCard'
import ServerFormModal from './ServerFormModal'
import styles from './ServerRegistry.module.scss'

export default function ServerRegistry() {
  const { t } = useTranslation()
  const updateMcpServerList = useStore(state => state.updateMcpServerList)
  const [servers, setServers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingServer, setEditingServer] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  const fetchServers = useCallback(async () => {
    setIsLoading(true)
    try {
      const res = await getMCPServerList()
      const list = res.data?.res?.data || []
      setServers(list)
      updateMcpServerList(list)
    } catch (e) {
      console.error(e)
    } finally {
      setIsLoading(false)
    }
  }, [updateMcpServerList])

  useEffect(() => { fetchServers() }, [fetchServers])

  const handleEdit = (server) => {
    setEditingServer(server)
    setShowForm(true)
  }

  const handleDelete = async (server) => {
    try {
      const res = await deleteMCPServer({ id: server.id })
      if (res.data?.res?.code === 400) {
        alert(res.data?.res?.message || t('agent.server.deleteError'))
        return
      }
      await fetchServers()
      setDeleteConfirm(null)
    } catch (e) {
      console.error(e)
    }
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingServer(null)
  }

  const handleFormSuccess = () => {
    handleFormClose()
    fetchServers()
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <h2 className={styles.title}>{t('agent.server.title')}</h2>
          <span className={styles.count}>{servers.length}</span>
        </div>
        <button className={styles.addButton} onClick={() => setShowForm(true)}>
          + {t('agent.server.register')}
        </button>
      </div>

      <div className={styles.content}>
        {isLoading ? (
          <div className={styles.skeletonList}>
            {[1, 2, 3].map(i => <div key={i} className={styles.skeleton} />)}
          </div>
        ) : servers.length === 0 ? (
          <div className={styles.empty}>
            <p className={styles.emptyTitle}>{t('agent.server.emptyTitle')}</p>
            <p className={styles.emptyDesc}>{t('agent.server.emptyDesc')}</p>
            <button className={styles.emptyButton} onClick={() => setShowForm(true)}>
              {t('agent.server.register')}
            </button>
          </div>
        ) : (
          <div className={styles.list}>
            {servers.map(server => (
              <ServerCard
                key={server.id}
                server={server}
                onEdit={() => handleEdit(server)}
                onDelete={() => setDeleteConfirm(server)}
              />
            ))}
          </div>
        )}
      </div>

      {deleteConfirm && (
        <div className={styles.modalOverlay} onClick={() => setDeleteConfirm(null)}>
          <div className={styles.confirmModal} onClick={e => e.stopPropagation()}>
            <p className={styles.confirmTitle}>{t('agent.server.deleteConfirmTitle')}</p>
            <p className={styles.confirmDesc}>
              {t('agent.server.deleteConfirmDesc', { name: deleteConfirm.name })}
            </p>
            <div className={styles.confirmButtons}>
              <button className={styles.cancelButton} onClick={() => setDeleteConfirm(null)}>
                {t('common.cancel')}
              </button>
              <button className={styles.deleteButton} onClick={() => handleDelete(deleteConfirm)}>
                {t('common.confirm')}
              </button>
            </div>
          </div>
        </div>
      )}

      {showForm && (
        <ServerFormModal
          server={editingServer}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  )
}
