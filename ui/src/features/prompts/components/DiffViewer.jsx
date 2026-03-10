import { useMemo } from 'react'
import Modal from '@/components/overlay/Modal'
import styles from './DiffViewer.module.scss'

function computeDiff(oldText, newText) {
  const oldLines = (oldText || '').split('\n')
  const newLines = (newText || '').split('\n')
  const maxLen = Math.max(oldLines.length, newLines.length)

  const result = []
  for (let i = 0; i < maxLen; i++) {
    const oldLine = i < oldLines.length ? oldLines[i] : undefined
    const newLine = i < newLines.length ? newLines[i] : undefined
    const changed = oldLine !== newLine
    result.push({ lineNum: i + 1, oldLine, newLine, changed })
  }
  return result
}

export default function DiffViewer({ open, onClose, oldVersion, newVersion, oldText, newText }) {
  const diff = useMemo(() => computeDiff(oldText, newText), [oldText, newText])

  return (
    <Modal open={open} onClose={onClose} size="lg">
      <div className={styles.viewer}>
        <div className={styles.header}>
          <h3 className={styles.title}>
            Diff: v{oldVersion} vs v{newVersion}
          </h3>
          <button className={styles.closeBtn} onClick={onClose}>
            &times;
          </button>
        </div>

        <div className={styles.diffContainer}>
          <div className={styles.pane}>
            <div className={styles.paneHeader}>v{oldVersion} (old)</div>
            <div className={styles.paneBody}>
              {diff.map((row) => (
                <div
                  key={`old-${row.lineNum}`}
                  className={`${styles.line} ${row.changed && row.oldLine != null ? styles.removed : ''}`}
                >
                  <span className={styles.lineNum}>{row.oldLine != null ? row.lineNum : ''}</span>
                  <span className={styles.lineText}>{row.oldLine ?? ''}</span>
                </div>
              ))}
            </div>
          </div>

          <div className={styles.pane}>
            <div className={styles.paneHeader}>v{newVersion} (new)</div>
            <div className={styles.paneBody}>
              {diff.map((row) => (
                <div
                  key={`new-${row.lineNum}`}
                  className={`${styles.line} ${row.changed && row.newLine != null ? styles.added : ''}`}
                >
                  <span className={styles.lineNum}>{row.newLine != null ? row.lineNum : ''}</span>
                  <span className={styles.lineText}>{row.newLine ?? ''}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Modal>
  )
}
