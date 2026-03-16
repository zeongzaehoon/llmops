import Card from '@/components/layout/Card'
import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import styles from './ToolsetCard.module.scss'

export default function ToolsetCard({ toolset, onDeploy, onEdit, onDelete }) {
  const isLive = !!toolset.isService

  return (
    <Card hoverable className={styles.card}>
      <div className={styles.header}>
        <span className={styles.name}>{toolset.name}</span>
        {isLive ? (
          <Badge variant="live" className={styles.liveBadge}>LIVE</Badge>
        ) : (
          <Badge variant="draft">Draft</Badge>
        )}
      </div>

      {toolset.description && (
        <p className={styles.description}>{toolset.description}</p>
      )}

      {toolset.mcpInfo?.length > 0 && (
        <div className={styles.servers}>
          <span className={styles.serversLabel}>Servers & Tools:</span>
          {toolset.mcpInfo.map((info, idx) => (
            <div key={info.serverId || idx} className={styles.serverItem}>
              <span className={styles.serverName}>{info.serverName || info.serverId}:</span>
              <div className={styles.tools}>
                {info.tools?.map((tool) => (
                  <span key={tool} className={styles.toolTag}>
                    {tool}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className={styles.actions}>
        {!isLive && (
          <Button size="sm" variant="primary" onClick={() => onDeploy?.(toolset)}>
            Deploy
          </Button>
        )}
        <Button size="sm" variant="ghost" onClick={() => onEdit?.(toolset)}>
          Edit
        </Button>
        <Button size="sm" variant="danger" onClick={() => onDelete?.(toolset)}>
          Delete
        </Button>
      </div>
    </Card>
  )
}
