import { useMemo, useState } from 'react'
import SearchInput from '@/components/inputs/SearchInput'
import styles from './HistoryList.module.scss'

function groupByDate(items) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const weekAgo = new Date(today)
  weekAgo.setDate(weekAgo.getDate() - 7)

  const groups = {
    Today: [],
    Yesterday: [],
    'This Week': [],
    Older: [],
  }

  items.forEach((item) => {
    const date = new Date(item.regDate || item.createdAt || item.timestamp)
    if (date >= today) {
      groups.Today.push(item)
    } else if (date >= yesterday) {
      groups.Yesterday.push(item)
    } else if (date >= weekAgo) {
      groups['This Week'].push(item)
    } else {
      groups.Older.push(item)
    }
  })

  return Object.entries(groups).filter(([, items]) => items.length > 0)
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

export default function HistoryList({ items = [], selectedId, onSelect }) {
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    if (!search.trim()) return items
    const q = search.toLowerCase()
    return items.filter(
      (item) =>
        item.question?.toLowerCase().includes(q) ||
        item.ask?.toLowerCase().includes(q) ||
        item.answer?.toLowerCase().includes(q),
    )
  }, [items, search])

  const grouped = useMemo(() => groupByDate(filtered), [filtered])

  return (
    <div className={styles.container}>
      <div className={styles.searchWrap}>
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search conversations..."
        />
      </div>

      <div className={styles.list}>
        {grouped.length === 0 ? (
          <div className={styles.empty}>No conversations found</div>
        ) : (
          grouped.map(([label, groupItems]) => (
            <div key={label} className={styles.group}>
              <div className={styles.groupLabel}>{label}</div>
              {groupItems.map((item) => {
                const id = item._id || item.ask_id || item.id
                const isActive = id === selectedId
                const question = item.question || item.ask || '(no question)'
                const time = formatTime(item.regDate || item.createdAt)
                const rating = item.rating

                return (
                  <button
                    key={id}
                    className={`${styles.item} ${isActive ? styles.active : ''}`}
                    onClick={() => onSelect(item)}
                  >
                    <span className={styles.question}>{question}</span>
                    <div className={styles.meta}>
                      <span className={styles.time}>{time}</span>
                      {rating != null && (
                        <span className={styles.rating}>
                          {rating > 0 ? '+' : ''}{rating}
                        </span>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
