import styles from './StatusDot.module.scss'

/**
 * Status dot indicator with optional label.
 * @param {'live'|'offline'|'warning'} status
 * @param {'sm'|'md'} size
 * @param {string} label
 */
export default function StatusDot({ status = 'offline', size = 'md', label }) {
  return (
    <span className={styles.container}>
      <span className={`${styles.dot} ${styles[size]} ${styles[status]}`} />
      {label && <span className={styles.label}>{label}</span>}
    </span>
  )
}
