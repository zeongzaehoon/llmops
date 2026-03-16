import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import PageHeader from '@/components/layout/PageHeader'
import Card from '@/components/layout/Card'
import Button from '@/components/inputs/Button'
import SearchInput from '@/components/inputs/SearchInput'
import EmptyState from '@/components/feedback/EmptyState'
import { useAgents, useCreateAgent } from '@/hooks/queries/useAgents'
import styles from './AgentHubPage.module.scss'

export default function AgentHubPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [showNewForm, setShowNewForm] = useState(false)
  const [newAgent, setNewAgent] = useState({ agent: '', name: '', description: '' })

  const { data: agents = [] } = useAgents()
  const createAgentMutation = useCreateAgent()

  const filtered = useMemo(() => {
    if (!search) return agents
    const q = search.toLowerCase()
    return agents.filter((a) =>
      a.agent?.toLowerCase().includes(q) ||
      a.name?.toLowerCase().includes(q) ||
      a.description?.toLowerCase().includes(q)
    )
  }, [agents, search])

  const handleCreateAgent = () => {
    const agent = newAgent.agent.trim()
    const name = newAgent.name.trim()
    if (!agent || !name) {
      toast.error('Agent ID and name are required')
      return
    }

    createAgentMutation.mutate(
      { agent, name, description: newAgent.description.trim() || undefined },
      {
        onSuccess: () => {
          toast.success(`Agent "${agent}" created`)
          setShowNewForm(false)
          setNewAgent({ agent: '', name: '', description: '' })
          navigate(`/admin/agents/${encodeURIComponent(agent)}`)
        },
        onError: (err) => {
          const msg = err?.response?.data?.message || 'Failed to create agent'
          toast.error(msg)
        },
      },
    )
  }

  return (
    <div className={styles.page}>
      <PageHeader
        title="Agents"
        description="Each agent combines a model, prompt, and toolset"
        actions={
          <Button size="sm" onClick={() => setShowNewForm(true)}>
            + New Agent
          </Button>
        }
      />

      {/* New agent form */}
      {showNewForm && (
        <div className={styles.newForm}>
          <div className={styles.newFields}>
            <label className={styles.newField}>
              <span className={styles.newLabel}>ID</span>
              <input
                type="text"
                className={styles.newInput}
                placeholder="e.g. main, cs, analyzer"
                value={newAgent.agent}
                onChange={(e) => setNewAgent((p) => ({ ...p, agent: e.target.value }))}
                autoFocus
              />
            </label>
            <label className={styles.newField}>
              <span className={styles.newLabel}>Name</span>
              <input
                type="text"
                className={styles.newInput}
                placeholder="Display name"
                value={newAgent.name}
                onChange={(e) => setNewAgent((p) => ({ ...p, name: e.target.value }))}
              />
            </label>
            <label className={styles.newField}>
              <span className={styles.newLabel}>Description</span>
              <input
                type="text"
                className={styles.newInput}
                placeholder="Optional"
                value={newAgent.description}
                onChange={(e) => setNewAgent((p) => ({ ...p, description: e.target.value }))}
                onKeyDown={(e) => e.key === 'Enter' && handleCreateAgent()}
              />
            </label>
          </div>
          <div className={styles.newActions}>
            <Button size="sm" onClick={handleCreateAgent} loading={createAgentMutation.isPending} disabled={!newAgent.agent.trim() || !newAgent.name.trim()}>
              Create
            </Button>
            <Button size="sm" variant="secondary" onClick={() => { setShowNewForm(false); setNewAgent({ agent: '', name: '', description: '' }) }}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      <div className={styles.toolbar}>
        <SearchInput placeholder="Search agents..." value={search} onChange={setSearch} />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title={agents.length === 0 ? 'No agents yet' : 'No agents found'}
          description={
            agents.length === 0
              ? 'Create your first agent to get started'
              : 'Try a different search term'
          }
          action={agents.length === 0 ? {
            label: '+ New Agent',
            onClick: () => setShowNewForm(true),
          } : undefined}
        />
      ) : (
        <div className={styles.grid}>
          {filtered.map((a) => (
            <Card
              key={a.id}
              hoverable
              className={styles.card}
              onClick={() => navigate(`/admin/agents/${encodeURIComponent(a.agent)}`)}
            >
              <div className={styles.cardHeader}>
                <span className={styles.agentName}>{a.agent}</span>
              </div>

              {a.description && (
                <p className={styles.cardDescription}>{a.description}</p>
              )}

              {a.regDate && (
                <div className={styles.statusGrid}>
                  <span className={styles.muted}>
                    Created {new Date(a.regDate).toLocaleDateString()}
                  </span>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
