import styles from './Card.module.scss'

/**
 * Card container component.
 * @param {React.ReactNode} children
 * @param {string} className
 * @param {function} onClick
 * @param {boolean} hoverable
 */
export default function Card({ children, className = '', onClick, hoverable = false }) {
  return (
    <div
      className={`${styles.card} ${hoverable ? styles.hoverable : ''} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}
