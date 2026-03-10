import { useState } from 'react'
import { useParams } from 'react-router-dom'
import PageHeader from '@/components/layout/PageHeader'
import EmptyState from '@/components/feedback/EmptyState'
import CategorySelector from '@/features/prompts/components/CategorySelector'
import { useHistory } from '@/hooks/queries/useHistory'
import HistoryList from './components/HistoryList'
import HistoryDetail from './components/HistoryDetail'
import styles from './HistoryPage.module.scss'

const DEFAULT_CATEGORIES = ['main', 'cs', 'journeymapMCP', 'ranking', 'trend', 'weekly']

export default function HistoryPage() {
  const { agent: paramAgent } = useParams()
  const [agent, setAgent] = useState(paramAgent || 'main')
  const [selected, setSelected] = useState(null)

  const { data: history = [], isLoading } = useHistory(agent)

  const handleSelect = (item) => {
    setSelected(item)
  }

  const handleAgentChange = (cat) => {
    setAgent(cat)
    setSelected(null)
  }

  return (
    <div className={styles.page}>
      <PageHeader
        title="History"
        description="Browse and review conversation history"
      />

      <div className={styles.categoryBar}>
        <CategorySelector
          categories={DEFAULT_CATEGORIES}
          active={agent}
          onSelect={handleAgentChange}
        />
      </div>

      {isLoading ? (
        <div className={styles.loading}>Loading history...</div>
      ) : history.length === 0 ? (
        <EmptyState
          title="No conversations"
          description={`No chat history found for "${agent}"`}
        />
      ) : (
        <div className={styles.layout}>
          <div className={styles.listPanel}>
            <HistoryList
              items={history}
              selectedId={selected?._id || selected?.ask_id}
              onSelect={handleSelect}
            />
          </div>
          <div className={styles.detailPanel}>
            <HistoryDetail conversation={selected} />
          </div>
        </div>
      )}
    </div>
  )
}
