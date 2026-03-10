import styles from './Tabs.module.scss'

/**
 * Tab bar component.
 * @param {Array<{key: string, label: string, count?: number}>} items
 * @param {string} activeKey
 * @param {function} onChange
 */
export default function Tabs({ items = [], activeKey, onChange }) {
  return (
    <div className={styles.tabs}>
      {items.map((item) => (
        <button
          key={item.key}
          className={`${styles.tab} ${activeKey === item.key ? styles.active : ''}`}
          onClick={() => onChange?.(item.key)}
        >
          {item.label}
          {item.count != null && <span className={styles.count}>{item.count}</span>}
        </button>
      ))}
    </div>
  )
}
