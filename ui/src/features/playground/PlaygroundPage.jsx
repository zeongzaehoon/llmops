import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '@/components/layout/PageHeader'
import Card from '@/components/layout/Card'
import Badge from '@/components/data-display/Badge'
import StatusDot from '@/components/data-display/StatusDot'
import EmptyState from '@/components/feedback/EmptyState'
import { useAgents } from '@/hooks/queries/useToolsets'
import { useAuth } from '@/hooks/useAuth'
import styles from './PlaygroundPage.module.scss'

export default function PlaygroundPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const { connect, isConnected } = useAuth()
  const { data: agents = [], isLoading } = useAgents()

  useEffect(() => {
    if (!isConnected) {
      connect('main')
    }
  }, [isConnected, connect])

  const filtered = useMemo(() => {
    if (!search.trim()) return agents
    const q = search.toLowerCase()
    return agents.filter(
      (a) =>
        a.name?.toLowerCase().includes(q) ||
        a.agent?.toLowerCase().includes(q) ||
        a.description?.toLowerCase().includes(q)
    )
  }, [agents, search])

  const handleSelect = (item) => {
    const agent = item.agent || item.name
    navigate(`/admin/playground/${encodeURIComponent(agent)}`)
  }

  return (
    <div className={styles.page}>
      <PageHeader
        title="Playground"
        description="Select an agent to start a conversation"
      />

      <div className={styles.searchBar}>
        <span className={styles.searchIcon}>&#x1F50D;</span>
        <input
          type="text"
          placeholder="Search agents..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className={styles.loadingContainer}>Loading agents...</div>
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No agents found"
          description={
            search
              ? 'Try a different search term'
              : 'No agent toolsets have been configured yet'
          }
        />
      ) : (
        <div className={styles.grid}>
          {filtered.map((item) => (
            <Card
              key={item.id || item.name}
              hoverable
              onClick={() => handleSelect(item)}
              className={styles.agentCard}
            >
              <div className={styles.cardHeader}>
                <span className={styles.cardTitle}>{item.name}</span>
                <StatusDot
                  status={item.isService ? 'live' : 'offline'}
                  label={item.isService ? 'active' : 'draft'}
                />
              </div>
              {item.description && (
                <p className={styles.cardDescription}>{item.description}</p>
              )}
              <div className={styles.cardMeta}>
                <Badge variant="info">{item.agent || 'general'}</Badge>
                {item.mcpInfo?.length > 0 && (
                  <span className={styles.toolCount}>
                    {item.mcpInfo.length} toolset{item.mcpInfo.length !== 1 ? 's' : ''}
                  </span>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
