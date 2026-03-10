import { useState } from 'react'
import Badge from '@/components/data-display/Badge'
import styles from './VersionTimeline.module.scss'

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' })
}

function getDeployBadge(status) {
  if (status === 'blue') return <Badge variant="production">Production</Badge>
  if (status === 'green') return <Badge variant="staging">Staging</Badge>
  return null
}

export default function VersionTimeline({
  versions = [],
  activeVersion,
  onSelectVersion,
  onShowDiff,
}) {
  const [diffPair, setDiffPair] = useState(null)

  const handleDiffClick = (oldVer, newVer) => {
    setDiffPair({ old: oldVer, new: newVer })
    onShowDiff?.(oldVer, newVer)
  }

  return (
    <div className={styles.timeline}>
      <h3 className={styles.title}>Version Timeline</h3>
      <div className={styles.list}>
        {versions.map((v, idx) => {
          const isActive = v.version === activeVersion
          const borderClass = v.deployStatus === 'blue'
            ? styles.borderBlue
            : v.deployStatus === 'green'
              ? styles.borderGreen
              : ''

          return (
            <div key={v.version}>
              <button
                className={`${styles.entry} ${isActive ? styles.active : ''} ${borderClass}`}
                onClick={() => onSelectVersion(v.version)}
              >
                <div className={styles.entryHeader}>
                  <span className={styles.version}>v{v.version}</span>
                  {getDeployBadge(v.deployStatus)}
                </div>
                <span className={styles.date}>{formatDate(v.regDate)}</span>
                {v.memo && <p className={styles.memo}>{v.memo}</p>}
              </button>

              {idx < versions.length - 1 && (
                <button
                  className={styles.diffLink}
                  onClick={() => handleDiffClick(versions[idx + 1].version, v.version)}
                >
                  Show diff: v{versions[idx + 1].version} vs v{v.version}
                </button>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
