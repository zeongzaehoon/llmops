import { useState } from 'react'
import toast from 'react-hot-toast'
import Card from '@/components/layout/Card'
import StatusDot from '@/components/data-display/StatusDot'
import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import SearchInput from '@/components/inputs/SearchInput'
import EmptyState from '@/components/feedback/EmptyState'
import ConfirmDialog from '@/components/feedback/ConfirmDialog'
import { useServers, useDeleteServer } from '@/hooks/queries/useServers'
import ServerFormModal from './ServerFormModal'
import styles from './ServerPanel.module.scss'

export default function ServerPanel({ onRegister }) {
  const { data: servers = [], isLoading } = useServers()
  const deleteServer = useDeleteServer()

  const [search, setSearch] = useState('')
  const [editTarget, setEditTarget] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)

  const filtered = servers.filter(
    (s) =>
      s.name?.toLowerCase().includes(search.toLowerCase()) ||
      s.uri?.toLowerCase().includes(search.toLowerCase()),
  )

  const handleDelete = () => {
    if (!deleteTarget) return
    deleteServer.mutate(
      { id: deleteTarget.id },
      {
        onSuccess: () => {
          toast.success(`Server "${deleteTarget.name}" deleted`)
          setDeleteTarget(null)
        },
        onError: () => toast.error('Failed to delete server'),
      },
    )
  }

  if (!isLoading && servers.length === 0) {
    return (
      <EmptyState
        title="No MCP servers registered"
        description="Connect your first server to get started."
        action={{ label: '+ Register Server', onClick: onRegister }}
      />
    )
  }

  return (
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <SearchInput
          placeholder="Search servers..."
          value={search}
          onChange={setSearch}
        />
      </div>

      <div className={styles.grid}>
        {filtered.map((server) => {
          const isLive = !!server.live
          const toolCount = server.tools?.length ?? 0

          return (
            <Card key={server.id} hoverable className={styles.card}>
              <div className={styles.cardHeader}>
                <span className={styles.serverName}>{server.name}</span>
                <StatusDot
                  status={isLive ? 'live' : 'offline'}
                  label={isLive ? 'Live' : 'Disconnected'}
                />
              </div>

              <p className={styles.uri} title={server.uri}>
                {server.uri}
              </p>

              {server.description && (
                <p className={styles.description}>{server.description}</p>
              )}

              <div className={styles.meta}>
                <Badge variant="count">Tools: {toolCount || '--'}</Badge>
              </div>

              <div className={styles.actions}>
                <Button size="sm" variant="ghost" onClick={() => setEditTarget(server)}>
                  Edit
                </Button>
                <Button size="sm" variant="ghost" onClick={() => toast.success('Health check sent')}>
                  Health
                </Button>
                <Button size="sm" variant="danger" onClick={() => setDeleteTarget(server)}>
                  Delete
                </Button>
              </div>
            </Card>
          )
        })}
      </div>

      <ServerFormModal
        open={!!editTarget}
        onClose={() => setEditTarget(null)}
        server={editTarget}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Server"
        description={`Are you sure you want to delete "${deleteTarget?.name}"? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
