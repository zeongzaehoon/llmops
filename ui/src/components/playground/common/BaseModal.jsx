import { useState, useEffect, useRef } from 'react'
import loadingAnim from '@/assets/anim-loading.svg'
import styles from './BaseModal.module.scss'

const BaseModal = ({
  isLoading = false,
  timeOut,
  outsideDisabled = true,
  onClose,
  title,
  children
}) => {
  const [progressWidth, setProgressWidth] = useState(100)
  const intervalRef = useRef(null)

  useEffect(() => {
    if (timeOut) {
      const totalTime = timeOut
      const intervalTime = 100
      const step = 100 / (totalTime / intervalTime)

      intervalRef.current = setInterval(() => {
        setProgressWidth((prev) => {
          const next = prev - step
          if (next <= 0) {
            clearInterval(intervalRef.current)
            onClose?.()
            return 0
          }
          return next
        })
      }, intervalTime)

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
        }
      }
    }
  }, [timeOut, onClose])

  const wrapperClassName = `${styles['modal-wrapper']} ${outsideDisabled ? styles['outside-disabled'] : ''}`

  return (
    <div className={wrapperClassName}>
      {isLoading ? (
        <img className={styles.loading} src={loadingAnim} alt="loading" />
      ) : (
        <div className={styles['modal-viewer']}>
          {timeOut && (
            <div
              className={styles['progress-bar']}
              style={{ width: `${progressWidth}%` }}
            />
          )}
          {title && (
            <div className={styles['modal-viewer-header']}>{title}</div>
          )}
          {children}
          {!timeOut && (
            <button
              className={styles['modal-viewer-closeBtn']}
              onClick={() => onClose?.()}
            >
              &times;
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default BaseModal
