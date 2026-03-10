import { useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import PageHeader from '@/components/layout/PageHeader'
import Button from '@/components/inputs/Button'
import { useAuth } from '@/hooks/useAuth'
import { useServers } from '@/hooks/queries/useServers'
import { useToolsets } from '@/hooks/queries/useToolsets'
import { useGraphs } from '@/hooks/queries/useGraphs'
import { useDeployList } from '@/hooks/queries/usePrompts'
import StatCard from './components/StatCard'
import ServerHealth from './components/ServerHealth'
import DeployStatus from './components/DeployStatus'
import QuickStart from './components/QuickStart'
import styles from './DashboardPage.module.scss'

export default function DashboardPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { isConnected, connect } = useAuth()

  // Auto-connect on mount
  useEffect(() => {
    connect('main')
  }, [connect])

  // Data queries
  const { data: servers = [], isLoading: serversLoading } = useServers()
  const { data: toolsets = [], isLoading: toolsetsLoading } = useToolsets()
  const { data: graphs = [], isLoading: graphsLoading } = useGraphs()
  const { data: deployList = [], isLoading: deploysLoading } = useDeployList()

  const isLoading = serversLoading || toolsetsLoading || graphsLoading || deploysLoading

  // Refresh all queries
  const handleRefresh = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['servers'] })
    queryClient.invalidateQueries({ queryKey: ['toolsets'] })
    queryClient.invalidateQueries({ queryKey: ['graphs'] })
    queryClient.invalidateQueries({ queryKey: ['deployList'] })
  }, [queryClient])

  // Compute stats
  const liveServers = servers.filter(
    (s) => s.status === 'live' || s.status === 'active'
  ).length
  const downServers = servers.length - liveServers

  const activeToolsets = toolsets.filter(
    (t) => t.status === 'active' || t.deployStatus === 'live'
  ).length
  const draftToolsets = toolsets.length - activeToolsets

  const totalVersions = deployList.length
  const stagedVersions = deployList.filter(
    (d) => (d.deployStatus || '').toLowerCase() === 'green' ||
           (d.deployStatus || '').toLowerCase() === 'staging' ||
           (d.deployStatus || '').toLowerCase() === 'staged'
  ).length

  return (
    <div className={styles.page}>
      <PageHeader
        title="Dashboard"
        description="Overview of your Solomon platform"
        actions={
          <Button variant="secondary" size="sm" onClick={handleRefresh} loading={isLoading}>
            Refresh
          </Button>
        }
      />

      {/* Stat cards */}
      <div className={styles.statGrid}>
        <StatCard
          icon={'\u26A1'}
          title="API Status"
          value={isConnected ? 'Healthy' : 'Connecting'}
          subtitle={isConnected ? 'All systems operational' : 'Establishing connection...'}
          color="var(--sol-status-success)"
          pulse={isConnected}
          loading={!isConnected && !servers.length}
          onClick={() => {}}
        />
        <StatCard
          icon={'\uD83D\uDDA5\uFE0F'}
          title="MCP Servers"
          value={servers.length}
          subtitle={`${liveServers} live${downServers > 0 ? ` \u00B7 ${downServers} down` : ''}`}
          color="var(--sol-brand-primary)"
          loading={serversLoading}
          onClick={() => navigate('/admin/agents')}
        />
        <StatCard
          icon={'\uD83E\uDD16'}
          title="Agents"
          value={toolsets.length}
          subtitle={`${activeToolsets} active${draftToolsets > 0 ? ` \u00B7 ${draftToolsets} draft` : ''}`}
          color="var(--sol-brand-accent)"
          loading={toolsetsLoading}
          onClick={() => navigate('/admin/agents')}
        />
        <StatCard
          icon={'\uD83D\uDCDD'}
          title="Prompts"
          value={`${totalVersions} ver.`}
          subtitle={`${stagedVersions} staged`}
          color="var(--sol-status-info)"
          loading={deploysLoading}
          onClick={() => navigate('/admin/agents')}
        />
      </div>

      {/* Main content grid */}
      <div className={styles.contentGrid}>
        <div className={styles.mainCol}>
          <ServerHealth servers={servers} loading={serversLoading} />
          <DeployStatus deployList={deployList} loading={deploysLoading} />
        </div>
        <div className={styles.sideCol}>
          <QuickStart
            hasServers={servers.length > 0}
            hasToolsets={toolsets.length > 0}
            hasPlayground={false}
          />
        </div>
      </div>
    </div>
  )
}
