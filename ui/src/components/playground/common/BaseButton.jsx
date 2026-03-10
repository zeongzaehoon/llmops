import styles from './BaseButton.module.scss'

const BaseButton = ({
  color = 'primary',
  size = 'small',
  style,
  disabled = false,
  onClick,
  children
}) => {
  return (
    <button
      className={`${styles.button} ${styles[`button-${size}`]} ${styles[`button-${color}`]}`}
      style={style}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

export default BaseButton
