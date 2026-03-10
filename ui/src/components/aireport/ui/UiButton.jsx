import { useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import styles from './UiButton.module.scss'

export default function UiButton({
  loading = false,
  disabled = false,
  primary = false,
  primary2 = false,
  size = 'normal',
  iconName,
  onClick: onClickProp,
  children
}) {
  const { i18n } = useTranslation()
  const [clicked, setClicked] = useState(false)

  const cssClass = [
    styles.uiBtn,
    primary && styles.primary,
    primary2 && styles.primary2,
    loading && styles.loading,
    disabled && styles.disabled,
    styles[`size--${size}`],
    iconName ? styles['use-icon'] : styles['no-icon']
  ]
    .filter(Boolean)
    .join(' ')

  const handleClick = useCallback(
    (event) => {
      if (!clicked) {
        setClicked(true)
        setTimeout(() => {
          setClicked(false)
        }, 500)
        if (disabled) {
          return
        }
        onClickProp?.(event)
      }
    },
    [clicked, disabled, onClickProp]
  )

  return (
    <button className={cssClass} disabled={disabled} onClick={handleClick}>
      {iconName && <i className={`${styles.icon} ${iconName}`} />}
      <span className={`${styles.text} ${i18n.language}`}>{children}</span>
      {loading && (
        <span className={styles['loading-circle']}>
          <svg x="0px" y="0px" viewBox="0 0 150 150">
            <circle className={styles['loading-inner']} cx="75" cy="75" r="60" />
          </svg>
        </span>
      )}
    </button>
  )
}
