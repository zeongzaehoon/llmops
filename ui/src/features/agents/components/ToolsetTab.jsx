import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import Card from '@/components/layout/Card'
import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import EmptyState from '@/components/feedback/EmptyState'
import ConfirmDialog from '@/components/feedback/ConfirmDialog'
import { useToolsetsByAgent, useDeleteToolset, useDeployToolset } from '@/hooks/queries/useToolsets'
import ToolsetCard from './ToolsetCard'
import styles from '../AgentDetailPage.module.scss'

export default function ToolsetTab({ agent }) {
  const navigate = useNavigate()
  const { data: agentToolsets = [] } = useToolsetsByAgent(agent)
  const deleteToolset = useDeleteToolset()
  const deployToolsetMutation = useDeployToolset()
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deployTarget, setDeployTarget] = useState(null)

  const liveToolset = useMemo(() => agentToolsets.find((t) => t.isService), [agentToolsets])

  const handleDeployToolset = () => {
    if (!deployTarget) return
    deployToolsetMutation.mutate(
      { id: deployTarget.id, agent: deployTarget.agent },
      {
        onSuccess: () => {
          toast.success('Toolset deployed')
          setDeployTarget(null)
        },
        onError: () => toast.error('Failed to deploy')
      }
    )
  }

  const handleDeleteToolset = () => {
    if (!deleteTarget) return
    deleteToolset.mutate(
      { id: deleteTarget.id },
      {
        onSuccess: () => {
          toast.success('Toolset deleted')
          setDeleteTarget(null)
        },
        onError: () => toast.error('Failed to delete')
      }
    )
  }

  return (
    <div className={styles.toolsetTab}>
      <div className={styles.toolsetHeader}>
        <Button
          size="sm"
          onClick={() => navigate(`/admin/agents/${encodeURIComponent(agent)}/toolset/new`)}
        >
          + New Toolset
        </Button>
      </div>

      {/* Live toolset summary */}
      {liveToolset && (
        <Card className={styles.liveToolsetCard}>
          <div className={styles.liveToolsetHeader}>
            <Badge variant="live">LIVE</Badge>
            <span className={styles.liveToolsetName}>{liveToolset.name}</span>
          </div>
          {liveToolset.mcpInfo?.length > 0 && (
            <div className={styles.liveToolsetMeta}>
              {liveToolset.mcpInfo.map((info, idx) => (
                <span key={idx} className={styles.liveToolsetServer}>
                  {info.serverName || info.serverId}: {info.tools?.length || 0} tools
                </span>
              ))}
            </div>
          )}
        </Card>
      )}

      {agentToolsets.length === 0 ? (
        <EmptyState
          title="No toolsets"
          description="Create a toolset to connect MCP tools to this agent"
          action={{
            label: '+ New Toolset',
            onClick: () => navigate(`/admin/agents/${encodeURIComponent(agent)}/toolset/new`)
          }}
        />
      ) : (
        <div className={styles.toolsetGrid}>
          {agentToolsets.map((toolset) => (
            <ToolsetCard
              key={toolset.id}
              toolset={toolset}
              onDeploy={setDeployTarget}
              onEdit={(t) =>
                navigate(
                  `/admin/agents/${encodeURIComponent(agent)}/toolset/${encodeURIComponent(t.id)}`
                )
              }
              onDelete={setDeleteTarget}
            />
          ))}
        </div>
      )}

      <ConfirmDialog
        open={!!deployTarget}
        title="Deploy Toolset"
        description={
          liveToolset
            ? `Replace live toolset "${liveToolset.name}" with "${deployTarget?.name}"?`
            : `Deploy "${deployTarget?.name}" to production?`
        }
        confirmLabel="Deploy"
        variant="primary"
        onConfirm={handleDeployToolset}
        onCancel={() => setDeployTarget(null)}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Toolset"
        description={`Delete "${deleteTarget?.name}"? This cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleDeleteToolset}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
