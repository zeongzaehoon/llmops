import Badge from '@/components/data-display/Badge'
import styles from './DeployStatus.module.scss'

/**
 * Blue-Green deployment overview table.
 * @param {Array} deployList - Deployment entries with agent, version, deployStatus
 * @param {boolean} loading - Loading state
 */
export default function DeployStatus({ deployList = [], loading = false }) {
  if (loading) {
    return (
      <div className={styles.container}>
        <h3 className={styles.heading}>Deployment Status</h3>
        <div className={styles.shimmerTable}>
          {[1, 2, 3].map((i) => (
            <div key={i} className={styles.shimmerRow}>
              <div className={styles.shimmerBlock} style={{ width: '25%' }} />
              <div className={styles.shimmerBlock} style={{ width: '30%' }} />
              <div className={styles.shimmerBlock} style={{ width: '30%' }} />
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Group deploy entries by category
  const grouped = deployList.reduce((acc, item) => {
    const cat = item.agent || 'unknown'
    if (!acc[cat]) acc[cat] = { blue: null, green: null }

    const status = (item.deployStatus || '').toLowerCase()
    if (status === 'blue' || status === 'production' || status === 'live') {
      acc[cat].blue = item
    } else if (status === 'green' || status === 'staging' || status === 'staged') {
      acc[cat].green = item
    }

    return acc
  }, {})

  const categories = Object.keys(grouped)

  if (categories.length === 0) {
    return (
      <div className={styles.container}>
        <h3 className={styles.heading}>Deployment Status</h3>
        <p className={styles.empty}>No deployments found.</p>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <h3 className={styles.heading}>Deployment Status</h3>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.thCategory}>Category</th>
              <th className={styles.thBlue}>Blue (Production)</th>
              <th className={styles.thGreen}>Green (Staging)</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((cat) => {
              const { blue, green } = grouped[cat]
              return (
                <tr key={cat}>
                  <td className={styles.tdCategory}>{cat}</td>
                  <td className={styles.tdBlue}>
                    {blue ? (
                      <span className={styles.deployCell}>
                        <span className={styles.version}>v{blue.version || '?'}</span>
                        <Badge variant="live">live</Badge>
                      </span>
                    ) : (
                      <span className={styles.noEntry}>&mdash;</span>
                    )}
                  </td>
                  <td className={styles.tdGreen}>
                    {green ? (
                      <span className={styles.deployCell}>
                        <span className={styles.version}>v{green.version || '?'}</span>
                        <Badge variant="staging">staged</Badge>
                      </span>
                    ) : (
                      <span className={styles.noEntry}>&mdash;</span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
