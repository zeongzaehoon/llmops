import { useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { enrollMCPServer, updateMCPServer, getMCPServerTools } from '@/api/mcpApi'
import styles from './ServerFormModal.module.scss'

export default function ServerFormModal({ server, onClose, onSuccess }) {
  const { t } = useTranslation()
  const isEdit = !!server

  const [form, setForm] = useState({
    name: server?.name || '',
    uri: server?.uri || '',
    token: '',
    description: server?.description || ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [testResult, setTestResult] = useState(null) // null | 'testing' | 'success' | 'fail'
  const [testTools, setTestTools] = useState([])

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }))
    setTestResult(null)
  }

  const handleTest = useCallback(async () => {
    if (!form.uri) return
    setTestResult('testing')
    try {
      // For new server, we can't test via ID. For edit, use server ID.
      if (isEdit && server?.id) {
        const res = await getMCPServerTools({ id: server.id })
        const tools = res.data?.res?.data || []
        setTestTools(tools)
        setTestResult(tools.length > 0 ? 'success' : 'fail')
      } else {
        // For new servers, just validate URI format
        try {
          new URL(form.uri)
          setTestResult('success')
          setTestTools([])
        } catch {
          setTestResult('fail')
        }
      }
    } catch {
      setTestResult('fail')
      setTestTools([])
    }
  }, [form.uri, isEdit, server?.id])

  const handleSubmit = async () => {
    if (!form.name || !form.uri) return
    setIsSubmitting(true)
    try {
      if (isEdit) {
        const data = { id: server.id }
        if (form.name !== server.name) data.name = form.name
        if (form.uri !== server.uri) data.uri = form.uri
        if (form.description !== server.description) data.description = form.description
        await updateMCPServer(data)
      } else {
        await enrollMCPServer({
          name: form.name,
          uri: form.uri,
          token: form.token,
          description: form.description || undefined
        })
      }
      onSuccess()
    } catch (e) {
      console.error(e)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h3>{isEdit ? t('agent.server.editTitle') : t('agent.server.registerTitle')}</h3>
          <button className={styles.closeButton} onClick={onClose}>&times;</button>
        </div>

        <div className={styles.form}>
          <div className={styles.field}>
            <label>{t('agent.server.name')} *</label>
            <input
              value={form.name}
              onChange={e => handleChange('name', e.target.value)}
              placeholder={t('agent.server.namePlaceholder')}
            />
          </div>

          <div className={styles.field}>
            <label>{t('agent.server.uri')} *</label>
            <div className={styles.uriRow}>
              <input
                value={form.uri}
                onChange={e => handleChange('uri', e.target.value)}
                placeholder="http://mcp-server:8000/mcp"
              />
              <button
                className={`${styles.testButton} ${testResult === 'success' ? styles.testSuccess : ''} ${testResult === 'fail' ? styles.testFail : ''}`}
                onClick={handleTest}
                disabled={testResult === 'testing' || !form.uri}
              >
                {testResult === 'testing' ? '...' :
                 testResult === 'success' ? t('agent.server.connected') :
                 testResult === 'fail' ? t('agent.server.connectFail') :
                 t('agent.server.testConnection')}
              </button>
            </div>
          </div>

          {!isEdit && (
            <div className={styles.field}>
              <label>{t('agent.server.token')}</label>
              <input
                type="password"
                value={form.token}
                onChange={e => handleChange('token', e.target.value)}
                placeholder={t('agent.server.tokenPlaceholder')}
              />
            </div>
          )}

          <div className={styles.field}>
            <label>{t('agent.server.description')}</label>
            <textarea
              value={form.description}
              onChange={e => handleChange('description', e.target.value)}
              placeholder={t('agent.server.descPlaceholder')}
              rows={3}
            />
          </div>

          {testResult === 'success' && testTools.length > 0 && (
            <div className={styles.toolPreview}>
              <label>{t('agent.server.availableTools')} ({testTools.length})</label>
              <div className={styles.toolList}>
                {testTools.map((tool, i) => (
                  <div key={i} className={styles.toolItem}>
                    <span className={styles.toolName}>{tool.toolName}</span>
                    <span className={styles.toolDesc}>{tool.description}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onClose}>{t('common.cancel')}</button>
          <button
            className={styles.submitBtn}
            onClick={handleSubmit}
            disabled={isSubmitting || !form.name || !form.uri || (!isEdit && !form.token)}
          >
            {isSubmitting ? '...' : (isEdit ? t('agent.server.update') : t('agent.server.register'))}
          </button>
        </div>
      </div>
    </div>
  )
}
