import { useRef, useEffect } from 'react'
import styles from './ConfirmDialog.module.scss'

/**
 * Native <dialog> based confirm dialog.
 * @param {boolean} open
 * @param {string} title
 * @param {string} description
 * @param {string} confirmLabel
 * @param {string} cancelLabel
 * @param {'primary'|'danger'} variant
 * @param {function} onConfirm
 * @param {function} onCancel
 */
export default function ConfirmDialog({
  open,
  title = '확인',
  description = '',
  confirmLabel = '확인',
  cancelLabel = '취소',
  variant = 'primary',
  onConfirm,
  onCancel,
}) {
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
    onCancel?.()
  }

  return (
    <dialog ref={dialogRef} className={styles.dialog} onCancel={handleCancel}>
      <div className={styles.content}>
        <h3 className={styles.title}>{title}</h3>
        {description && <p className={styles.description}>{description}</p>}
        <div className={styles.actions}>
          <button className={`${styles.btn} ${styles.btnCancel}`} onClick={onCancel}>
            {cancelLabel}
          </button>
          <button
            className={`${styles.btn} ${styles.btnConfirm} ${styles[variant]}`}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </dialog>
  )
}
