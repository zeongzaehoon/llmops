import { useState } from 'react'
import Button from '@/components/inputs/Button'
import styles from './SearchPanel.module.scss'

const TOP_K_OPTIONS = [1, 3, 5, 10, 20]

export default function SearchPanel({ onSearch, isLoading = false }) {
  const [query, setQuery] = useState('')
  const [agent, setAgent] = useState('main')
  const [topK, setTopK] = useState(5)

  const handleSearch = () => {
    if (!query.trim()) return
    onSearch({ query: query.trim(), agent, top_k: topK })
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSearch()
    }
  }

  return (
    <div className={styles.panel}>
      <div className={styles.queryRow}>
        <textarea
          className={styles.queryInput}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter a semantic search query..."
          rows={2}
        />
      </div>
      <div className={styles.controlsRow}>
        <div className={styles.field}>
          <label className={styles.label}>Agent</label>
          <input
            type="text"
            className={styles.input}
            value={agent}
            onChange={(e) => setAgent(e.target.value)}
            placeholder="main"
          />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>Top K</label>
          <select
            className={styles.select}
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
          >
            {TOP_K_OPTIONS.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </div>
        <div className={styles.searchAction}>
          <Button
            onClick={handleSearch}
            loading={isLoading}
            disabled={!query.trim()}
          >
            Search
          </Button>
        </div>
      </div>
    </div>
  )
}
