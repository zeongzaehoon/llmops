import { useState, useRef, useEffect } from 'react'
import { useSSE } from '@/hooks/useSSE'
import Button from '@/components/inputs/Button'
import styles from './GraphTestPanel.module.scss'

export default function GraphTestPanel({ graphId, graphName, agents }) {
  const [question, setQuestion] = useState('')
  const [collapsed, setCollapsed] = useState(false)
  const { content, isStreaming, error, ask, abort } = useSSE()
  const resultsRef = useRef(null)

  useEffect(() => {
    if (resultsRef.current) {
      resultsRef.current.scrollTop = resultsRef.current.scrollHeight
    }
  }, [content])

  const handleRun = () => {
    if (!question.trim() || !graphId) return

    ask('main', {
      question: question.trim(),
      graph_id: graphId,
    })
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleRun()
    }
  }

  const agentNames = agents.filter((a) => a.name).map((a) => a.name)

  return (
    <div className={styles.panel}>
      <button
        type="button"
        className={styles.panelHeader}
        onClick={() => setCollapsed(!collapsed)}
      >
        <span className={styles.panelTitle}>Test Panel</span>
        <span className={`${styles.chevron} ${collapsed ? '' : styles.expanded}`}>
          &#9654;
        </span>
      </button>

      {!collapsed && (
        <div className={styles.panelBody}>
          <div className={styles.inputRow}>
            <input
              type="text"
              className={styles.questionInput}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter a question to test the graph..."
              disabled={isStreaming}
            />
            {isStreaming ? (
              <Button variant="danger" size="md" onClick={abort}>
                Stop
              </Button>
            ) : (
              <Button
                variant="primary"
                size="md"
                onClick={handleRun}
                disabled={!question.trim() || !graphId}
              >
                Run
              </Button>
            )}
          </div>

          {!graphId && (
            <p className={styles.hint}>Save the graph first to enable testing.</p>
          )}

          {(content || isStreaming || error) && (
            <div className={styles.results} ref={resultsRef}>
              {isStreaming && agentNames.length > 0 && (
                <div className={styles.agentStatus}>
                  {agentNames.map((name, i) => (
                    <span key={i} className={styles.agentTag}>
                      <span className={styles.agentDot} />
                      {name} {i === 0 ? 'thinking...' : 'waiting...'}
                    </span>
                  ))}
                </div>
              )}

              {content && (
                <div className={styles.streamContent}>
                  <span className={styles.streamLabel}>[{graphName || 'Graph'}]</span>
                  <div className={styles.streamText}>{content}</div>
                </div>
              )}

              {error && <div className={styles.errorMessage}>{error}</div>}

              {isStreaming && <span className={styles.cursor} />}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
