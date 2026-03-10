import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import styles from './ServerCard.module.scss'

export default function ServerCard({ server, onEdit, onDelete }) {
  const { t } = useTranslation()
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader} onClick={() => setExpanded(!expanded)}>
        <div className={styles.left}>
          <span className={`${styles.dot} ${server.live ? styles.live : styles.dead}`} />
          <div className={styles.info}>
            <span className={styles.name}>{server.name}</span>
            <span className={styles.uri}>{server.uri}</span>
          </div>
        </div>
        <div className={styles.right}>
          <span className={styles.toolCount}>
            {server.tools?.length || 0} {t('agent.server.tools')}
          </span>
          <span className={`${styles.status} ${server.live ? styles.statusLive : styles.statusDead}`}>
            {server.live ? t('agent.server.live') : t('agent.server.offline')}
          </span>
          <div className={styles.actions}>
            <button className={styles.actionBtn} onClick={e => { e.stopPropagation(); onEdit(); }}>
              {t('agent.common.edit')}
            </button>
            <button className={`${styles.actionBtn} ${styles.deleteBtn}`} onClick={e => { e.stopPropagation(); onDelete(); }}>
              {t('agent.common.delete')}
            </button>
          </div>
          <span className={`${styles.arrow} ${expanded ? styles.arrowUp : ''}`}>&#9662;</span>
        </div>
      </div>

      {expanded && server.tools?.length > 0 && (
        <div className={styles.toolList}>
          {server.tools.map((tool, i) => (
            <div key={i} className={styles.toolItem}>
              <span className={styles.toolName}>{tool.toolName}</span>
              <span className={styles.toolDesc}>{tool.description}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
