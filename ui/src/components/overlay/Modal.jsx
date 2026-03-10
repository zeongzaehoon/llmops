import { useRef, useEffect } from 'react'
import styles from './Modal.module.scss'

/**
 * Native <dialog> based modal.
 * @param {boolean} open
 * @param {function} onClose
 * @param {'sm'|'md'|'lg'} size
 */
export default function Modal({ open, onClose, size = 'md', children }) {
  const dialogRef = useRef(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return

    if (open && !dialog.open) {
      dialog.showModal()
    } else if (!open && dialog.open) {
      dialog.close()
    }
  }, [open])

  const handleCancel = (e) => {
    e.preventDefault()
    onClose?.()
  }

  const handleBackdropClick = (e) => {
    if (e.target === dialogRef.current) {
      onClose?.()
    }
  }

  return (
    <dialog
      ref={dialogRef}
      className={`${styles.dialog} ${styles[size]}`}
      onCancel={handleCancel}
      onClick={handleBackdropClick}
    >
      <div className={styles.content} onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </dialog>
  )
}
