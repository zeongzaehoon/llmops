import { useState, useEffect, useRef, useCallback } from 'react'
import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import { getTokenSize } from '@/api/operations'
import styles from './PromptEditor.module.scss'

export default function PromptEditor({
  promptData,
  agent,
  isLatest = false,
  onSave,
  isSaving = false,
}) {
  const [prompt, setPrompt] = useState('')
  const [memo, setMemo] = useState('')
  const [tokenCount, setTokenCount] = useState(null)
  const debounceRef = useRef(null)

  useEffect(() => {
    setPrompt(promptData?.prompt || '')
    setMemo('')
    setTokenCount(null)
  }, [promptData])

  const fetchTokenCount = useCallback((text) => {
    if (!text.trim()) {
      setTokenCount(0)
      return
    }
    getTokenSize({ prompt: text })
      .then((r) => {
        const size = r.data?.res?.data
        if (size != null) setTokenCount(size)
      })
      .catch(() => {})
  }, [])

  const handlePromptChange = (e) => {
    const value = e.target.value
    setPrompt(value)

    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => fetchTokenCount(value), 300)
  }

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [])

  const handleSave = () => {
    if (!prompt.trim()) return
    onSave?.({ prompt, agent, memo })
  }

  const readOnly = !isLatest
  const deployLabel = promptData?.deployStatus === 'blue'
    ? 'Production'
    : promptData?.deployStatus === 'green'
      ? 'Staging'
      : null
  const deployVariant = promptData?.deployStatus === 'blue'
    ? 'production'
    : promptData?.deployStatus === 'green'
      ? 'staging'
      : 'info'

  return (
    <div className={styles.editor}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <h3 className={styles.title}>
            {promptData ? `Version v${promptData.version}` : 'Editor'}
          </h3>
          {deployLabel && <Badge variant={deployVariant}>{deployLabel}</Badge>}
        </div>
        {readOnly && (
          <span className={styles.readOnly}>Read-only (not latest version)</span>
        )}
      </div>

      <textarea
        className={styles.textarea}
        value={prompt}
        onChange={handlePromptChange}
        placeholder="Enter system prompt..."
        readOnly={readOnly}
        spellCheck={false}
      />

      <div className={styles.footer}>
        <div className={styles.footerLeft}>
          {tokenCount != null && (
            <span className={styles.tokenCount}>Token count: {tokenCount.toLocaleString()}</span>
          )}
        </div>

        {isLatest && (
          <div className={styles.footerRight}>
            <input
              type="text"
              className={styles.memoInput}
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              placeholder="Version memo (optional)"
            />
            <Button
              variant="primary"
              size="md"
              loading={isSaving}
              disabled={!prompt.trim()}
              onClick={handleSave}
            >
              Save as New Version
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
