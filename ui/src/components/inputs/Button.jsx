import styles from './Button.module.scss'

/**
 * Button component.
 * @param {'primary'|'secondary'|'ghost'|'danger'} variant
 * @param {'sm'|'md'|'lg'} size
 * @param {boolean} loading
 * @param {boolean} disabled
 * @param {React.ReactNode} leftIcon
 */
export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  leftIcon,
  children,
  className = '',
  ...props
}) {
  return (
    <button
      className={`${styles.button} ${styles[variant]} ${styles[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className={styles.spinner} />}
      {!loading && leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}
      {children}
    </button>
  )
}
