import { useState } from 'react'
import Card from '@/components/layout/Card'
import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import EmptyState from '@/components/feedback/EmptyState'
import ConfirmDialog from '@/components/feedback/ConfirmDialog'
import styles from './ResultList.module.scss'

function getScoreVariant(score) {
  if (score >= 0.9) return 'success'
  if (score >= 0.7) return 'warning'
  return 'danger'
}

function getScoreClass(score) {
  if (score >= 0.9) return styles.scoreHigh
  if (score >= 0.7) return styles.scoreMid
  return styles.scoreLow
}

export default function ResultList({ results = [], onDelete, isDeleting = false }) {
  const [expandedId, setExpandedId] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)

  const handleToggleExpand = (id) => {
    setExpandedId((prev) => (prev === id ? null : id))
  }

  const handleConfirmDelete = () => {
    if (deleteTarget) {
      onDelete?.(deleteTarget)
      setDeleteTarget(null)
    }
  }

  if (results.length === 0) {
    return (
      <EmptyState
        title="No results"
        description="Run a search query to find matching vectors"
      />
    )
  }

  return (
    <>
      <div className={styles.list}>
        {results.map((result, idx) => {
          const id = result.id || `result-${idx}`
          const isExpanded = expandedId === id

          return (
            <Card key={id} className={styles.resultCard}>
              <div className={styles.cardHeader}>
                <div className={styles.headerLeft}>
                  <span className={`${styles.score} ${getScoreClass(result.score)}`}>
                    {(result.score ?? 0).toFixed(4)}
                  </span>
                  <span className={styles.vectorId}>{id}</span>
                </div>
                <Button
                  variant="danger"
                  size="sm"
                  loading={isDeleting}
                  onClick={() => setDeleteTarget(id)}
                >
                  Delete
                </Button>
              </div>
              <div
                className={`${styles.content} ${isExpanded ? styles.expanded : ''}`}
                onClick={() => handleToggleExpand(id)}
              >
                <p className={styles.text}>
                  {result.text || result.content || result.metadata?.text || '(no content)'}
                </p>
              </div>
              {!isExpanded && (
                <button
                  className={styles.expandBtn}
                  onClick={() => handleToggleExpand(id)}
                >
                  Show more
                </button>
              )}
              {result.metadata && Object.keys(result.metadata).length > 0 && (
                <div className={styles.metadata}>
                  <span className={styles.metaLabel}>Metadata</span>
                  <pre className={styles.metaCode}>
                    <code>{JSON.stringify(result.metadata, null, 2)}</code>
                  </pre>
                </div>
              )}
            </Card>
          )
        })}
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Vector"
        description={`Are you sure you want to delete vector "${deleteTarget}"?`}
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </>
  )
}
