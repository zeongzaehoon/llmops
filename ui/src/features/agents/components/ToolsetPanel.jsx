import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import SearchInput from '@/components/inputs/SearchInput'
import EmptyState from '@/components/feedback/EmptyState'
import ConfirmDialog from '@/components/feedback/ConfirmDialog'
import { useToolsets, useDeleteToolset, useDeployToolset } from '@/hooks/queries/useToolsets'
import ToolsetCard from './ToolsetCard'
import styles from './ToolsetPanel.module.scss'

export default function ToolsetPanel() {
  const navigate = useNavigate()
  const { data: toolsets = [], isLoading } = useToolsets()
  const deleteToolset = useDeleteToolset()
  const deployToolset = useDeployToolset()

  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deployTarget, setDeployTarget] = useState(null)

  const categories = useMemo(() => {
    const set = new Set(toolsets.map((t) => t.agent).filter(Boolean))
    return Array.from(set).sort()
  }, [toolsets])

  const filtered = useMemo(() => {
    let result = toolsets
    if (activeCategory) {
      result = result.filter((t) => t.agent === activeCategory)
    }
    if (search) {
      const q = search.toLowerCase()
      result = result.filter(
        (t) => t.name?.toLowerCase().includes(q) || t.agent?.toLowerCase().includes(q),
      )
    }
    return result
  }, [toolsets, activeCategory, search])

  const handleDeploy = () => {
    if (!deployTarget) return
    deployToolset.mutate(
      { name: deployTarget.name, agent: deployTarget.agent },
      {
        onSuccess: () => {
          toast.success(`Toolset "${deployTarget.name}" deployed`)
          setDeployTarget(null)
        },
        onError: () => toast.error('Failed to deploy toolset'),
      },
    )
  }

  const handleDelete = () => {
    if (!deleteTarget) return
    deleteToolset.mutate(
      { name: deleteTarget.name, agent: deleteTarget.agent },
      {
        onSuccess: () => {
          toast.success(`Toolset "${deleteTarget.name}" deleted`)
          setDeleteTarget(null)
        },
        onError: () => toast.error('Failed to delete toolset'),
      },
    )
  }

  if (!isLoading && toolsets.length === 0) {
    return (
      <EmptyState
        title="No toolsets created"
        description="Build your first agent toolset to orchestrate MCP tools."
        action={{
          label: '+ New Agent',
          onClick: () => navigate('/admin/agents'),
        }}
      />
    )
  }

  return (
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <SearchInput placeholder="Search toolsets..." value={search} onChange={setSearch} />
      </div>

      {categories.length > 0 && (
        <div className={styles.chips}>
          <button
            className={`${styles.chip} ${!activeCategory ? styles.chipActive : ''}`}
            onClick={() => setActiveCategory(null)}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              className={`${styles.chip} ${activeCategory === cat ? styles.chipActive : ''}`}
              onClick={() => setActiveCategory(activeCategory === cat ? null : cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      <div className={styles.grid}>
        {filtered.map((toolset) => (
          <ToolsetCard
            key={toolset.name}
            toolset={toolset}
            onDeploy={setDeployTarget}
            onEdit={(t) => navigate(`/admin/agents/${encodeURIComponent(t.agent)}/toolset/${encodeURIComponent(t.name)}`)}
            onDelete={setDeleteTarget}
          />
        ))}
      </div>

      <ConfirmDialog
        open={!!deployTarget}
        title="Deploy Toolset"
        description={`Deploy "${deployTarget?.name}" to production? This will make it live immediately.`}
        confirmLabel="Deploy"
        variant="primary"
        onConfirm={handleDeploy}
        onCancel={() => setDeployTarget(null)}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Toolset"
        description={`Are you sure you want to delete "${deleteTarget?.name}"? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
