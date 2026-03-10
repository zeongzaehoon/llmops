import { useMemo } from 'react'
import styles from './HistorySidebar.module.scss'

/**
 * Group history items by date: Today, Yesterday, Older.
 */
function groupByDate(items) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const groups = { Today: [], Yesterday: [], Older: [] }

  for (const item of items) {
    const date = new Date(item.regDate || item.timestamp || 0)
    if (date >= today) {
      groups.Today.push(item)
    } else if (date >= yesterday) {
      groups.Yesterday.push(item)
    } else {
      groups.Older.push(item)
    }
  }

  return Object.entries(groups).filter(([, items]) => items.length > 0)
}

/**
 * Extract the first user question from a history entry.
 */
function getPreview(item) {
  return item.question || item.ask || item.content || 'Untitled conversation'
}

export default function HistorySidebar({
  history = [],
  collapsed,
  onToggle,
  activeId,
  onSelect,
}) {
  const grouped = useMemo(() => groupByDate(history), [history])

  if (collapsed) {
    return (
      <button
        className={styles.expandBtn}
        onClick={onToggle}
        title="Show history"
      >
        &#x25B6;
      </button>
    )
  }

  return (
    <div className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
      <div className={styles.sidebarHeader}>
        <span className={styles.sidebarTitle}>Chat History</span>
        <button
          className={styles.collapseBtn}
          onClick={onToggle}
          title="Hide history"
        >
          &#x25C0;
        </button>
      </div>

      <div className={styles.historyList}>
        {grouped.length === 0 ? (
          <div className={styles.emptyHistory}>No conversations yet</div>
        ) : (
          grouped.map(([label, items]) => (
            <div key={label} className={styles.dateGroup}>
              <div className={styles.dateLabel}>{label}</div>
              {items.map((item) => (
                <button
                  key={item._id || item.ask_id || item.id}
                  className={`${styles.historyItem} ${
                    activeId === (item._id || item.ask_id) ? styles.active : ''
                  }`}
                  onClick={() => onSelect(item)}
                  title={getPreview(item)}
                >
                  {getPreview(item)}
                </button>
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
