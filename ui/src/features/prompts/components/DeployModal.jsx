import { useState, useRef } from 'react'
import Modal from '@/components/overlay/Modal'
import Button from '@/components/inputs/Button'
import styles from './DeployModal.module.scss'

export default function DeployModal({
  open,
  onClose,
  onConfirm,
  type = 'deploy',
  loading = false,
}) {
  const [password, setPassword] = useState('')
  const badgeRef = useRef(null)

  const isDeploy = type === 'deploy'
  const title = isDeploy ? 'Deploy to Production' : 'Rollback Production'
  const warning = isDeploy
    ? 'This will promote the current staging version to production. This action affects live traffic.'
    : 'This will revert production to the previous version. This action affects live traffic.'

  const handleConfirm = () => {
    if (!password.trim()) return
    onConfirm?.(password, () => {
      if (badgeRef.current) {
        badgeRef.current.classList.add(styles.bounce)
        setTimeout(() => {
          badgeRef.current?.classList.remove(styles.bounce)
        }, 600)
      }
    })
    setPassword('')
  }

  const handleClose = () => {
    setPassword('')
    onClose?.()
  }

  return (
    <Modal open={open} onClose={handleClose} size="sm">
      <div className={styles.modal}>
        <div className={styles.header}>
          <h3 className={styles.title}>{title}</h3>
          <span
            ref={badgeRef}
            className={`${styles.badge} ${isDeploy ? styles.deployBadge : styles.rollbackBadge}`}
          >
            {isDeploy ? 'DEPLOY' : 'ROLLBACK'}
          </span>
        </div>

        <p className={styles.warning}>{warning}</p>

        <div className={styles.field}>
          <label className={styles.label} htmlFor="deploy-password">
            Enter password to confirm
          </label>
          <input
            id="deploy-password"
            type="password"
            className={styles.input}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            onKeyDown={(e) => e.key === 'Enter' && handleConfirm()}
            autoFocus
          />
        </div>

        <div className={styles.actions}>
          <Button variant="ghost" size="md" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            variant={isDeploy ? 'primary' : 'danger'}
            size="md"
            loading={loading}
            disabled={!password.trim()}
            onClick={handleConfirm}
          >
            {title}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
