import { useState } from 'react'
import styles from './VersionTimeline.module.scss'

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

export default function VersionTimeline({
  versions = [],
  activeVersion,
  onSelectVersion,
  onShowDiff,
}) {
  const [diffPair, setDiffPair] = useState(null)
  const total = versions.length

  const handleDiffClick = (oldId, newId) => {
    setDiffPair({ old: oldId, new: newId })
    onShowDiff?.(oldId, newId)
  }

  return (
    <div className={styles.timeline}>
      <h3 className={styles.title}>Version Timeline</h3>
      <div className={styles.list}>
        {versions.map((v, idx) => {
          const isActive = v.id === activeVersion
          const versionNumber = total - idx

          return (
            <div key={v.id}>
              <button
                className={`${styles.entry} ${isActive ? styles.active : ''}`}
                onClick={() => onSelectVersion(v.id)}
              >
                <div className={styles.entryHeader}>
                  <span className={styles.version}>v{versionNumber}</span>
                </div>
                <span className={styles.date}>{formatDate(v.date)}</span>
                {v.memo && <p className={styles.memo}>{v.memo}</p>}
              </button>

              {idx < versions.length - 1 && (
                <button
                  className={styles.diffLink}
                  onClick={() => handleDiffClick(versions[idx + 1].id, v.id)}
                >
                  Show diff: v{total - idx - 1} vs v{versionNumber}
                </button>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
