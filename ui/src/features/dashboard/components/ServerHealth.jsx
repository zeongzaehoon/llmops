import Badge from '@/components/data-display/Badge'
import StatusDot from '@/components/data-display/StatusDot'
import styles from './ServerHealth.module.scss'

/**
 * Server health overview with status indicators and tool counts.
 * @param {Array} servers - MCP server list
 * @param {boolean} loading - Loading state
 */
export default function ServerHealth({ servers = [], loading = false }) {
  if (loading) {
    return (
      <div className={styles.container}>
        <h3 className={styles.heading}>Server Health</h3>
        <div className={styles.list}>
          {[1, 2, 3].map((i) => (
            <div key={i} className={styles.shimmerRow}>
              <div className={styles.shimmerBlock} style={{ width: '30%' }} />
              <div className={styles.shimmerBlock} style={{ width: '50%' }} />
              <div className={styles.shimmerBlock} style={{ width: '10%' }} />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (servers.length === 0) {
    return (
      <div className={styles.container}>
        <h3 className={styles.heading}>Server Health</h3>
        <p className={styles.empty}>No MCP servers registered yet.</p>
      </div>
    )
  }

  const maxTools = Math.max(...servers.map((s) => s.tools?.length || 0), 1)

  return (
    <div className={styles.container}>
      <h3 className={styles.heading}>Server Health</h3>
      <div className={styles.list}>
        {servers.map((server) => {
          const toolCount = server.tools?.length || 0
          const isLive = !!server.live
          const pct = maxTools > 0 ? (toolCount / maxTools) * 100 : 0

          return (
            <div key={server.name || server._id} className={styles.row}>
              <div className={styles.serverInfo}>
                <StatusDot status={isLive ? 'live' : 'offline'} size="sm" />
                <span className={styles.serverName}>{server.name}</span>
              </div>

              <div className={styles.barWrap}>
                <div
                  className={`${styles.bar} ${isLive ? styles.barLive : styles.barDown}`}
                  style={{ width: `${pct}%` }}
                />
              </div>

              <Badge variant={isLive ? 'live' : 'danger'}>
                {isLive ? 'Live' : 'Down'}
              </Badge>

              <span className={styles.toolCount}>{toolCount}t</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
