import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import PageHeader from '@/components/layout/PageHeader'
import Card from '@/components/layout/Card'
import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import SearchInput from '@/components/inputs/SearchInput'
import EmptyState from '@/components/feedback/EmptyState'
import ConfirmDialog from '@/components/feedback/ConfirmDialog'
import { useGraphs, useDeleteGraph } from '@/hooks/queries/useGraphs'
import styles from './GraphHubPage.module.scss'

function MiniGraphPreview({ type = 'linear' }) {
  const previewMap = {
    linear: (
      <svg viewBox="0 0 120 40" className={styles.preview}>
        <circle cx="20" cy="20" r="6" fill="var(--sol-brand-primary)" />
        <line x1="26" y1="20" x2="54" y2="20" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <circle cx="60" cy="20" r="6" fill="var(--sol-brand-primary)" />
        <line x1="66" y1="20" x2="94" y2="20" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <circle cx="100" cy="20" r="6" fill="var(--sol-brand-primary)" />
      </svg>
    ),
    debate: (
      <svg viewBox="0 0 120 40" className={styles.preview}>
        <circle cx="60" cy="8" r="6" fill="var(--sol-status-warning)" />
        <line x1="54" y1="12" x2="30" y2="28" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <line x1="66" y1="12" x2="90" y2="28" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <circle cx="26" cy="32" r="6" fill="var(--sol-status-warning)" />
        <circle cx="94" cy="32" r="6" fill="var(--sol-status-warning)" />
      </svg>
    ),
    parallel: (
      <svg viewBox="0 0 120 40" className={styles.preview}>
        <circle cx="20" cy="20" r="6" fill="var(--sol-status-success)" />
        <line x1="26" y1="20" x2="44" y2="10" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <line x1="26" y1="20" x2="44" y2="20" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <line x1="26" y1="20" x2="44" y2="30" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <circle cx="50" cy="10" r="5" fill="var(--sol-status-success)" />
        <circle cx="50" cy="20" r="5" fill="var(--sol-status-success)" />
        <circle cx="50" cy="30" r="5" fill="var(--sol-status-success)" />
        <line x1="55" y1="10" x2="74" y2="20" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <line x1="55" y1="20" x2="74" y2="20" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <line x1="55" y1="30" x2="74" y2="20" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <circle cx="80" cy="20" r="6" fill="var(--sol-status-success)" />
      </svg>
    ),
    router: (
      <svg viewBox="0 0 120 40" className={styles.preview}>
        <rect x="14" y="12" width="16" height="16" rx="3" fill="var(--sol-brand-primary)" />
        <line x1="30" y1="20" x2="48" y2="10" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <line x1="30" y1="20" x2="48" y2="30" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <circle cx="54" cy="10" r="5" fill="var(--sol-brand-primary)" />
        <circle cx="54" cy="30" r="5" fill="var(--sol-brand-primary)" />
        <line x1="59" y1="10" x2="74" y2="10" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <line x1="59" y1="30" x2="74" y2="30" stroke="var(--sol-border-primary)" strokeWidth="2" />
        <circle cx="80" cy="10" r="5" fill="var(--sol-brand-primary)" />
        <circle cx="80" cy="30" r="5" fill="var(--sol-brand-primary)" />
      </svg>
    ),
  }
  return previewMap[type] || previewMap.linear
}

export default function GraphHubPage() {
  const navigate = useNavigate()
  const { data: graphs = [], isLoading } = useGraphs()
  const deleteGraph = useDeleteGraph()

  const [search, setSearch] = useState('')
  const [deleteTarget, setDeleteTarget] = useState(null)

  const filtered = graphs.filter(
    (g) =>
      g.name?.toLowerCase().includes(search.toLowerCase()) ||
      g.type?.toLowerCase().includes(search.toLowerCase()),
  )

  const handleDelete = () => {
    if (!deleteTarget) return
    deleteGraph.mutate(
      { name: deleteTarget.name },
      {
        onSuccess: () => {
          toast.success(`Graph "${deleteTarget.name}" deleted`)
          setDeleteTarget(null)
        },
        onError: () => toast.error('Failed to delete graph'),
      },
    )
  }

  return (
    <div className={styles.page}>
      <PageHeader
        title="Graphs"
        description="Multi-agent workflow graphs using agents"
        actions={
          <Button size="sm" onClick={() => navigate('/admin/graphs/new')}>
            + New Graph
          </Button>
        }
      />

      {!isLoading && graphs.length === 0 ? (
        <EmptyState
          title="No graphs created"
          description="Design your first multi-agent graph workflow."
          action={{
            label: '+ New Graph',
            onClick: () => navigate('/admin/graphs/new'),
          }}
        />
      ) : (
        <>
          <div className={styles.toolbar}>
            <SearchInput placeholder="Search graphs..." value={search} onChange={setSearch} />
          </div>

          <div className={styles.grid}>
            {filtered.map((graph) => (
              <Card key={graph.name} hoverable className={styles.card}>
                <div className={styles.cardHeader}>
                  <span className={styles.graphName}>{graph.name}</span>
                  <Badge variant="info">{graph.type || 'linear'}</Badge>
                </div>

                {graph.description && (
                  <p className={styles.description}>{graph.description}</p>
                )}

                <div className={styles.previewWrapper}>
                  <MiniGraphPreview type={graph.type} />
                </div>

                <div className={styles.agentList}>
                  {graph.agents?.map((a, i) => (
                    <span key={i} className={styles.agentTag}>{a.name || `Agent ${i + 1}`}</span>
                  ))}
                </div>

                <div className={styles.actions}>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => navigate(`/admin/graphs/${encodeURIComponent(graph.name)}`)}
                  >
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => navigate(`/admin/playground/${encodeURIComponent(graph.name)}`)}
                  >
                    Test
                  </Button>
                  <Button size="sm" variant="danger" onClick={() => setDeleteTarget(graph)}>
                    Delete
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Graph"
        description={`Are you sure you want to delete "${deleteTarget?.name}"? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
