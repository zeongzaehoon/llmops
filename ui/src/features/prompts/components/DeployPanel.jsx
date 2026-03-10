import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import styles from './DeployPanel.module.scss'

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

export default function DeployPanel({
  deployInfo,
  onDeploy,
  onRollback,
}) {
  const blue = deployInfo?.blue
  const green = deployInfo?.green

  return (
    <div className={styles.panel}>
      <h3 className={styles.title}>Deploy Status</h3>

      <div className={styles.columns}>
        <div className={`${styles.column} ${styles.blue}`}>
          <div className={styles.columnHeader}>
            <span className={styles.label}>BLUE</span>
            <Badge variant="production">Production</Badge>
          </div>
          <div className={styles.info}>
            <span className={styles.version}>
              {blue?.version != null ? `v${blue.version}` : 'Not deployed'}
            </span>
            <span className={styles.date}>{formatDate(blue?.regDate)}</span>
          </div>
        </div>

        <div className={`${styles.column} ${styles.green}`}>
          <div className={styles.columnHeader}>
            <span className={styles.label}>GREEN</span>
            <Badge variant="staging">Staging</Badge>
          </div>
          <div className={styles.info}>
            <span className={styles.version}>
              {green?.version != null ? `v${green.version}` : 'Not deployed'}
            </span>
            <span className={styles.date}>{formatDate(green?.regDate)}</span>
          </div>
        </div>
      </div>

      <div className={styles.actions}>
        <Button variant="primary" size="md" onClick={onDeploy}>
          Deploy to Production
        </Button>
        <Button variant="danger" size="md" onClick={onRollback}>
          Rollback Production
        </Button>
      </div>
    </div>
  )
}
