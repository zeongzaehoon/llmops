import { useState, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import PageHeader from '@/components/layout/PageHeader'
import Tabs from '@/components/navigation/Tabs'
import Button from '@/components/inputs/Button'
import { useToolsetsByAgent } from '@/hooks/queries/useToolsets'
import ModelTab from './components/ModelTab'
import PromptTab from './components/PromptTab'
import ToolsetTab from './components/ToolsetTab'
import styles from './AgentDetailPage.module.scss'

const TAB_KEYS = { MODEL: 'model', PROMPT: 'prompt', TOOLSET: 'toolset' }

export default function AgentDetailPage() {
  const { agent } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(TAB_KEYS.MODEL)

  // Toolset count for the tab badge. Shares react-query cache with ToolsetTab,
  // so this does not cause a second network request.
  const { data: agentToolsets = [] } = useToolsetsByAgent(agent)

  const tabItems = useMemo(
    () => [
      { key: TAB_KEYS.MODEL, label: 'Model' },
      { key: TAB_KEYS.PROMPT, label: 'Prompt' },
      { key: TAB_KEYS.TOOLSET, label: 'Toolset', count: agentToolsets.length }
    ],
    [agentToolsets.length]
  )

  return (
    <div className={styles.page}>
      <PageHeader
        title={agent}
        description="Model, prompt, and toolset configuration"
        actions={
          <Button variant="secondary" size="sm" onClick={() => navigate('/admin/agents')}>
            Back
          </Button>
        }
      />

      <div className={styles.tabBar}>
        <Tabs items={tabItems} activeKey={activeTab} onChange={setActiveTab} />
      </div>

      <div className={styles.content}>
        {activeTab === TAB_KEYS.MODEL && <ModelTab agent={agent} />}
        {activeTab === TAB_KEYS.PROMPT && <PromptTab agent={agent} />}
        {activeTab === TAB_KEYS.TOOLSET && <ToolsetTab agent={agent} />}
      </div>
    </div>
  )
}
