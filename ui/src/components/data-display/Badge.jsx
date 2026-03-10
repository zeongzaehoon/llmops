import styles from './Badge.module.scss'

/**
 * Badge component.
 * @param {'live'|'draft'|'staging'|'production'|'count'|'info'|'danger'} variant
 * @param {React.ReactNode} children
 */
export default function Badge({ variant = 'info', children, className = '' }) {
  return (
    <span className={`${styles.badge} ${styles[variant] || ''} ${className}`}>
      {children}
    </span>
  )
}
